from django.db import models
from django.utils.translation import gettext_lazy as _
from .mixins import UUIDMixin, ModifiedMixin, CreatedMixin


class Genre(UUIDMixin, ModifiedMixin, CreatedMixin):
    '''
    Модель, описывающая таблицу Genre, хранящую жанры кинопроизведений: драма, боевик, ужасы, мелодрама и т.п.
    '''
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content\".\"genre"  # явное указание на нестандартную схему
        verbose_name = _('verbose_name_genre')
        verbose_name_plural = _('verbose_name_plural_genre')
