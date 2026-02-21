from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdate, UserCreate
from typing import List, Optional

class UserService:
    def get_all_users(self, db: Session) -> List[User]:
        """
        Get all staff and admin users.
        """
        return db.query(User).filter(User.role.in_(['staff', 'admin'])).all()

    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """
        Get a specific user by ID.
        """
        return db.query(User).filter(User.id == user_id, User.role.in_(['staff', 'admin'])).first()

    def get_user_by_mobile(self, db: Session, mobile: str) -> Optional[User]:
        """
        Get a user by mobile number.
        """
        return db.query(User).filter(User.mobile == mobile, User.role.in_(['staff', 'admin'])).first()

    def update_user(self, db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """
        Update a user's details.
        Staff users must be assigned to a shop.
        """
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        
        # Store password as plain text for staff/admin users
        if 'password' in update_data and update_data['password']:
            update_data['hashed_password'] = update_data['password']
            update_data.pop('password')

        for key, value in update_data.items():
            setattr(db_user, key, value)

        # Validate shop assignment for staff users
        if db_user.role == 'staff' and not db_user.shop_id:
            raise ValueError("Staff users must be assigned to a shop")

        db.commit()
        db.refresh(db_user)
        return db_user

    def delete_user(self, db: Session, user_id: str) -> bool:
        """
        Delete a user.
        """
        db_user = self.get_user_by_id(db, user_id)
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True

    def create_user(self, db: Session, user_data: UserCreate) -> Optional[User]:
        """
        Create a new staff or admin user.
        Staff users must be assigned to a shop.
        """
        # Check if mobile already exists
        existing_user = self.get_user_by_mobile(db, user_data.mobile)
        if existing_user:
            raise ValueError(f"User with mobile {user_data.mobile} already exists")

        # Validate shop assignment for staff users
        if user_data.role == 'staff':
            if not user_data.shop_id:
                raise ValueError("Staff users must be assigned to a shop")

        # Store password as plain text for staff/admin users
        db_user = User(
            id=user_data.id,
            mobile=user_data.mobile,
            email=user_data.email,
            hashed_password=user_data.password,
            role=user_data.role,
            shop_id=user_data.shop_id
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
