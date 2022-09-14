from dataclasses import dataclass
from typing import Optional


@dataclass
class FilmWork:
    id: str
    title: str
    type: str
    created: str
    modified: str
    creation_date: Optional[str] = None
    file_path: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None


@dataclass
class Genre:
    id: str
    name: str
    created: str
    modified: str
    description: Optional[str] = None


@dataclass
class Person:
    id: str
    full_name: str
    created: str
    modified: str


@dataclass
class GenreFilmWork:
    id: str
    genre_id: str
    film_work_id: str
    created: str


@dataclass
class PersonFilmWork:
    id: str
    film_work_id: str
    person_id: str
    role: str
    created: str
