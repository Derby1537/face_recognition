from sqlalchemy import ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from models.Person import Person
from models.Picture import Picture

class FaceEncoding(Base):
    __tablename__ = "face_encodings"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"))
    picture_id: Mapped[int] = mapped_column(ForeignKey("pictures.id"))

    encoding: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    person: Mapped["Person"] = relationship()
    picture: Mapped["Picture"] = relationship()
