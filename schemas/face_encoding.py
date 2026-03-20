from pydantic import BaseModel

class FaceEncodingSchema(BaseModel):
    id: int
    picture_id: int
    tolerance: float | None = None

    class Config:
        from_attributes = True
