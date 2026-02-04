from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate, ResetPasswordRequest
from app.services import customer as customer_service
from app.core.config import settings

router = APIRouter()

@router.post("/addCustomer", response_model=CustomerResponse, summary="Create a new customer")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer.
    """
    return customer_service.create_customer(db=db, customer=customer)


@router.get("/all", response_model=List[CustomerResponse], summary="Get all customers")
def read_customers(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    """
    Retrieve all customers.
    """
    customers = customer_service.get_customers(db, skip=skip, limit=limit)
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse, summary="Get a specific customer")
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific customer by ID.
    """
    db_customer = customer_service.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer


@router.put("/{customer_id}", response_model=CustomerResponse, summary="Update a customer")
def update_customer(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    """
    Update a customer's information.
    """
    db_customer = customer_service.update_customer(db, customer_id=customer_id, customer=customer)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer


@router.delete("/{customer_id}", response_model=CustomerResponse, summary="Delete a customer")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Delete a customer.
    """
    db_customer = customer_service.delete_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer


@router.post("/reset-password", summary="Reset a customer's password")
def reset_customer_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset a customer's password.
    """
    if request.security_password != settings.SYSTEM_PASS_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid pass_key",
        )
    success = customer_service.reset_password(db, customer_id=request.customer_id, new_password=request.new_password)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found or password reset failed")
    return {"detail": "Password reset successfully"}
