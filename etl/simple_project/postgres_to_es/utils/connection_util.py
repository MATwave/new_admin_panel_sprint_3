from contextlib import contextmanager

import psycopg2
from elasticsearch import Elasticsearch
from psycopg2.extras import RealDictCursor


@contextmanager
def elastic_search_connection(dsn: dict):
    """Создает подключение к ElasticSearch, которое закроет на выходе.

    Args:
        dsl: словарь с DSN (Data Source Name) для подключения к ElasticSearch

    Yields:
        Подключение к ElasticSearch.
    """
    es_connection = Elasticsearch(dsn['host'])
    try:
        yield es_connection
    finally:
        es_connection.close()


@contextmanager
def postgres_connection(dsn: dict):
    """
    Создает подключение к PostgreSQL, которое закроет на выходе.

    Args:
        dsl: словарь с DSN (Data Source Name) для подключения к БД Postgres

    Yields:
        Подключение к PostgreSQL.
    """
    connection = psycopg2.connect(**dsn, cursor_factory=RealDictCursor)
    connection.set_session(autocommit=True)
    try:
        yield connection
    finally:
        connection.close()
