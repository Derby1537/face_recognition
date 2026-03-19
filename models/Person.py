from sqlalchemy import Column, Integer, LargeBinary, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    encoding = Column(LargeBinary, nullable=False)
