import json


class Transformer:
    def transform(self, data: dict) -> list[dict]:
        """Обработка данных из Postgres и преобразование в формат для ElasticSearch
        :param data: Словарь из Postgres
        """
        butch = []
        for row in data:
            filmwork = {
                "id": row['id'],
                "imdb_rating": row['imdb_rating'],
                "genre": row['genre'],
                "title": row['title'],
                "description": row['description'],
                "director": row['director'],
                "actors_names": row['actors_names'] if row['actors_names'] is not None else '',
                "writers_names": row['writers_names'] if row['writers_names'] is not None else '',
                "actors": json.loads(row['actors']) if row['actors'] is not None else [],
                "writers": json.loads(row['writers']) if row['writers'] is not None else []
            }
            butch.append(filmwork)
        return butch
