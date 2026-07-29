from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.users import UserService

router = APIRouter()
user_service = UserService()

@router.get("", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """
    List all staff and admin users.
    """
    try:
        users = user_service.get_all_users(db)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """
    Get a specific user by ID.
    """
    try:
        user = user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new staff or admin user.
    Staff users must be assigned to a shop.
    """
    try:
        if user.role not in ['staff', 'admin']:
            raise HTTPException(status_code=400, detail="Role must be 'staff' or 'admin'")
        
        if user.role == 'staff' and not user.shop_id:
            raise HTTPException(status_code=400, detail="Staff users must be assigned to a shop")
        
        created_user = user_service.create_user(db, user)
        return created_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_data: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user's details.
    Staff users must be assigned to a shop.
    """
    try:
        user = user_service.update_user(db, user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate shop assignment for staff users after update
        if user.role == 'staff' and not user.shop_id:
            raise HTTPException(status_code=400, detail="Staff users must be assigned to a shop")
        
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """
    Delete a user.
    """
    try:
        success = user_service.delete_user(db, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
