from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from movies.models import Filmwork
from movies.models.person_film_work import PersonFilmwork, Roles


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']  # Список методов, которые реализует обработчик

    @staticmethod
    def _aggregate_person(role: Roles):
        return ArrayAgg('persons__full_name',
                        filter=Q(personfilmwork__role__icontains=role),
                        distinct=True)

    def get_queryset(self):
        queryset = Filmwork.objects.prefetch_related('genres', 'person').values().all(). \
            annotate(genres=ArrayAgg('genres__name', distinct=True),
                     actors=MoviesApiMixin._aggregate_person(role=Roles.ACTOR),
                     directors=MoviesApiMixin._aggregate_person(role=Roles.DIRECTOR),
                     writers=MoviesApiMixin._aggregate_person(role=Roles.WRITER),
                     )

        return queryset

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, self.paginate_by)
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(page.object_list)
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return kwargs['object']
