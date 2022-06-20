import typing
import uuid
from dataclasses import dataclass


@dataclass()
class ETLPerson:
    __slots__ = ("id", "full_name", "role", "film_ids")

    id: uuid.UUID
    full_name: str
    role: str
    film_ids: typing.List[uuid.UUID]

    @classmethod
    def from_dict_cls(cls, dict_: typing.Dict[str, typing.Any]):
        if dict_:
            return cls(id=dict_["id"]
                       , full_name=dict_["full_name"]
                       , role=dict_["role"]
                       , film_ids=dict_["film_ids"][1:-1].split(","))
        return ""


@dataclass()
class ETLGenre:
    __slots__ = ("id", "name", "description")

    id: uuid.UUID
    name: str
    description: str

    @classmethod
    def from_dict_cls(cls, dict_: typing.Dict[str, typing.Any]):
        if dict_:
            return cls(id=dict_["id"]
                       , name=dict_["name"]
                       , description=dict_["description"])
        return ""

    @classmethod
    def dict_to_list(cls, iterable: typing.Iterable[dict]):
        if iterable:
            return [cls.from_dict_cls(it) for it in iterable]
        return []

@dataclass()
class ETLPersonMovie:
    __slots__ = ("id", "name")

    id: uuid.UUID
    name: str

    @classmethod
    def from_dict_cls(cls, dict_: typing.Dict[str, typing.Any]):
        if dict_:
            return cls(id=dict_["id"]
                       , name=dict_["name"])
        return ""

    @classmethod
    def dict_to_list_cls(cls, iterable: typing.Iterable[dict]):
        if iterable:
            return [cls.from_dict_cls(it) for it in iterable]
        return None

    @staticmethod
    def dict_to_list(iterable: typing.Iterable[dict]):
        if iterable:
            return list(map(str, iterable))
        return None

@dataclass()
class ETLMovie:
    __slots__ = (
        "id",
        "title",
        "description",
        "imdb_rating",
        "genre",
        "writers_names",
        "actors_names",
        "director",
        "writers",
        "actors",
        "directors",
    )

    id: uuid.UUID
    title: str
    description: str
    imdb_rating: float
    genre: typing.List[str]
    writers_names: typing.List[str]
    actors_names: typing.List[str]
    director: typing.List[str]
    writers: typing.List["ETLPersonMovie"]
    actors: typing.List["ETLPersonMovie"]
    directors: typing.List["ETLPersonMovie"]

    @classmethod
    def from_dict_cls(cls, dict_: typing.Dict[str, typing.Any]) -> "ETLMovie":
        return cls(
            id=dict_["id"],
            title=str(dict_["title"]),
            description=str(dict_["description"]),
            imdb_rating=float(dict_["imdb_rating"]),
            genre=list(map(str, dict_["genres"])),
            writers_names=ETLPersonMovie.dict_to_list(dict_["writers_names"]),
            actors_names=ETLPersonMovie.dict_to_list(dict_["actors_names"]),
            director=ETLPersonMovie.dict_to_list(dict_["director"]),
            writers=ETLPersonMovie.dict_to_list_cls(dict_["writers"]),
            actors=ETLPersonMovie.dict_to_list_cls(dict_["actors"]),
            directors=ETLPersonMovie.dict_to_list_cls(dict_["directors"]),
        )
