import time
from utils.env_utild import return_dsn
import datetime
from utils.logger_util import get_logger
from storage import (State, JsonFileStorage)
from ETL_classes.extractor import Extractor
from ETL_classes.transformer import Transformer
from ETL_classes.loader import Loader


def etl(logger, extracrot, transformer, state):
    '''
    Extract-Transform-Load процесс перекачки данных из PostgreSQL в Elasticsearch
    '''

    last_sync_timestamp = state.get_state('last_sync_timestamp')
    start_timestamp = datetime.datetime.now()
    filmwork_ids = state.get_state('filmwork_ids')

    for extracted_part in extracrot.extract(last_sync_timestamp, start_timestamp, filmwork_ids):
        data = transformer.transform(extracted_part)
        loader.load(data)
    state.set_state("filmwork_ids", [])
    state.set_state("last_sync_timestamp", str(start_timestamp))


if __name__ == '__main__':
    dsn = return_dsn()
    logger = get_logger(__name__)

    state = State(JsonFileStorage(file_path='state.json'))
    extracrot = Extractor(psql_dsn=dsn['psql'], chunk_size=50, storage_state=state)
    transformer = Transformer()
    loader = Loader(dsn['es'], logger)
    while True:
        etl(logger, extracrot, transformer, state)
        time.sleep(60)
