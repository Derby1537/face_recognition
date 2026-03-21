
from sqlalchemy.orm import relationship
from . import Base
from sqlalchemy import Column, Integer, LargeBinary, String

class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    encoding = Column(LargeBinary, nullable=False)

    pictures = relationship(
        "Picture",
        secondary="face_encodings",
        back_populates="people"
    )
    face_encodings = relationship(
        "FaceEncoding",
        foreign_keys="FaceEncoding.person_id",
        primaryjoin="Person.id == FaceEncoding.person_id",
    )

