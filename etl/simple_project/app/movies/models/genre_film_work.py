from django.db import models
from .mixins import UUIDMixin, CreatedMixin
from django.utils.translation import gettext_lazy as _


class GenreFilmwork(UUIDMixin, CreatedMixin):
    '''
    Жанры и кинопроизведения относятся друг к другу как «многие ко многим».
    Один фильм может принадлежать нескольким жанрам, а один жанр относится к множеству фильмов.
    Модель описывает промежуточную таблица genre_film_work с дополнительным полем created
    '''
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('filmwork genre')
        verbose_name_plural = _('filmwork genres')
        constraints = [models.UniqueConstraint(fields=['film_work', 'genre'],
                                               name='film_work_genre_uniq')]
        indexes = [models.Index(fields=['film_work', 'genre'],
                                name='film_work_genre_idx')]
