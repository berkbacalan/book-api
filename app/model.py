from pydantic import BaseModel
from sqlalchemy import Column, Integer, String


class Book(BaseModel):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    author = Column(String, index=True)