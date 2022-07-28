from pydantic import BaseModel
from typing import List

class BookRequest(BaseModel):
    name: str
    author: str

class BookResponse(BaseModel):
    id: int
    name: str
    author: str

    class Config:
        orm_mode = True


class Books(BaseModel):
    books: List[BookResponse]