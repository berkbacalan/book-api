from app.schema import UserLoginSchema


def is_user_exists(email: str, db):
    user = db.users.find_one({'email': email})
    if user:
        return True
    
    return False


def check_user(data: UserLoginSchema, db):
    users = db.users.find()
    for user in list(users):
        if user["email"] == data.email and user["password"] == data.password:
            return True
    return False
