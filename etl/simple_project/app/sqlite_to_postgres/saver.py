from dataclasses import astuple, fields

from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_batch


class PostgresSaver:
    '''
        Класс приемника содержимого таблиц SQLite в PostgreSQL"""
    '''

    def __init__(self, connection: _connection):
        self.connection = connection

    def save_all_data(self, data: dict, page_size: int):
        '''
        сохраняет всю собранную из SQLite информацию в соответствующие таблицы PostgreSQL
        '''
        for table in data:
            field_names = [field.name for field in fields(data[table][0])]
            field_names_str = ','.join(field_names)
            values_s = ','.join(['%s'] * len(field_names))

            with self.connection.cursor() as cursor:
                cursor.execute(f'TRUNCATE content.{table} CASCADE; ')
                query = f"""INSERT INTO content.{table} ({field_names_str})
                            VALUES ({values_s})
                            ON CONFLICT do nothing"""

                tuple_list = [astuple(model) for model in data[table]]

                execute_batch(cursor, query, tuple_list, page_size=page_size)

                self.connection.commit()
