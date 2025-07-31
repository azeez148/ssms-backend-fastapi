from sqlalchemy import Column, Integer, String, event
from sqlalchemy.orm import relationship, sessionmaker
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    address = Column(String)
    mobile = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)

    sales = relationship("Sale", back_populates="customer")

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
