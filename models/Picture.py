from sqlalchemy.orm import relationship
from . import Base
from sqlalchemy import Column, Integer, String

class Picture(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True)
    path = Column(String(255), nullable=False, index=True)

    people = relationship(
        "Person",
        secondary="face_encodings",  # tabella di associazione
        back_populates="pictures"
    )
