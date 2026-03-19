from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from . import Base

people_pictures = Table(
    "people_pictures",
    Base.metadata,
    Column("person_id", Integer, ForeignKey("people.id"), primary_key=True),
    Column("picture_id", Integer, ForeignKey("pictures.id"), primary_key=True)
)
