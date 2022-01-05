from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, F
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import Film_work


class MoviesApiMixin:
    model = Film_work
    http_method_names = ["get"]

    def get_queryset(self):

        all_movies = Film_work.objects.values(
            
        ).annotate(
            genres=ArrayAgg(
                'genres__name',
                distinct=True,
            )
        ).annotate(
            writers=ArrayAgg(
                'persons__full_name',
                distinct=True,
                filter=Q(
                    personfilmwork__role='writer'
                )
            )
        ).annotate(
            actors=ArrayAgg(
                'persons__full_name',
                distinct=True,
                filter=Q(
                    personfilmwork__role='actor'
                )
            )
        ).annotate(
            directors=ArrayAgg(
                'persons__full_name',
                distinct=True,
                filter=Q(
                    personfilmwork__role='director'
                )
            )
        )

        return all_movies.values()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):

    model = Film_work
    paginate_by = 50

    http_method_names = ["get"]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = self.get_queryset()

        paginator, page, object_list, is_paginated = self.paginate_queryset(
            context, self.paginate_by
        )
        prev = page.previous_page_number() if page.has_previous() else None
        next = page.next_page_number() if page.has_next() else None

        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": prev,
            "next": next,
            "results": list(object_list),
        }

        return context


class MovieDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, object, **kwargs):

        data = self.get_queryset().filter(id=self.kwargs['pk']).get()
        try:
            context = {
                "results": data,
            }
        except Exception as err:
            print(err)

        return context
