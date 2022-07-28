from .database import Base
from sqlalchemy import Column, Integer, String


class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    author = Column(String, index=True)
