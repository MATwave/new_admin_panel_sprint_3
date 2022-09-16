import datetime
import logging
import os
import time

import elasticsearch
import psycopg2

from ETL_classes.extractor import Extractor
from ETL_classes.loader import Loader
from ETL_classes.transformer import Transformer
from utils.backoff_util import backoff
from storage import (State, JsonFileStorage)
from utils.env_utild import BaseConfig
from utils.logger_util import get_logger


@backoff((elasticsearch.exceptions.ConnectionError,))
@backoff((psycopg2.OperationalError,))
def etl(logger: logging.Logger, extracrot: Extractor, transformer: Transformer, state: State, loader: Loader) -> None:
    '''
    Extract-Transform-Load процесс перекачки данных из PostgreSQL в Elasticsearch
    '''

    last_sync_timestamp = state.get_state('last_sync_timestamp')
    logger.info(f'последняя синхронизация была {last_sync_timestamp}')
    start_timestamp = datetime.datetime.now()
    filmwork_ids = state.get_state('filmwork_ids')

    for extracted_part in extracrot.extract(last_sync_timestamp, start_timestamp, filmwork_ids):
        data = transformer.transform(extracted_part)
        loader.load(data)
        state.set_state("last_sync_timestamp", str(start_timestamp))
        state.set_state("filmwork_ids", [])


if __name__ == '__main__':
    configs = BaseConfig()
    logger = get_logger(__name__)

    state = State(JsonFileStorage(file_path='state.json'))

    extractor = Extractor(psql_dsn=configs.dsn, chunk_size=configs.chunk_size, storage_state=state, logger=logger)
    transformer = Transformer()
    loader = Loader(dsn=configs.es_base_url, logger=logger)

    while True:
        etl(logger, extractor, transformer, state, loader)
        logger.info(f'в сон на {configs.sleep_time}')
        time.sleep(configs.sleep_time)
