from . import Base
from sqlalchemy import Column, Integer, LargeBinary, String

class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    encoding = Column(LargeBinary, nullable=False)
