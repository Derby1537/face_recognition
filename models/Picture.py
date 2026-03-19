
from sqlalchemy.orm import relationship
from models.People_Pictures import people_pictures
from . import Base
from sqlalchemy import Column, Integer, String

class Picture(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True)
    path = Column(String(255), nullable=False, index=True)

    people = relationship(
        "Person",
        secondary=people_pictures,
        back_populates="pictures"
    )
