from sqlalchemy.orm import Session

from models.Face_Encodings import FaceEncoding
from models.Person import Person
from models.Picture import Picture


def getStats(db: Session) -> dict:
    total_people = db.query(Person).count()
    total_pictures = db.query(Picture).count()
    total_encodings = db.query(FaceEncoding).count()
    assigned_encodings = db.query(FaceEncoding).filter(FaceEncoding.person_id.isnot(None)).count()
    unassigned_encodings = total_encodings - assigned_encodings

    return {
        "people": total_people,
        "pictures": total_pictures,
        "encodings": {
            "total": total_encodings,
            "assigned": assigned_encodings,
            "unassigned": unassigned_encodings,
        },
    }
