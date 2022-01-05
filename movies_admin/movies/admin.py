from django.contrib import admin
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
    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    # Отображение полей в списке
    list_display = ('title', 'type', 'creation_date', 'rating',)

    # Фильтрация в списке
    list_filter = ('type',)

    # Поиск по полям
    search_fields = ('title', 'description', 'id')
