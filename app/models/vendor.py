from sqlalchemy import Column, Integer, String, event
from sqlalchemy.orm import relationship, sessionmaker
from app.models.base import BaseModel

class Vendor(BaseModel):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    address = Column(String)
    mobile = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)

    purchases = relationship("Purchase", back_populates="vendor")

# Listener to check for unique mobile number before insert/update
@event.listens_for(Vendor, 'before_insert')
@event.listens_for(Vendor, 'before_update')
def before_insert_update_vendor(mapper, connection, target):
    if target.mobile:
        Session = sessionmaker(bind=connection)
        session = Session()
        existing_vendor = session.query(Vendor).filter(Vendor.mobile == target.mobile, Vendor.id != target.id).first()
        if existing_vendor:
            raise ValueError(f"Vendor with mobile number {target.mobile} already exists.")
        session.close()
    if target.email:
        Session = sessionmaker(bind=connection)
        session = Session()
        existing_vendor = session.query(Vendor).filter(Vendor.email == target.email, Vendor.id != target.id).first()
        if existing_vendor:
            raise ValueError(f"Vendor with email {target.email} already exists.")
        session.close()
