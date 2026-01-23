from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.user import LoginRequest, RegisterRequest, UserProfile, UserProfileUpdate, AuthResponse
from app.services.auth import AuthService
from app.models.user import User
from datetime import timedelta

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = AuthService.decode_token(token)
    if not payload:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise credentials_exception
    return user

@router.post("/register", response_model=AuthResponse)
async def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user exists by mobile number in either users or customers table
    if db.query(User).filter(User.mobile == user_data.mobile).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered in users"
        )
    
    from app.models.customer import Customer
    if db.query(Customer).filter(Customer.mobile == user_data.mobile).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered in customers"
        )
    
    # Create user
    user = AuthService.create_user(db, user_data.model_dump())
    
    # Create access token
    access_token = AuthService.create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(days=7)
    )
    
    return AuthResponse(token=access_token, user=user)

@router.post("/login", response_model=AuthResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, login_data.mobile, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect mobile number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = AuthService.create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(days=7)
    )

    user = UserProfile.from_user_and_customer(user, user.customer)
    
    return AuthResponse(token=access_token, user=user)

@router.post("/logout")
async def logout():
    # In a stateless JWT setup, client-side logout is sufficient
    # Server-side logout would be needed for token blacklisting
    return {"message": "Successfully logged out"}

@router.get("/status")
async def auth_status(current_user: User = Depends(get_current_user)):
    user = UserProfile.from_user_and_customer(current_user, current_user.customer)
    return user

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return UserProfile.from_user_and_customer(current_user, current_user.customer)

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    for field, value in profile_update.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user