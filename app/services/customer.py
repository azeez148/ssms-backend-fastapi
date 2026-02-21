from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.auth import AuthService
from app.models.user import User

def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Customer).offset(skip).limit(limit).all()

def get_customer_by_email(db: Session, email: str):
    return db.query(Customer).filter(Customer.email == email).first()

def get_customer_by_mobile(db: Session, mobile: str):
    return db.query(Customer).filter(Customer.mobile == mobile).first()

def get_or_create_customer(db: Session, customer: CustomerCreate):
    """
    Get a customer by mobile number, or create a new one if not found.
    """
    db_customer = get_customer_by_mobile(db, customer.mobile)
    if not db_customer and customer.email and customer.email.strip():  # Only check email if it's not empty
        db_customer = get_customer_by_email(db, customer.email)
    if db_customer:
        return db_customer
    return create_customer(db, customer)

def create_customer(db: Session, customer: CustomerCreate):
    customer_data = customer.model_dump()
    if 'name' in customer_data:
        name = customer_data.pop('name')
        name_parts = name.split(' ', 1)
        customer_data['first_name'] = name_parts[0]
        customer_data['last_name'] = name_parts[1] if len(name_parts) > 1 else None
    
    # Use normalized email to handle empty strings
    customer_data['email'] = customer.normalized_email

    db_customer = Customer(**customer_data, created_by="system", updated_by="system")
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(db: Session, customer_id: int, customer: CustomerUpdate):
    db_customer = get_customer(db, customer_id)
    if db_customer:
        update_data = customer.model_dump(exclude_unset=True)
        if 'name' in update_data:
            name = update_data.pop('name')
            name_parts = name.split(' ', 1)
            update_data['first_name'] = name_parts[0]
            update_data['last_name'] = name_parts[1] if len(name_parts) > 1 else None

        for key, value in update_data.items():
            setattr(db_customer, key, value)
        db_customer.updated_by = "system"
        
        # Update related User record with common attributes (mobile and email)
        db_user = db.query(User).filter(User.customer_id == customer_id).first()
        if db_user:
            if 'mobile' in update_data:
                db_user.mobile = update_data['mobile']
            if 'email' in update_data:
                db_user.email = update_data['email'] if update_data['email'] and update_data['email'].strip() else None
        
        db.commit()
        db.refresh(db_customer)
        if db_user:
            db.refresh(db_user)
    return db_customer

def delete_customer(db: Session, customer_id: int):
    db_customer = get_customer(db, customer_id)
    if db_customer:
        db.delete(db_customer)
        db.commit()
    return db_customer

def reset_password(db: Session, customer_id: int, new_password: str) -> bool:
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return False

    db_user = db.query(User).filter(User.customer_id == customer_id).first()
    if not db_user:
        return False

    new_password = new_password or db_customer.mobile

    # Only hash password for non-staff/admin users
    if db_user.role not in ['staff', 'admin']:
        hashed_password = AuthService.get_password_hash(new_password)
    else:
        hashed_password = new_password

    db_user.hashed_password = hashed_password
    db.commit()
    return True
