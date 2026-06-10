from sqlalchemy import func, and_
from sqlalchemy.orm import Session, joinedload
from typing import Dict, List, Optional
from datetime import datetime
from app.models.category import Category
from app.models.product import Product
from app.models.product_size import ProductSize
from app.models.sale import Sale, SaleItem
from app.models.purchase import Purchase, PurchaseItem, shop_purchases
from app.schemas.enums import SaleStatus

class DashboardService:
    def get_dashboard_data(self, db: Session, shop_id: Optional[int] = None) -> Dict:
        today = datetime.utcnow().date().isoformat()

        # Sales Calculations
        def get_sales_summary(filters):
            query = db.query(
                func.count(Sale.id),
                func.coalesce(func.sum(Sale.total_price), 0.0),
                func.coalesce(func.sum(Sale.total_quantity), 0)
            ).filter(*filters)
            if shop_id:
                query = query.filter(Sale.shop_id == shop_id)
            res = query.one()
            return {
                "total_count": int(res[0] or 0),
                "total_revenue": float(res[1] or 0.0),
                "total_items_sold": int(res[2] or 0)
            }

        total_sales = get_sales_summary([Sale.status.in_([SaleStatus.COMPLETED, SaleStatus.SHIPPED])])
        todays_sales = get_sales_summary([Sale.date == today, Sale.status != SaleStatus.CANCELLED])
        pending_sales = get_sales_summary([Sale.date == today, Sale.status == SaleStatus.PENDING])
        shipped_sales = get_sales_summary([Sale.date == today, Sale.status == SaleStatus.SHIPPED])

        # Purchase Calculations
        def get_purchases_summary(filters):
            query = db.query(
                func.count(Purchase.id),
                func.coalesce(func.sum(Purchase.total_price), 0.0),
                func.coalesce(func.sum(Purchase.total_quantity), 0)
            ).filter(*filters)
            if shop_id:
                query = query.join(shop_purchases, Purchase.id == shop_purchases.c.purchase_id).filter(shop_purchases.c.shop_id == shop_id)
            res = query.one()
            return {
                "total_count": int(res[0] or 0),
                "total_cost": float(res[1] or 0.0),
                "total_items_purchased": int(res[2] or 0)
            }

        total_purchases = get_purchases_summary([])
        todays_purchases = get_purchases_summary([Purchase.date == today])

        # Product and Category Counts
        prod_query = db.query(func.count(Product.id))
        if shop_id:
            prod_query = prod_query.join(Product.shops).filter(Product.shops.any(id=shop_id))
        total_products = prod_query.scalar() or 0
        total_categories = db.query(func.count(Category.id)).scalar() or 0

        # Inventory Summary
        inventory_query = db.query(
            func.coalesce(func.sum(ProductSize.quantity * Product.unit_price), 0.0),
            func.coalesce(func.sum(ProductSize.quantity * Product.selling_price), 0.0)
        ).select_from(Product).join(ProductSize, Product.id == ProductSize.product_id)
        if shop_id:
            inventory_query = inventory_query.filter(Product.shops.any(id=shop_id))

        inv_res = inventory_query.one()
        total_stock_value = float(inv_res[0] or 0.0)
        projected_sale_value = float(inv_res[1] or 0.0)
        projected_profit_value = projected_sale_value - total_stock_value

        # Most Sold Items
        most_sold_query = db.query(
            SaleItem.product_id,
            SaleItem.product_name,
            SaleItem.product_category,
            func.coalesce(func.sum(SaleItem.quantity), 0).label("total_quantity"),
            func.coalesce(func.sum(SaleItem.total_price), 0.0).label("total_revenue")
        ).join(Sale, SaleItem.sale_id == Sale.id).group_by(SaleItem.product_id, SaleItem.product_name, SaleItem.product_category)

        if shop_id:
            most_sold_query = most_sold_query.filter(Sale.shop_id == shop_id)

        most_sold_res = most_sold_query.order_by(func.sum(SaleItem.quantity).desc()).limit(5).all()

        most_sold_items = {
            f"item_{r.product_id}": {
                "product_name": r.product_name,
                "product_category": r.product_category,
                "total_quantity": int(r.total_quantity),
                "total_revenue": float(r.total_revenue)
            } for r in most_sold_res
        }

        # Recent Sales
        recent_sales_query = db.query(Sale).options(joinedload(Sale.customer))
        if shop_id:
            recent_sales_query = recent_sales_query.filter(Sale.shop_id == shop_id)
        recent_sales = recent_sales_query.order_by(Sale.date.desc(), Sale.id.desc()).limit(5).all()

        # Recent Purchases
        recent_purchases_query = db.query(Purchase).options(joinedload(Purchase.vendor))
        if shop_id:
            recent_purchases_query = recent_purchases_query.join(shop_purchases, Purchase.id == shop_purchases.c.purchase_id).filter(shop_purchases.c.shop_id == shop_id)
        recent_purchases = recent_purchases_query.order_by(Purchase.date.desc(), Purchase.id.desc()).limit(5).all()

        return {
            "total_sales": total_sales,
            "todays_sales": todays_sales,
            "pending_sales": pending_sales,
            "shipped_sales": shipped_sales,
            "total_purchases": total_purchases,
            "todays_purchases": todays_purchases,
            "total_products": int(total_products),
            "total_categories": int(total_categories),
            "inventory_summary": {
                "total_stock_value": total_stock_value,
                "projected_sale_value": projected_sale_value,
                "projected_profit_value": projected_profit_value
            },
            "most_sold_items": most_sold_items,
            "recent_sales": recent_sales,
            "recent_purchases": recent_purchases
        }
