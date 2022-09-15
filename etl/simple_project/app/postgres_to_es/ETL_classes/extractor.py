import datetime

from etl.simple_project.app.postgres_to_es.utils.backoff_util import backoff
from etl.simple_project.app.postgres_to_es.utils.connection_util import postgres_connection


class Extractor:
    '''класс для извлечения данных из PostgreSQL'''

    def __init__(self, psql_dsn, chunk_size: int, storage_state) -> None:
        self.chunk_size = chunk_size
        self.state = storage_state
        self.dsn = psql_dsn

    @backoff()
    def extract(self, extract_timestamp: datetime.datetime, start_timestamp: datetime.datetime,
                exclude_ids: list):
        """
        Метод чтения данных пачками.
        После падения чтение начинается с последней обработанной записи
        """
        print(self.dsn)
        with postgres_connection(self.dsn) as pg_conn,pg_conn.cursor() as cursor:
            print('here')
            sql = """
                    SELECT 
                        fw.id,
                        fw.rating as imdb_rating, 
                        json_agg(DISTINCT g.name) as genre,
                        fw.title,
                        fw.description,
                        string_agg(DISTINCT CASE WHEN pfw.role = 'director' THEN p.full_name ELSE '' END, ',') AS director,
                        array_remove(COALESCE(array_agg(DISTINCT CASE WHEN pfw.role = 'actor' THEN p.full_name END) FILTER (WHERE p.full_name IS NOT NULL)), NULL) AS actors_names,
                        array_remove(COALESCE(array_agg(DISTINCT CASE WHEN pfw.role = 'writer' THEN p.full_name END) FILTER (WHERE p.full_name IS NOT NULL)), NULL) AS writers_names,
                        concat('[', string_agg(DISTINCT CASE WHEN pfw.role = 'actor' THEN json_build_object('id', p.id, 'name', p.full_name) #>> '{}' END, ','), ']') AS actors,
                        concat('[', string_agg(DISTINCT CASE WHEN pfw.role = 'writer' THEN json_build_object('id', p.id, 'name', p.full_name) #>> '{}' END, ','), ']') AS writers,
                        GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) AS last_modified
                    FROM 
                        content.film_work as fw
                        LEFT JOIN content.genre_film_work gfm ON fw.id = gfm.film_work_id
                        LEFT JOIN content.genre g ON gfm.genre_id = g.id
                        LEFT JOIN content.person_film_work pfw ON fw.id = pfw.film_work_id
                        LEFT JOIN content.person p ON pfw.person_id = p.id
                    GROUP BY fw.id
                    HAVING GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) > %(extract_timestamp)s
                    """

            if exclude_ids:
                sql += """
                AND (fw.id not in %(exclude_ids)s OR 
                  GREATEST(MAX(fw.modified), MAX(g.modified), MAX(p.modified)) > %(start_timestamp)s)
                """
            sql += """
            ORDER BY last_modified DESC;
            """
            cursor.execute(sql, {'exclude_ids': tuple(exclude_ids),
                                         'extract_timestamp': extract_timestamp,
                                         'start_timestamp': start_timestamp
                                         }
                                   )

            while True:
                rows = cursor.fetchmany(self.chunk_size)
                if not rows:
                    break
                for data in rows:
                    ids_list = self.state.get_state("filmwork_ids")
                    ids_list.append(data['id'])
                    self.state.set_state("filmwork_ids", ids_list)
                yield rows
