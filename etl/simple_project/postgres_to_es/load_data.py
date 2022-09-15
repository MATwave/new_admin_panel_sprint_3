import datetime
import os
import time

import elasticsearch
import psycopg2

from ETL_classes.extractor import Extractor
from ETL_classes.loader import Loader
from ETL_classes.transformer import Transformer
from etl.simple_project.postgres_to_es.utils.backoff_util import backoff
from storage import (State, JsonFileStorage)
from utils.env_utild import return_dsn
from utils.logger_util import get_logger


@backoff((elasticsearch.exceptions.ConnectionError,))
@backoff((psycopg2.OperationalError,))
def etl(logger, extracrot, transformer, state, loader):
    '''
    Extract-Transform-Load процесс перекачки данных из PostgreSQL в Elasticsearch
    '''

    last_sync_timestamp = state.get_state('last_sync_timestamp')
    logger.info(f'последняя синхронизация была {last_sync_timestamp}')
    start_timestamp = datetime.datetime.now()
    filmwork_ids = state.get_state('filmwork_ids')

    loader.create_index('movies')

    for extracted_part in extracrot.extract(last_sync_timestamp, start_timestamp, filmwork_ids):
        data = transformer.transform(extracted_part)
        loader.load(data)
    state.set_state("last_sync_timestamp", str(start_timestamp))
    state.set_state("filmwork_ids", [])


if __name__ == '__main__':
    dsn = return_dsn()
    logger = get_logger(__name__)

    state = State(JsonFileStorage(file_path='state.json'))

    chunk_size = int(os.environ.get('CHUNK_SIZE'))

    extractor = Extractor(psql_dsn=dsn['psql'], chunk_size=chunk_size, storage_state=state, logger=logger)
    transformer = Transformer()
    loader = Loader(dsn=dsn['es'], logger=logger)

    while True:
        etl(logger, extractor, transformer, state, loader)
        logger.info(f'в сон на {float(os.environ.get("ES_SLEEP"))}')
        time.sleep(float(os.environ.get('ES_SLEEP')))
