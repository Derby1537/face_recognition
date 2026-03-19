from pydantic import BaseModel

class PictureSchema(BaseModel):
    id: int
    path: str

    class Config:
        from_attributes = True
