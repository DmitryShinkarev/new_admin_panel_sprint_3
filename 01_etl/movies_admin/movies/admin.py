from django.contrib import admin
from django.utils.translation import gettext_lazy as _


from .models import Genre, Film_work, GenreFilmwork, Person, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork

    # Отображение полей в списке
    list_display = ('name')

    # Фильтрация в списке
    list_filter = ('name',)

    # Поиск по полям
    search_fields = ('name', 'description', 'id')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork

    # Отображение полей в списке
    list_display = ('name')

    # Фильтрация в списке
    list_filter = ('name',)

    # Поиск по полям
    search_fields = ('name', 'role', 'id')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(Film_work)
class FilmworkAdmin(admin.ModelAdmin):
    
    list_display = ('title', 'type', 'creation_date',
                    'rating', 'get_genres', 'get_persons',)
    list_filter = ('type',)
    search_fields = ('title', 'description', 'id',)
    
    inlines = (GenreFilmworkInline, PersonFilmworkInline)
    list_prefetch_related = ('persons', 'genres')

    def item_count(self, obj):
        return obj.items.count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(*self.list_prefetch_related)

    def get_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])

    def get_persons(self, obj):
        return ', '.join([person.full_name for person in obj.persons.all()])

    get_genres.short_description = _('Genres')
    get_persons.short_description = _('Persons')
