from sqlalchemy.orm import Session, joinedload
from app.models.sale import Sale
from app.schemas.report import SalesReportResponse
from typing import Optional

class ReportService:
    def get_sales_report(self, db: Session, start_date: Optional[str] = None, end_date: Optional[str] = None) -> SalesReportResponse:
        query = db.query(Sale).options(
            joinedload(Sale.customer),
            joinedload(Sale.payment_type),
            joinedload(Sale.delivery_type),
            joinedload(Sale.sale_items)
        )

        if start_date:
            query = query.filter(Sale.date >= start_date)
        if end_date:
            query = query.filter(Sale.date <= end_date)

        sales = query.all()

        total_sales = len(sales)
        total_amount = sum(sale.total_price for sale in sales)
        total_quantity = sum(sale.total_quantity for sale in sales)

        status_breakdown = {}
        for sale in sales:
            status = sale.status.value if hasattr(sale.status, 'value') else str(sale.status)
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

        return SalesReportResponse(
            sales=sales,
            total_sales=total_sales,
            status_breakdown=status_breakdown,
            total_amount=total_amount,
            total_quantity=total_quantity
        )
