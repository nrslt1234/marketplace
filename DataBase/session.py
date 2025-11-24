from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from DataBase.models import Base

database_url = "postgresql+psycopg2://postgres:03092006@localhost:5432/DataB"
engine = create_engine(database_url, echo=True)
Base.metadata.create_all(bind = engine)
SessionLocal = sessionmaker(bind=engine)