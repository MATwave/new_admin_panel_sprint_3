import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class ModifiedMixin(models.Model):
    '''
    Миксин содержащий набор атрибутов и методов, который может быть полезен другим классам.
    Данный миксин позволяет вынести общие столбцы таблиц (modified) во вне.
    '''
    modified = models.DateTimeField(_("modified"), auto_now=True)

    class Meta:
        abstract = True  # класс не является представлением таблицы


class CreatedMixin(models.Model):
    '''
    Миксин содержащий набор атрибутов и методов, который может быть полезен другим классам.
    Данный миксин позволяет вынести общие столбцы таблиц (created) во вне.
    '''
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        abstract = True  # класс не является представлением таблицы


class UUIDMixin(models.Model):
    '''
    Миксин содержащий набор атрибутов и методов, который может быть полезен другим классам.
    Данный миксин позволяет вынести общие столбцы таблиц (id) во вне.
    Миксин объединен по признаку UUID
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
