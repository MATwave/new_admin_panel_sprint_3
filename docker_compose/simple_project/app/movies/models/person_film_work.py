from django.db import models
from django.utils.translation import gettext_lazy as _
from .mixins import UUIDMixin, CreatedMixin


class Roles(models.TextChoices):
    DIRECTOR = 'director', _('director')
    WRITER = 'writer', _('writer')
    ACTOR = 'actor', _('actor')
    UNDEFINED = 'undefined', _('undefined')


class PersonFilmwork(UUIDMixin, CreatedMixin):
    '''
    Авторы и кинопроизведения относятся друг к другу как «многие ко многим».
    У фильма может быть несколько авторов, а один автор может создать множество фильмов.
    Модель описывает промежуточную таблица person_film_work с дополнительным полем created
    '''
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.CharField(_('role'),
                            max_length=50,
                            choices=Roles.choices,
                            default=Roles.UNDEFINED)

    class Meta:
        db_table = "content\".\"person_film_work"

        verbose_name = _('filmwork person')
        verbose_name_plural = _('filmwork people')
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'],
                                    name='film_work_person_role_uniq')
        ]
        indexes = [
            models.Index(fields=['film_work', 'person', 'role'],
                         name='film_work_person_role_idx')
        ]
