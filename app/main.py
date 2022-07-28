from http import HTTPStatus
from fastapi import FastAPI, Depends, Body
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.auth import JWTBearer, signJWT
from app.helper import check_user, is_user_exists

from app.schema import BookRequest, Books, UserSchema, UserLoginSchema
from .database import SessionLocal, engine
from . import model

app = FastAPI()
model.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return "Default backend with status 200"


@app.get('/books', tags=["Book"], dependencies=[Depends(JWTBearer())])
async def get_books(db: Session = Depends(get_db)):
    try:
        books = db.query(model.Book).all()
    except Exception as e:
        raise e
    finally:
        db.close()

    return books

@app.post('/book', tags=["Book"], dependencies=[Depends(JWTBearer())])
async def save_book(book: BookRequest, db: Session = Depends(get_db)):
    '''
    Assumption: Two book can not share same name.
    '''
    try:
        book_exists = db.query(model.Book).filter(model.Book.name==book.name and model.Book.author==book.author).first()
        if book_exists:
            return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="The book is already in the database")

        db_book = model.Book(
                name=book.name, author=book.author
            )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
    except Exception as e:
        raise e
    finally:
        db.close()

@app.post('/delete/{book_id}', tags=["Book"], dependencies=[Depends(JWTBearer())])
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    try:
        db.query(model.Book).filter(model.Book.id==book_id).delete()
        db.commit()
    except Exception as e:
        raise e
    finally:
        db.close()
        
        
@app.put('/update/', tags=["Book"], dependencies=[Depends(JWTBearer())])
async def update_book(id: int, name: str, author:str, db: Session = Depends(get_db)):
    try:
        book = db.query(model.Book).filter(model.Book.id==id).first()
        book.name = name
        book.author = author
        db.commit()
    except Exception as e:
        raise e
    finally:
        db.close()

    return Response(status_code=200, content='Book updated.')

@app.get('/book/{id}', tags=["Book"], dependencies=[Depends(JWTBearer())])
async def get_book(id: int, db: Session = Depends(get_db)):
    try:
        book = db.query(model.Book).filter(model.Book.id==id).first()
        if book:
            return book
        else:
            return HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No book with given id.")
    except Exception as e:
        raise e
    finally:
        db.close()

@app.post("/user/signup", tags=["User"])
async def create_user(user: UserSchema = Body(...), db: Session = Depends(get_db)):
    try:
        # check if there is user with given email address
        user_exists = is_user_exists(user, db)
        if user_exists:
            return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Email address already signed up.")
        else:
            new_user = model.User(email=user.email, password=user.password)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
    except Exception as e:
        raise e
    finally:
        db.close()
    
    return signJWT(user.email)


@app.post("/user/login", tags=["User"])
async def user_login(user: UserLoginSchema = Body(...), db: Session = Depends(get_db)):
    if check_user(user, db):
        return signJWT(user.email)
    return HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Wrong credentials.")
