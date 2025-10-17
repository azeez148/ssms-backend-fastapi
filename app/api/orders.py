from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.order import Order, OrderCreate
from app.models.order import Order as OrderModel
from app.api.auth import get_current_user
from app.models.user import User
import uuid

router = APIRouter()

@router.post("", response_model=Order)
async def create_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_order = OrderModel(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        total=order.total,
        status=order.status
    )
    
    for item in order.items:
        order_item = OrderItem(
            id=str(uuid.uuid4()),
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=item.quantity,
            price=item.price
        )
        db_order.items.append(order_item)
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/my-orders", response_model=List[Order])
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(OrderModel).filter(OrderModel.user_id == current_user.id).all()

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(OrderModel).filter(
        OrderModel.id == order_id,
        OrderModel.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order