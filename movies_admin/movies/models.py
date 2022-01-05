import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:

        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
        
class TypeRole(models.TextChoices):
    ACTOR = "actor", _("actor")
    DIRECTOR = "director", _("director")
    WRITER = "writer", _("writer")

class TypeFilm(models.TextChoices):
    MOVIE = "movie", _("Film")
    SOPHOMORE = "tv_show", _("TV show")

class GenreFilmwork(UUIDMixin, models.Model):
    filmwork = models.ForeignKey("Film_work", on_delete=models.CASCADE)
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        constraints = [
        models.UniqueConstraint(fields=['filmwork', 'genre'], 
                                name='film_work_genre_idx')
        ]


class PersonFilmwork(UUIDMixin, models.Model):
    filmwork = models.ForeignKey("Film_work", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)

    role = models.CharField(
        _("Role"), max_length=10,
        choices=TypeRole.choices,
        default=TypeRole.ACTOR
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        constraints = [
        models.UniqueConstraint(fields=['filmwork', 'person', 'role'], 
                                name='film_work_person_idx')
        ]


class Genre(UUIDMixin, TimeStampedMixin):

    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    def __str__(self):
        return self.name

    class Meta:

        db_table = "content\".\"genre"
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")


class Person(UUIDMixin, TimeStampedMixin):

    full_name = models.CharField(_("Artist name"), max_length=255, blank=True)
    birth_date = models.DateField(_("Birth date"))

    def __str__(self):
        return self.full_name

    class Meta:

        db_table = "content\".\"person"
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")


class Film_work(UUIDMixin, TimeStampedMixin):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    creation_date = models.DateField(_("Release date"))

    rating = models.IntegerField(
        _("Rating"),
        default=0,
        blank=True,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(10.0)
        ]
    )

    type = models.CharField(
        _("Type"), max_length=10,
        choices=TypeFilm.choices,
        default=TypeFilm.MOVIE
    )

    genres = models.ManyToManyField(
        Genre,
        through="GenreFilmwork"
    )

    persons = models.ManyToManyField(
        Person,
        through="PersonFilmwork"
    )

    def __str__(self):
        return self.title

    class Meta:

        db_table = "content\".\"film_work"

        verbose_name = _("Film")
        verbose_name_plural = _("Films")
