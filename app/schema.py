from pydantic import BaseModel
from typing import List

class Book(BaseModel):
    id: int
    name: str
    author: str


class Books(BaseModel):
    books: List[Book]