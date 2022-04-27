import typing
import uuid
from dataclasses import dataclass


@dataclass()
class ETLPerson:
    __slots__ = ("id", "name")

    id: uuid.UUID
    name: str

    @classmethod
    def from_dict_cls(cls, dict_: typing.Dict[str, typing.Any]):
        if dict_:
            return cls(id=dict_["id"], name=dict_["name"])
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
class ETLGenre:
    __slots__ = ("id", "name")

    id: str
    name: str

    @classmethod
    def from_dict_cls(cls, dict_: typing.Dict[str, typing.Any]):
        if dict_:
            return cls(id=dict_["id"], name=dict_["name"])
        return ""

    @classmethod
    def dict_to_list(cls, iterable: typing.Iterable[dict]):
        if iterable:
            return [cls.from_dict_cls(it) for it in iterable]
        return []


@dataclass()
class ETLMovie:
    __slots__ = (
        "id",
        "title",
        "description",
        "rating",
        "genre",
        "writers_names",
        "actors_names",
        "director",
        "writers",
        "actors",
    )

    id: uuid.UUID
    title: str
    description: str
    rating: float
    genre: typing.List[str]
    writers_names: typing.List[str]
    actors_names: typing.List[str]
    director: typing.List[str]
    writers: typing.List["ETLPerson"]
    actors: typing.List["ETLPerson"]

    @classmethod
    def from_dict_cls(cls, dict_: typing.Dict[str, typing.Any]) -> "ETLMovie":
        return cls(
            id=dict_["id"],
            title=str(dict_["title"]),
            description=str(dict_["description"]),
            rating=float(dict_["rating"]),
            genre=list(map(str, dict_["genres"])),
            writers_names=ETLPerson.dict_to_list(dict_["writers_names"]),
            actors_names=ETLPerson.dict_to_list(dict_["actors_names"]),
            director=ETLPerson.dict_to_list(dict_["director"]),
            writers=ETLPerson.dict_to_list_cls(dict_["writers"]),
            actors=ETLPerson.dict_to_list_cls(dict_["actors"]),
        )
