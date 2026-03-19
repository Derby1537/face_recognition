from db.db import engine
from models.Person import Base

Base.metadata.create_all(engine)

print("Database and tables created successfully")
