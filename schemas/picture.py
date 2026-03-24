import os
from pydantic import BaseModel, field_validator

class PictureBase(BaseModel):
    id: int
    path: str

    @field_validator("path")
    @classmethod
    def filename_only(cls, v: str) -> str:
        return os.path.basename(v)

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
