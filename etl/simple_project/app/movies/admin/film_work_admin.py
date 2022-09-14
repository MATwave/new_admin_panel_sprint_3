from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models.filmwork import Filmwork
from ..models.genre_film_work import GenreFilmwork
from ..models.person_film_work import PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    autocomplete_fields = ('genre',)


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ('person',)


class RatingListFilter(admin.SimpleListFilter):
    title = _('rating')

    parameter_name = 'rating'

    def lookups(self, request, model_admin):
        return ((str(k), f'{k}-{k + 1}') for k in range(10))

    def queryset(self, request, queryset):
        if self.value():
            rate = int(self.value())
            return queryset.filter(rating__gte=rate, rating__lte=rate + 1)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)
    list_display = ('title', 'get_genres', 'get_persons', 'type', 'creation_date', 'rating',)
    list_filter = ('type', RatingListFilter,)
    list_prefetch_related = ('genres', 'persons')
    search_fields = ('title', 'description', 'id',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related(*self.list_prefetch_related)
        return queryset

    def get_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])

    def get_persons(self, film):
        return ', '.join([person.full_name for person in film.persons.all()])

    get_persons.short_description = _('persons')

    get_genres.short_description = _('genres')
