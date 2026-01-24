from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.models.user import User
from sqlalchemy.orm import Session
import uuid
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

    @staticmethod
    def get_password_hash(password: str) -> str:
        return hash_password(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        # First create the customer
        from app.models.customer import Customer
        from app.models.shop import Shop
        from app.schemas.enums import UserRole
        
        db_customer = Customer(
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            address=user_data.get("address"),
            city=user_data.get("city"),
            state=user_data.get("state"),
            zip_code=user_data.get("zip_code"),
            mobile=user_data["mobile"],
            email=user_data.get("email")
        )
        db.add(db_customer)
        db.flush()  # Get the customer ID without committing

        # Then create the user with reference to customer
        db_user = User(
            id=str(uuid.uuid4()),
            mobile=user_data["mobile"],
            email=user_data.get("email"),
            hashed_password=AuthService.get_password_hash(user_data["password"]),
            customer_id=db_customer.id,
            role=user_data.get("role", UserRole.STAFF)
        )

        if "shop_ids" in user_data:
            shops = db.query(Shop).filter(Shop.id.in_(user_data["shop_ids"])).all()
            db_user.shops = shops

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, mobile: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.mobile == mobile).first()
        if not user or not AuthService.verify_password(password, user.hashed_password):
            return None
        return user