import os
import sqlite3
from contextlib import contextmanager
from dataclasses import fields

import dotenv
import psycopg2
from psycopg2.extras import DictCursor
from sqlite_to_postgres.models import (FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork)

models = {'film_work': FilmWork,
          'genre': Genre,
          'genre_film_work': GenreFilmWork,
          'person': Person,
          'person_film_work': PersonFilmWork
          }


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def return_dsl() -> dict:
    '''
    Возвращает словарь DSN (Data Source Name) для подключения к БД
    '''
    dotenv.load_dotenv(dotenv.find_dotenv())
    dsn = {'psql': {'dbname': os.environ.get('psql_DB_NAME'),
                    'user': os.environ.get('psql_DB_USER'),
                    'password': os.environ.get('psql_DB_PASSWORD'),
                    'host': os.environ.get('psql_DB_HOST'),
                    'port': os.environ.get('psql_DB_PORT')},

           'sqlite': {'db_path': os.environ.get('sqlite_DB_NAME')}
           }
    return dsn


dsn = return_dsl()


def test_integrity():
    """Проверка соответствия количества записей в таблицах БД."""

    with (conn_context(**dsn['sqlite']) as sqlite_conn,
          psycopg2.connect(**dsn['psql'], cursor_factory=DictCursor) as pg_conn):
        for table in models:
            curs = sqlite_conn.cursor()
            sqlite_rows_count = curs.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]

            cursor = pg_conn.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM content.{table};')
            psql_rows_count = cursor.fetchone()[0]

            assert sqlite_rows_count == psql_rows_count, \
                (f'Количество записей в таблице {table} PostgreSQL не совпадает с SQLite')


sqlite_rename_dict = {'created': 'substr(created_at,0,20)',
                      'modified': 'substr(updated_at,0,20)'}

psql_rename_dict = {'created': 'TO_CHAR(created,\'YYYY-MM-DD HH24:MI:SS\')',
                    'modified': 'TO_CHAR(modified,\'YYYY-MM-DD HH24:MI:SS\')',
                    'creation_date': 'TO_CHAR(creation_date,\'YYYY-MM-DD HH24:MI:SS\')'}


def test_contents():
    """Проверка соответствия содержимого."""
    dsn = return_dsl()
    with (conn_context(**dsn['sqlite']) as sqlite_conn,
          psycopg2.connect(**dsn['psql'], cursor_factory=DictCursor) as pg_conn):

        for table in models:
            field_names = [field.name for field in fields(models[table])]

            sqlite_renamed_fields = [sqlite_rename_dict[field] if field in sqlite_rename_dict else field for field in
                                     field_names]
            sqlite_field_names_str = ','.join(sqlite_renamed_fields)

            curs = sqlite_conn.cursor()
            sqlite_person_data = curs.execute(f"SELECT {sqlite_field_names_str} FROM {table}").fetchall()

            psql_renamed_fields = [psql_rename_dict[field] if field in psql_rename_dict else field for field in
                                   field_names]
            psql_field_names_str = ','.join(psql_renamed_fields)

            cursor = pg_conn.cursor()
            cursor.execute(f"SELECT {psql_field_names_str} FROM content.{table}")
            postgre_person_data = cursor.fetchall()

            for i in range(len(postgre_person_data)):
                assert len(set(postgre_person_data[i]) - set(tuple(sqlite_person_data[i]))) == 0, \
                    (f'Списки не идентичны в таблице {table}')


if __name__ == '__main__':
    test_integrity()
    test_contents()
