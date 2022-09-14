from django.db import models
from django.utils.translation import gettext_lazy as _
from .mixins import UUIDMixin, ModifiedMixin, CreatedMixin


class Person(UUIDMixin, ModifiedMixin, CreatedMixin):
    '''
        Модель, описывающая таблицу Person, хранящую участников кинопроизведений: актёр, продюсер или режиссёр.
    '''

    class Gender(models.TextChoices):
        MALE = 'male', _('male')
        FEMALE = 'female', _('female')

    full_name = models.TextField(_('full_name'))
    gender = models.TextField(_('gender'), choices=Gender.choices, null=True)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = "content\".\"person"

        verbose_name = _('verbose_name_person')
        verbose_name_plural = _('verbose_name_plural_person')

        indexes = [
            models.Index(fields=['full_name'], name='person_full_name_idx')
        ]
