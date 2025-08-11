from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
from sqlalchemy import or_

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        mobile=user.mobile,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_mobile(db: Session, mobile: str):
    return db.query(User).filter(User.mobile == mobile).first()

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(
        or_(
            User.username == username,
            User.email == username,
            User.mobile == username
        )
    ).first()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def update_password(db: Session, user: User, new_password: str):
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user
