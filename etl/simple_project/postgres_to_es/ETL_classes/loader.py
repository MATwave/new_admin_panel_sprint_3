import json

import elasticsearch.exceptions
from elasticsearch import helpers,ConnectionError

from utils.connection_util import elastic_search_connection
from utils.backoff_util import backoff

class Loader:
    def __init__(self, dsn, logger) -> None:
        self.dsn = dsn
        self.logger = logger
        # при первичной инициализации класса Loader создадим (если нет) индекс movies в ElasticSearch
        self.create_index('movies')

    @backoff((ConnectionError,))
    def create_index(self, index_name: str) -> None:
        """Создание ES индекса.
           :param index_name: Наименование индекса.
           :param mapping: Настройки индекса
        """
        settings = {
            "refresh_interval": "1s",
            "analysis": {
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_"
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english"
                    },
                    "english_possessive_stemmer": {
                        "type": "stemmer",
                        "language": "possessive_english"
                    },
                    "russian_stop": {
                        "type": "stop",
                        "stopwords": "_russian_"
                    },
                    "russian_stemmer": {
                        "type": "stemmer",
                        "language": "russian"
                    }
                },
                "analyzer": {
                    "ru_en": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "english_stop",
                            "english_stemmer",
                            "english_possessive_stemmer",
                            "russian_stop",
                            "russian_stemmer"
                        ]
                    }
                }
            }
        }

        mappings = {
            "dynamic": "strict",
            "properties": {
                "id": {
                    "type": "keyword"
                },
                "imdb_rating": {
                    "type": "float"
                },
                "genre": {
                    "type": "keyword"
                },
                "title": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                    }
                },
                "description": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "director": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "actors_names": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "writers_names": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "actors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "id": {
                            "type": "keyword"
                        },
                        "name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "writers": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "id": {
                            "type": "keyword"
                        },
                        "name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                }
            },
        }

        # подключившись к ES
        with elastic_search_connection(self.dsn) as es:
            if not es.ping():
                raise elasticsearch.exceptions.ConnectionError
            # если нет индекса
            if not es.indices.exists(index='movies'):
                # создаем индекс movies
                es.indices.create(index=index_name, settings=settings, mappings=mappings)
                self.logger.info(f"Создание индекса {index_name} со следующими схемами:"
                                 f"{json.dumps(settings, indent=2)} и {json.dumps(mappings, indent=2)} ")

    def load(self, data: list[dict]) -> None:
        """Загружаем данные пачками в ElasticSearch
        :param data: Преобразованные словари для вставки в ElasticSearch
        """
        actions = [{'_index': 'movies', '_id': row['id'], '_source': row, } for row in data]
        # подключившись к ElasticSearch
        with elastic_search_connection(self.dsn) as es:
            # используя встроенные методы библиотеки elasticsearch грузим данные в ElasticSearch
            helpers.bulk(es, actions)
            self.logger.info(f'загружено {len(data)} строк')
