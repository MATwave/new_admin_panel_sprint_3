import datetime
import itertools
import sqlite3
from contextlib import contextmanager
from logging import Logger

from dacite import from_dict

from saver import PostgresSaver


@contextmanager
def conn_context(db_path: str):
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.OperationalError:
        conn = sqlite3.connect('db.sqlite')
    
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


class SQLiteLoader:
    '''
    Класс загружчика содержимого таблиц SQLite."""
    '''

    rename_dict = {'created_at': 'created_at as created',
                   'updated_at': 'updated_at as modified',
                   }

    def __init__(self, sqlite_conn: sqlite3.Connection):
        self.connection = sqlite_conn
        self.cursor = self.connection.cursor()

    def return_field_names(self, table: str) -> str:
        '''
        возвращает список стобцов в таблице с переименованием различающихся в базах на основе словаря rename_dict
        '''
        request = self.cursor.execute(f"SELECT * FROM {table};")
        fields = [_[0] for _ in request.description]
        # переименовываем столбцы
        renamed_fields = [self.rename_dict[field] if field in self.rename_dict else field for field in fields]
        field_names = ", ".join(renamed_fields)
        return field_names

    def load_movies(self, logger: Logger, models: dict, postgres_saver: PostgresSaver, page_size: int) -> None:
        '''
        запоминает все таблицы из SQLite в пачки dataclass'ов размером page_size и грузит в PostgreSQL
        '''
        request = 'SELECT name FROM sqlite_schema WHERE type=\'table\' ORDER BY name'
        list_of_table = list(itertools.chain(*self.cursor.execute(request).fetchall()))

        start = datetime.datetime.now()

        data_dict = {}
        for table in list_of_table:
            logger.info(f'загрузка даннных из таблицы {table}')

            field_names = self.return_field_names(table)
            self.cursor.execute(f'SELECT {field_names} FROM {table}')
            data_list = []

            while True:
                data_fetch = self.cursor.fetchmany(page_size)
                if not data_fetch:
                    break
                else:
                    for fetch in data_fetch:
                        data_list.append(from_dict(data_class=models[table], data=fetch))
                    logger.info(f'скачали из SQLite таблицы [{table}] {len(data_fetch)} строк')

                    data_dict.update({table: data_list})
                    postgres_saver.save_all_data(data_dict, page_size)
                    logger.info(f'загрузили в PostgreSQL таблицу [{table}] {len(data_fetch)} строк')

        logger.info('Подгрузили все данные из SQLite в PostgreSQL за ' + str(datetime.datetime.now() - start))
