from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

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
        db.commit()
        db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: int):
    db_customer = get_customer(db, customer_id)
    if db_customer:
        db.delete(db_customer)
        db.commit()
    return db_customer
