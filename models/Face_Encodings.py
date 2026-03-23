from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, LargeBinary
from . import Base


class FaceEncoding(Base):
    __tablename__ = "face_encodings"

    id: Mapped[int] = mapped_column(primary_key=True)

    person_id: Mapped[int | None] = mapped_column(
        ForeignKey("people.id"),
        nullable=True
    )
    picture_id: Mapped[int] = mapped_column(ForeignKey("pictures.id"))

    encoding: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    tolerance: Mapped[float | None] = mapped_column(nullable=True)

    picture: Mapped["Picture"] = relationship("Picture", overlaps="people,pictures")

