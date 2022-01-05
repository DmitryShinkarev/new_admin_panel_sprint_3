from dataclasses import dataclass
from datetime import datetime


@dataclass()
class Movie():
    __slots__ = (
        'id', 'title', 'description', 'rating', 'creation_date', 'type',
        'created', 'modified'
    )

    id: str
    title: str
    description: str
    rating: float
    creation_date: str
    type: str
    created: str
    modified: str

    def __post_init__(self):
        self.rating = 0 if self.rating == None else self.rating
        self.creation_date = '0001-01-01 00:00:00.000000' if \
                self.creation_date == None else self.creation_date
        self.description = '' if self.description == None else \
                self.description
        self.created = str(datetime.now())
        self.modified = str(datetime.now())
        


@dataclass()
class Genre():
    __slots__ = (
        'id', 'name', 'description', 'created', 'modified'
    )
    
    id: str
    name: str
    description: str
    created: str
    modified: str
    
    
    def __post_init__(self):
        self.description = '' if self.description == None else \
                self.description
        self.created = str(datetime.now())
        self.modified = str(datetime.now())
        

@dataclass()
class Person():
    __slots__ = (
        'id', 'full_name', 'birth_date', 'created', 'modified'
    )

    id: str
    full_name: str
    birth_date: str
    created: str
    modified: str

    def __post_init__(self):
        self.birth_date = '0001-01-01 00:00:00.000000' if \
                self.birth_date == None else self.birth_date
        self.created = str(datetime.now())
        self.modified = str(datetime.now())


@dataclass()
class Genre_film_work():
    __slots__ = (
        'id', 'genre_id', 'filmwork_id', 'created'
    )

    id: str
    genre_id: str
    filmwork_id: str
    created: str

    def __post_init__(self):
        self.created = str(datetime.now())


@dataclass()
class Person_film_work():
    __slots__ = (
        'id', 'role', 'person_id', 'filmwork_id', 'created'
    )

    id: str
    role: str
    person_id: str
    filmwork_id: str
    created: str
    
    def __post_init__(self):
        self.created = str(datetime.now())

