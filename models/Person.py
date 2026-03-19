from sqlalchemy.orm import relationship

from models.People_Pictures import people_pictures
from . import Base
from sqlalchemy import Column, Integer, LargeBinary, String

class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    encoding = Column(LargeBinary, nullable=False)

    pictures = relationship(
        "Picture",
        secondary=people_pictures,
        back_populates="people"
    )
