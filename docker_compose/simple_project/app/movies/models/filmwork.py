from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from .mixins import UUIDMixin, ModifiedMixin, CreatedMixin


class Filmwork(UUIDMixin, ModifiedMixin, CreatedMixin):
    '''
    Модель, описывающая таблицу Filmwork, хранящую основную информацию о кинопроизведении:
    название, описание, дата создания, рейтинг и тип — фильм, сериал, мультфильм и т.п.
    '''

    class FilmTypes(models.TextChoices):
        movie = 'movie', _('movie')
        tv_show = 'tv_show', _('tv_show')
        cartoon = 'cartoon', _('cartoon')
        series = 'series', _('series')

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation_date'))
    rating = models.FloatField(_('rating'), blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    type = models.TextField(_('type'), choices=FilmTypes.choices)

    certificate = models.CharField(_('certificate'), max_length=512, blank=True, null=True)
    file_path = models.FileField(_('file'), blank=True, null=True, upload_to='movies/')

    genres = models.ManyToManyField('Genre', through='GenreFilmwork')
    persons = models.ManyToManyField('Person', through='PersonFilmwork')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content\".\"film_work"

        verbose_name = _('verbose_name_filmwork')
        verbose_name_plural = _('verbose_name_plural_filmwork')
        indexes = [models.Index(fields=['creation_date'],
                                name='film_work_creation_date_idx'),
                   models.Index(fields=['title'],
                                name='film_work_title_idx')]
