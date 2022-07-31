from sqlalchemy.ext.declarative import declarative_base
from pymongo import MongoClient

from app.config import get_settings


Base = declarative_base()

def create_db():
    client = MongoClient(get_settings().mongo_db)
    db = client['mongodb']
    return db