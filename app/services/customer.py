from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Customer).offset(skip).limit(limit).all()

def get_customer_by_mobile(db: Session, mobile: str):
    return db.query(Customer).filter(Customer.mobile == mobile).first()

def get_or_create_customer(db: Session, customer: CustomerCreate):
    """
    Get a customer by mobile number, or create a new one if not found.
    """
    db_customer = get_customer_by_mobile(db, customer.mobile)
    if db_customer:
        return db_customer
    return create_customer(db, customer)

def create_customer(db: Session, customer: CustomerCreate):
    db_customer = Customer(**customer.model_dump(), created_by="system", updated_by="system")
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(db: Session, customer_id: int, customer: CustomerUpdate):
    db_customer = get_customer(db, customer_id)
    if db_customer:
        update_data = customer.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_customer, key, value)
        db_customer.updated_by = "system"
        db.commit()
        db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: int):
    db_customer = get_customer(db, customer_id)
    if db_customer:
        db.delete(db_customer)
        db.commit()
    return db_customer
