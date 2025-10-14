from sqlalchemy import Column, Integer, String, event
from sqlalchemy.orm import relationship, sessionmaker
from app.models.base import BaseModel

class Customer(BaseModel):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    mobile = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)

    sales = relationship("Sale", back_populates="customer")
    user = relationship("User", back_populates="customer", uselist=False)

# Listener to check for unique mobile number before insert/update
@event.listens_for(Customer, 'before_insert')
@event.listens_for(Customer, 'before_update')
def before_insert_update_customer(mapper, connection, target):
    if target.mobile:
        Session = sessionmaker(bind=connection)
        session = Session()
        existing_customer = session.query(Customer).filter(Customer.mobile == target.mobile, Customer.id != target.id).first()
        if existing_customer:
            raise ValueError(f"Customer with mobile number {target.mobile} already exists.")
        session.close()
    if target.email:
        Session = sessionmaker(bind=connection)
        session = Session()
        existing_customer = session.query(Customer).filter(Customer.email == target.email, Customer.id != target.id).first()
        if existing_customer:
            raise ValueError(f"Customer with email {target.email} already exists.")
        session.close()
