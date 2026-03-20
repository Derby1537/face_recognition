from typing import List, Optional

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from controllers import people_controller
from db.db import get_db
from schemas.person import PersonBase, PersonUpdate, PersonWithPictures

router = APIRouter()


@router.get("/", response_model=List[PersonBase])
async def getPeople(
    search: Optional[str] = None,
    id: Optional[int] = None,
    name: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    db: Session = Depends(get_db)
):
    page_size = min(page_size, 100)
    return people_controller.getPeople(db, search, id, name, page, page_size)


@router.post("/sync_pictures")
async def syncPictures(
    id: int,
    tolerance: float = 0.5,
    db: Session = Depends(get_db)
):
    return people_controller.syncPictures(db, id, tolerance)


@router.get("/{id}", response_model=PersonWithPictures)
async def getPerson(id: int, db: Session = Depends(get_db)):
    return people_controller.getPerson(db, id)


@router.put("/{id}", response_model=PersonBase)
async def putPerson(id: int, data: PersonUpdate, db: Session = Depends(get_db)):
    return people_controller.putPerson(db, id, data.name)


@router.post("/")
async def postPerson(file: UploadFile = File(...), name: str = "", sync: bool = False, tolerance: float = 0.5, db: Session = Depends(get_db)):
    return await people_controller.postPerson(db, file, name, sync, tolerance)


@router.delete("/{id}")
async def deletePerson(id: int, db: Session = Depends(get_db)):
    return people_controller.deletePerson(db, id)


@router.post("/recognize")
async def recognizePerson(file: UploadFile = File(...), tolerance: float = 0.5):
    return await people_controller.recognizePerson(file, tolerance)
