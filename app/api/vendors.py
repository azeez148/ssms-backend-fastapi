from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.vendor import VendorCreate, VendorResponse, VendorUpdate
from app.services import vendor as vendor_service

router = APIRouter()

@router.post("/", response_model=VendorResponse, summary="Create a new vendor")
def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    """
    Create a new vendor.
    """
    return vendor_service.create_vendor(db=db, vendor=vendor)


@router.get("/", response_model=List[VendorResponse], summary="Get all vendors")
def read_vendors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all vendors.
    """
    vendors = vendor_service.get_vendors(db, skip=skip, limit=limit)
    return vendors


@router.get("/{vendor_id}", response_model=VendorResponse, summary="Get a specific vendor")
def read_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific vendor by ID.
    """
    db_vendor = vendor_service.get_vendor(db, vendor_id=vendor_id)
    if db_vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_vendor


@router.put("/{vendor_id}", response_model=VendorResponse, summary="Update a vendor")
def update_vendor(vendor_id: int, vendor: VendorUpdate, db: Session = Depends(get_db)):
    """
    Update a vendor's information.
    """
    db_vendor = vendor_service.update_vendor(db, vendor_id=vendor_id, vendor=vendor)
    if db_vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_vendor


@router.delete("/{vendor_id}", response_model=VendorResponse, summary="Delete a vendor")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """
    Delete a vendor.
    """
    db_vendor = vendor_service.delete_vendor(db, vendor_id=vendor_id)
    if db_vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return db_vendor
