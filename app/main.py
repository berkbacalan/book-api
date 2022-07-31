from itertools import islice
from http import HTTPStatus
from sqlite3 import DatabaseError
from fastapi import FastAPI, Depends, Body
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
import bson
from bson.objectid import ObjectId
from app.auth import JWTBearer, decodeJWT, signJWT
from app.helper import check_user, is_user_exists

from app.schema import BookModel, BookRequest, UpdateBook, UserSchema, UserLoginSchema
from .database import create_db

app = FastAPI()

def get_db():
    db = create_db()
    yield db


@app.get("/")
async def root():
    return "Default backend with status 200"


@app.get('/books', tags=["Book"], dependencies=[Depends(JWTBearer())])
async def get_books(db: Session = Depends(get_db)):
    try:
        books = db.books.find()
        result = list(books)
        for r in result:
            r["_id"] = str(r["_id"])
    except Exception as e:
        # we should capture exception instead of print in production
        # to sending sentry or newrelic etc.
        print(str(e))
        return HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Something went wrong.")
    return result


@app.post('/book', tags=["Book"], dependencies=[Depends(JWTBearer())])
async def save_book(book: BookRequest, db: Session = Depends(get_db)):
    '''
    Assumption: Two book can not share same name.
    '''
    try:
        book_exists = db.books.find({'name': book.name, 'author': book.author})

        if len(list(book_exists)) > 0:
            return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="The book is already in the database")
        book_db = BookModel(name=book.name, author=book.author, category=book.category, stock=book.stock, price=book.price, )
        db.books.insert_one(book_db.__dict__)
    except Exception as e:
        return HTTPException(status_code=HTTPStatus.BAD_GATEWAY, detail=str(e))

    return "Succesfully added."


@app.post('/delete/{book_id}', tags=["Book"], dependencies=[Depends(JWTBearer())])
async def delete_book(book_id: str, db: Session = Depends(get_db)):
    try:
        db.books.remove({'_id': ObjectId(book_id)})
        return HTTPException(status_code=HTTPStatus.OK, detail="Book deleted.")
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@app.put('/update', tags=["Book"], dependencies=[Depends(JWTBearer())])
async def update_book(body: UpdateBook = Body(...), db: Session = Depends(get_db)):
    try:
        book = db.books.update_one({'_id': ObjectId(body.id)}, {
            '$set': {
                'name': body.name if body.name else book['name'],
                'author': body.author if body.author else book['author'],
                'category': body.category if body.category else book['category'],
                'price': body.price if body.price else book['price'],
                'stock': body.stock if body.stock else book['stock']
            }})

        return Response(status_code=200, content="Book updated.")

    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@app.get('/book/{id}', tags=["Book"], dependencies=[Depends(JWTBearer())])
async def get_book(id: str, db: Session = Depends(get_db)):
    try:
        book = db.books.find_one({'_id': ObjectId(id)})
        if book:
            book['_id'] = str(book['_id'])
            return book
        else:
            return HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No book with given id.")
    except bson.errors.InvalidId as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid id.")
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/user/signup", tags=["User"])
async def create_user(user: UserSchema = Body(...), db: Session = Depends(get_db)):
    try:
        # check if there is user with given email address
        user_exists = is_user_exists(user.__dict__['email'], db)
        if user_exists:
            return HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Email address already signed up.")
        else:
            new_user = UserSchema(email=user.__dict__['email'], password=user.__dict__['password'])
            db.users.insert_one(new_user.__dict__)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

    return signJWT(user.__dict__['email'])


@app.post("/user/login", tags=["User"])
async def user_login(user: UserLoginSchema = Body(...), db = Depends(get_db)):
    if check_user(user, db):
        return signJWT(user.email)
    return HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Wrong credentials.")


@app.post("/buy_book/{id}", tags=["Buy"], dependencies=[Depends(JWTBearer())])
async def buy_book(id: str, db: Session = Depends(get_db), auth = Depends(JWTBearer())):
    try:
        book_db = db.books.find_one({'_id': ObjectId(id)})
        if book_db.get('stock') > 0:
            db.books.update_one({'_id': ObjectId(id)}, {
            '$set': {
                'sold': book_db['sold'] + 1,
                'stock': book_db['stock'] -1
            }})
            email = decodeJWT(auth)['email']
            db.shoppings.insert_one({'user': email, 'book': id})
            return Response(status_code=HTTPStatus.OK, content="Succesfully bought book.")
        else:
            return HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Book is not in stocks.")
    except Exception as e:
        return DatabaseError


@app.get("/recommendation", tags=["Recommendation"], dependencies=[Depends(JWTBearer())])
async def get_recommendation(db: Session = Depends(get_db), auth = Depends(JWTBearer())):
    '''
    Recommendation Service
    First step get user's most purchased book category
    Second step sort by NSPF -> book's number of sold / (1 / price)
    '''
    try:
        email = decodeJWT(auth)['email']
        purchased_books = db.shoppings.find({"user": email})
        purchase_history = {}
        for pb in purchased_books:
            pb_book = db.books.find_one({'_id': ObjectId(pb['book'])})
            if purchase_history.get(pb_book['category']):
                purchase_history[pb_book['category']] += 1
            else:
                purchase_history[pb_book['category']] = 1


        most_bought_category = max(purchase_history.keys(), key=(lambda new_k: purchase_history[new_k]))
        print(most_bought_category)

        res = {}

        category_books = db.books.find({'category': most_bought_category})
        for cb in category_books:
            res[cb['sold'] / (1 / cb['price'])] = [cb['name'], cb['author']]
        print("res",res)
        result = list(islice({k: v for k, v in sorted(res.items(), key=lambda item: item[1])}, 5))
        print("result",result)
        
        return HTTPException(status_code=200, detail=result)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
