import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from DataBase.models import Base

load_dotenv()
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url, echo=True)
Base.metadata.create_all(bind = engine)
SessionLocal = sessionmaker(bind=engine)