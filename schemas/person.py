from typing import List
from pydantic import BaseModel

from schemas.picture import PictureSchema

class PersonSchema(BaseModel):
    id: int
    name: str

    pictures: List[PictureSchema] = []

    class Config:
        from_attributes = True

class PersonUpdate(BaseModel):
    name: str
