import datetime
from typing import Iterator

from utils.connection_util import postgres_connection


class Extractor:
    '''класс для извлечения данных из PostgreSQL'''

    def __init__(self, psql_dsn, chunk_size: int, storage_state, logger) -> None:
        self.chunk_size = chunk_size
        self.state = storage_state
        self.dsn = psql_dsn
        self.logger = logger

    def extract(self,
                extract_timestamp: datetime.datetime,
                start_timestamp: datetime.datetime,
                exclude_ids: list) -> Iterator:
        """
        Метод чтения данных пачками.
        Ищем строки, удовлетворяющие условию - при нахождении записываем в хранилище состояния idшники
        """
        
        with postgres_connection(self.dsn) as pg_conn, pg_conn.cursor() as cursor:
            sql = f"""
                    SELECT 
                        fw.id,
                        fw.rating as imdb_rating, 
                        json_agg(DISTINCT g.name) as genre,
                        fw.title,
                        fw.description,
                        string_agg(DISTINCT CASE WHEN pfw.role = 'director' THEN p.full_name ELSE '' END, ',') AS director,
                        array_remove(COALESCE(array_agg(DISTINCT CASE WHEN pfw.role = 'actor' THEN p.full_name END) FILTER (WHERE p.full_name IS NOT NULL)), NULL) AS actors_names,
                        array_remove(COALESCE(array_agg(DISTINCT CASE WHEN pfw.role = 'writer' THEN p.full_name END) FILTER (WHERE p.full_name IS NOT NULL)), NULL) AS writers_names,
                        concat('[', string_agg(DISTINCT CASE WHEN pfw.role = 'actor' THEN json_build_object('id', p.id, 'name', p.full_name) #>> '{{}}' END, ','), ']') AS actors,
                        concat('[', string_agg(DISTINCT CASE WHEN pfw.role = 'writer' THEN json_build_object('id', p.id, 'name', p.full_name) #>> '{{}}' END, ','), ']') AS writers,
                        GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) AS last_modified
                    FROM 
                        content.film_work as fw
                        LEFT JOIN content.genre_film_work gfm ON fw.id = gfm.film_work_id
                        LEFT JOIN content.genre g ON gfm.genre_id = g.id
                        LEFT JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
                        LEFT JOIN content.person p ON pfw.person_id = p.id
                    GROUP BY fw.id
                    """

            # если переданный аргумент exclude_ids не пустой
            if exclude_ids:
                # добавляем условие
                sql += f"""
                AND (fw.id not in {tuple(exclude_ids)} OR 
                  GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) > '{str(start_timestamp)}')
                """
            sql += f"""
            HAVING GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) > '{str(extract_timestamp)}'
            ORDER BY GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) DESC;
            """
            # подключившись к PostgreSQL формируем запрос
            cursor.execute(sql)

            while True:
                # получаем строки, удовлетворяющие запросу размером chunk_size
                rows = cursor.fetchmany(self.chunk_size)
                # если таких строк нет - выходим
                if not rows:
                    self.logger.info('изменений не найдено')
                    break
                # если строки есть - фиксируем в хранилище состояния
                self.logger.info(f'извлечено {len(rows)} строк')
                for data in rows:
                    ids_list = self.state.get_state("filmwork_ids")
                    ids_list.append(data['id'])
                    self.state.set_state("filmwork_ids", ids_list)
                yield rows
