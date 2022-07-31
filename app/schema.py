from pydantic_mongo import ObjectIdField
from pydantic import BaseModel
from typing import List

class BookRequest(BaseModel):
    name: str
    author: str
    category: str
    stock: int
    price: float


class BookModel(BookRequest):
    sold: int = 0


class BookResponse(BaseModel):
    id: ObjectIdField
    name: str
    author: str
    stock: int
    sold: int
    price: float

    class Config:
        orm_mode = True


class Books(BaseModel):
    books: List[BookResponse]


class UpdateBook(BookRequest):
    id: str


class UserSchema(BaseModel):
    email: str
    password: str

    def __dict__(self):
        return {
            "email": self.email,
            "password": self.password

        }

    class Config:
        schema_extra = {
            "example": {
                "email": "johndoe@domain.com",
                "password": "password"
            }
        }

class UserLoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "johndoe@domain.com",
                "password": "password"
            }
        }
