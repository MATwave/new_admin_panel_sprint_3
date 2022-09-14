import os
from logging import Logger

import dotenv
import psycopg2
from psycopg2.extras import DictCursor

from loader import SQLiteLoader, conn_context, sqlite3
from models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork
from saver import PostgresSaver, _connection
from utils import get_logger

PAGE_SIZE = 500

models = {'film_work': FilmWork,
          'genre': Genre,
          'genre_film_work': GenreFilmWork,
          'person': Person,
          'person_film_work': PersonFilmWork
          }


def return_dsl() -> dict:
    '''
    Возвращает словарь DSN (Data Source Name) для подключения к БД
    '''
    dotenv.load_dotenv()
    dsn = {'psql': {'dbname': os.environ.get('psql_DB_NAME'),
                    'user': os.environ.get('psql_DB_USER'),
                    'password': os.environ.get('psql_DB_PASSWORD'),
                    'host': os.environ.get('psql_DB_HOST'),
                    'port': os.environ.get('psql_DB_PORT')},

           'sqlite': {'db_path': os.environ.get('sqlite_DB_NAME')}
           }
    return dsn


def load_from_sqlite(logger: Logger, sqlite_conn: sqlite3.Connection, pg_conn: _connection):
    """
    Основной метод загрузки данных из SQLite в Postgres
    Args:
        logger: логгер
        sqlite_conn: подключение к базе данных SQLite.
        pg_conn: подключение к базе данных PostgreSQL.
    """

    sqlite_loader = SQLiteLoader(sqlite_conn)
    postgres_saver = PostgresSaver(pg_conn)

    sqlite_loader.load_movies(logger, models, postgres_saver, PAGE_SIZE)


if __name__ == '__main__':
    logger = get_logger(__name__)

    try:
        dsn = return_dsl()
        with (conn_context(**dsn['sqlite']) as sqlite_conn,
              psycopg2.connect(**dsn['psql'], cursor_factory=DictCursor) as pg_conn):
            logger.info('подключились к базе')
            load_from_sqlite(logger, sqlite_conn, pg_conn)
    except KeyboardInterrupt as e:
        logger.warning(str(type(e)) + ' программа прервана пользователем')
        pg_conn.close()
    except Exception as e: # фиксируем в лог все исключения, которые могу возникнуть
        logger.warning(str(type(e)) + ' ' + str(e))
    except SystemExit as e:
        logger.warning(str(type(e)) + ' ' + str(e))
        pg_conn.close()
    except GeneratorExit as e:
        logger.warning(str(type(e)) + ' ' + str(e))
        pg_conn.close()
