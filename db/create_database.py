from db.db import engine
from models import Base

Base.metadata.create_all(engine)

print("Database and tables created successfully")
