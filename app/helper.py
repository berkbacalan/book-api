from app.database import SessionLocal
from app.schema import UserLoginSchema, UserSchema
from . import model


def is_user_exists(user: UserSchema, db: SessionLocal):
    user = db.query(model.User).filter(model.User.email==user.email).first()
    if user:
        return True
    
    return False


def check_user(data: UserLoginSchema, db: SessionLocal):
    users = db.query(model.User).all()
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False