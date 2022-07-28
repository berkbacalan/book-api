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


class UserSchema(BaseModel):
    email: str
    password: str

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
