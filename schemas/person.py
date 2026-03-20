from pydantic import BaseModel

class PersonBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class PersonWithPictures(PersonBase):
    pictures: list["PictureWithTolerance"] = []

    class Config:
        from_attributes = True

class PersonUpdate(BaseModel):
    name: str

from .picture import PictureBase, PictureWithTolerance
PersonWithPictures.model_rebuild()
