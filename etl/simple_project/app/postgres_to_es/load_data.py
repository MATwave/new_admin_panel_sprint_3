import time
from utils.env_utild import return_dsl
from utils.connection_util import (postgres_connection, elastic_search_connection)

from utils.logger_util import get_logger


def etl(logger, dsn) -> None:

    with (postgres_connection(dsn['psql']) as pg_conn,
          elastic_search_connection(dsn['es']) as es_client):

        logger.info('успешно подключились')


if __name__ == '__main__':
    dsn = return_dsl()
    logger = get_logger(__name__)
    while True:
        etl(logger, dsn)
        time.sleep(60)
