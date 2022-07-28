from fastapi import FastAPI
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import model
from .config import BASE_URL, PROTOCOL

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
