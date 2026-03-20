from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .Person import Person
from .Picture import Picture
from .Face_Encodings import FaceEncoding
