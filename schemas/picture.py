from pydantic import BaseModel

class PictureBase(BaseModel):
    id: int
    path: str

    class Config:
        from_attributes = True

class PictureWithTolerance(PictureBase):
    tolerance: float | None = None

    class Config:
        from_attributes = True

class PictureWithPeople(PictureBase):
    people: list["PersonBase"] = []

    class Config:
        from_attributes = True

from .person import PersonBase
PictureWithPeople.model_rebuild()
