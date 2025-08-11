from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import user as user_schema
from app.services import user_service, notification
from app.core import security

router = APIRouter()
email_notification_service = notification.EmailNotificationService()

@router.post("/register", response_model=user_schema.User)
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = user_service.get_user_by_mobile(db, mobile=user.mobile)
    if db_user:
        raise HTTPException(status_code=400, detail="Mobile number already registered")
    return user_service.create_user(db=db, user=user)


@router.post("/login", response_model=user_schema.Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_service.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password")
def forgot_password(request: user_schema.PasswordResetRequest, db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, email=request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = security.create_access_token(data={"sub": user.username})
    email_notification_service.send_password_reset_email(user, reset_token)
    return {"message": "Password reset email sent"}


@router.post("/reset-password")
def reset_password(request: user_schema.PasswordReset, db: Session = Depends(get_db)):
    try:
        username = security.verify_access_token(
            request.token,
            credentials_exception=HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        )
        user = user_service.get_user_by_username(db, username=username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_service.update_password(db, user, request.new_password)
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {e}"
        )
