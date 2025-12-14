from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.order import Order, OrderCreate
from app.models.order import Order as OrderModel
from app.models.sale import Sale as SaleModel
from app.models.sale import SaleItem as SaleItemModel
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
    # Query sales where customer_id matches the current user
    sales = db.query(SaleModel).filter(SaleModel.customer_id == current_user.customer_id).all()

    results = []
    for sale in sales:
        # determine date: prefer sale.date (string) if parseable, otherwise use created_date
        from datetime import datetime
        sale_date = None
        if isinstance(sale.date, str) and sale.date:
            try:
                sale_date = datetime.fromisoformat(sale.date)
            except Exception:
                sale_date = sale.created_date
        else:
            sale_date = sale.created_date

        order_obj = {
            "id": str(sale.id),
            "user_id": str(sale.customer_id) if sale.customer_id is not None else None,
            "date": sale_date,
            "total": float(sale.total_price) if sale.total_price is not None else 0.0,
            "status": sale.status.name if hasattr(sale.status, 'name') else str(sale.status),
            "created_at": sale.created_date,
            "updated_at": sale.updated_date or sale.created_date,
            "items": []
        }

        for si in sale.sale_items:
            item_obj = {
                "id": str(si.id),
                "order_id": str(si.sale_id),
                "created_at": si.created_date or sale.created_date,
                "updated_at": si.updated_date or si.created_date or sale.created_date,
                "product_id": str(si.product_id) if si.product_id is not None else None,
                "product_name": si.product_name,
                "quantity": int(si.quantity) if si.quantity is not None else 0,
                "price": float(si.sale_price) if si.sale_price is not None else 0.0
            }
            order_obj["items"].append(item_obj)

        results.append(order_obj)

    return results

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