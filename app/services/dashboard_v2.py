from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.models.sale import Sale, SaleItem
from app.models.product import Product, shop_products
from app.models.product_size import ProductSize
from app.schemas.enums import SaleStatus
from app.schemas.dashboard_v2 import (
    DashboardV2Response, DashboardV2Performance, PerformanceMetrics,
    DashboardV2StockInsights, StockInsightItem, DashboardV2Financials
)

class DashboardV2Service:
    def get_dashboard_data(
        self,
        db: Session,
        shop_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> DashboardV2Response:
        performance = self._get_performance(db, shop_id, start_date, end_date)
        stock_insights = self._get_stock_insights(db, shop_id)
        financials = self._get_financials(db, shop_id)

        return DashboardV2Response(
            performance=performance,
            stock_insights=stock_insights,
            financials=financials
        )

    def _get_performance(
        self,
        db: Session,
        shop_id: Optional[int] = None,
        custom_start: Optional[str] = None,
        custom_end: Optional[str] = None
    ) -> DashboardV2Performance:
        today = date.today()

        # Ranges
        daily_start = today.isoformat()
        weekly_start = (today - timedelta(days=today.weekday())).isoformat()
        monthly_start = today.replace(day=1).isoformat()
        yearly_start = today.replace(month=1, day=1).isoformat()

        return DashboardV2Performance(
            daily=self._calculate_performance_metrics(db, daily_start, None, shop_id),
            weekly=self._calculate_performance_metrics(db, weekly_start, None, shop_id),
            monthly=self._calculate_performance_metrics(db, monthly_start, None, shop_id),
            yearly=self._calculate_performance_metrics(db, yearly_start, None, shop_id),
            custom=self._calculate_performance_metrics(db, custom_start, custom_end, shop_id) if custom_start else None
        )

    def _calculate_performance_metrics(
        self,
        db: Session,
        start_date: str,
        end_date: Optional[str] = None,
        shop_id: Optional[int] = None
    ) -> PerformanceMetrics:
        # Aggregate Sale metrics
        sale_query = db.query(
            func.count(Sale.id).label('orders'),
            func.sum(Sale.total_price).label('revenue'),
            func.sum(Sale.total_quantity).label('items_sold')
        ).filter(
            Sale.status.in_([SaleStatus.COMPLETED, SaleStatus.SHIPPED]),
            Sale.date >= start_date
        )
        if end_date:
            sale_query = sale_query.filter(Sale.date <= end_date)
        if shop_id:
            sale_query = sale_query.filter(Sale.shop_id == shop_id)

        sale_stats = sale_query.first()

        # Aggregate profit
        # We need to join SaleItem with Product to get unit_price
        profit_query = db.query(
            func.sum((SaleItem.sale_price - Product.unit_price) * SaleItem.quantity)
        ).join(Sale, SaleItem.sale_id == Sale.id).join(
            Product, SaleItem.product_id == Product.id
        ).filter(
            Sale.status.in_([SaleStatus.COMPLETED, SaleStatus.SHIPPED]),
            Sale.date >= start_date
        )
        if end_date:
            profit_query = profit_query.filter(Sale.date <= end_date)
        if shop_id:
            profit_query = profit_query.filter(Sale.shop_id == shop_id)

        profit = profit_query.scalar() or 0.0

        return PerformanceMetrics(
            revenue=round(float(sale_stats.revenue or 0.0), 2),
            profit=round(float(profit), 2),
            orders=int(sale_stats.orders or 0),
            items_sold=int(sale_stats.items_sold or 0)
        )

    def _get_stock_insights(self, db: Session, shop_id: Optional[int] = None) -> DashboardV2StockInsights:
        # Base query for products
        product_ids_query = db.query(Product.id)
        if shop_id:
            product_ids_query = product_ids_query.join(shop_products).filter(shop_products.c.shop_id == shop_id)

        product_ids = [p.id for p in product_ids_query.all()]

        # Stock status
        stock_query = db.query(
            ProductSize.product_id,
            func.sum(ProductSize.quantity).label('total_qty')
        ).filter(ProductSize.product_id.in_(product_ids)).group_by(ProductSize.product_id).all()

        total_instock = 0
        out_of_stock_count = 0
        stock_map = {p_id: qty for p_id, qty in stock_query}

        # Products that are not in stock_map actually have 0 quantity (if we assume ProductSize records exist)
        # But we should check all products in the shop
        for p_id in product_ids:
            qty = stock_map.get(p_id, 0)
            if qty > 0:
                total_instock += 1
            else:
                out_of_stock_count += 1

        # Most/Less sold
        sold_query = db.query(
            SaleItem.product_id,
            SaleItem.product_name,
            func.sum(SaleItem.quantity).label('total_qty_sold')
        ).join(Sale).filter(
            Sale.status.in_([SaleStatus.COMPLETED, SaleStatus.SHIPPED]),
            SaleItem.product_id.in_(product_ids)
        ).group_by(SaleItem.product_id, SaleItem.product_name)

        sold_stats = sold_query.order_by(func.sum(SaleItem.quantity).desc()).all()

        # Map to items
        items = [
            StockInsightItem(
                product_id=p_id,
                product_name=p_name,
                quantity_sold=int(q_sold),
                current_stock=int(stock_map.get(p_id, 0))
            ) for p_id, p_name, q_sold in sold_stats
        ]

        return DashboardV2StockInsights(
            total_instock_items=total_instock,
            out_of_stock_items=out_of_stock_count,
            most_sold=items[:10],
            less_sold=items[-10:] if items else []
        )

    def _get_financials(self, db: Session, shop_id: Optional[int] = None) -> DashboardV2Financials:
        # Expected metrics
        product_query = db.query(Product).options() # We need prices
        if shop_id:
            product_query = product_query.join(shop_products).filter(shop_products.c.shop_id == shop_id)

        products = product_query.all()
        p_ids = [p.id for p in products]

        # Get current stock levels
        stock_levels = db.query(
            ProductSize.product_id,
            func.sum(ProductSize.quantity).label('total_qty')
        ).filter(ProductSize.product_id.in_(p_ids)).group_by(ProductSize.product_id).all()
        stock_map = {p_id: qty for p_id, qty in stock_levels}

        total_instock_value = 0.0
        expected_sales_value = 0.0
        expected_profit = 0.0

        for p in products:
            qty = stock_map.get(p.id, 0)
            if qty > 0:
                unit_price = p.unit_price or 0
                selling_price = p.selling_price or 0
                current_price = p.discounted_price if p.discounted_price is not None else selling_price

                total_instock_value += qty * unit_price
                expected_sales_value += qty * current_price
                expected_profit += qty * (current_price - unit_price)

        # Current actuals (All time)
        actual_sale_query = db.query(
            func.sum(Sale.total_price).label('total_revenue')
        ).filter(Sale.status.in_([SaleStatus.COMPLETED, SaleStatus.SHIPPED]))
        if shop_id:
            actual_sale_query = actual_sale_query.filter(Sale.shop_id == shop_id)

        current_sales = actual_sale_query.scalar() or 0.0

        actual_profit_query = db.query(
            func.sum((SaleItem.sale_price - Product.unit_price) * SaleItem.quantity)
        ).join(Sale, SaleItem.sale_id == Sale.id).join(
            Product, SaleItem.product_id == Product.id
        ).filter(
            Sale.status.in_([SaleStatus.COMPLETED, SaleStatus.SHIPPED])
        )
        if shop_id:
            actual_profit_query = actual_profit_query.filter(Sale.shop_id == shop_id)

        current_profit = actual_profit_query.scalar() or 0.0

        return DashboardV2Financials(
            total_instock_value=round(float(total_instock_value), 2),
            expected_sales_value=round(float(expected_sales_value), 2),
            expected_profit_loss=round(float(expected_profit), 2),
            current_sales=round(float(current_sales), 2),
            current_profit_loss=round(float(current_profit), 2)
        )
