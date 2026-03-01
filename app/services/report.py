from sqlalchemy.orm import Session, joinedload
from app.models.sale import Sale
from app.models.product import Product
from app.schemas.report import (
    SalesReportResponse, SalesComparisonResponse,
    SalesReportSummary, SalesComparisonDifference
)
from app.schemas.enums import SaleStatus
from typing import Optional

class ReportService:
    def _calculate_summary(self, db: Session, sales) -> dict:
        """Calculate summary metrics for a list of sales."""
        # Filter sales to avoid CANCELLED, PENDING, RETURNED for summary calculation
        active_sales = [
            sale for sale in sales
            if sale.status not in [SaleStatus.CANCELLED, SaleStatus.PENDING, SaleStatus.RETURNED]
        ]

        total_sales = len(active_sales)
        total_revenue = sum(sale.total_price for sale in active_sales)
        total_quantity = sum(sale.total_quantity for sale in active_sales)

        total_profit = 0.0
        sale_item_details = []
        for sale in active_sales:
            for item in sale.sale_items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                unit_price = product.unit_price if product else 0.0
                item_profit = (item.sale_price - unit_price) * item.quantity
                total_profit += item_profit

                sale_item_details.append({
                    "product_name": item.product_name,
                    "size": item.size,
                    "quantity": item.quantity,
                    "unit_price": unit_price,
                    "sale_price": item.sale_price,
                    "profit_loss": item_profit
                })

        status_breakdown = {}
        for sale in sales:
            status = sale.status.value if hasattr(sale.status, 'value') else str(sale.status)
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

        return {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_quantity": total_quantity,
            "total_profit": total_profit,
            "status_breakdown": status_breakdown,
            "sale_item_details": sale_item_details
        }

    def _query_sales(self, db: Session, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Query sales with optional date filters."""
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

        return query.all()

    def get_sales_report(self, db: Session, start_date: Optional[str] = None, end_date: Optional[str] = None) -> SalesReportResponse:
        sales = self._query_sales(db, start_date, end_date)
        summary = self._calculate_summary(db, sales)

        return SalesReportResponse(
            sales=sales,
            total_sales=summary["total_sales"],
            status_breakdown=summary["status_breakdown"],
            total_quantity=summary["total_quantity"],
            total_revenue=summary["total_revenue"],
            total_profit=summary["total_profit"],
            sale_item_details=summary["sale_item_details"]
        )

    def compare_sales_reports(
        self, db: Session,
        p1_start: str, p1_end: str,
        p2_start: str, p2_end: str,
        period: str
    ) -> SalesComparisonResponse:
        sales_1 = self._query_sales(db, p1_start, p1_end)
        sales_2 = self._query_sales(db, p2_start, p2_end)

        summary_1 = self._calculate_summary(db, sales_1)
        summary_2 = self._calculate_summary(db, sales_2)

        period_1 = SalesReportSummary(
            period_label=f"{period.capitalize()} starting {p1_start}",
            start_date=p1_start,
            end_date=p1_end,
            **summary_1
        )
        period_2 = SalesReportSummary(
            period_label=f"{period.capitalize()} starting {p2_start}",
            start_date=p2_start,
            end_date=p2_end,
            **summary_2
        )

        def pct_change(old: float, new: float) -> Optional[float]:
            if old == 0:
                return None
            return round(((new - old) / abs(old)) * 100, 2)

        difference = SalesComparisonDifference(
            total_sales=summary_2["total_sales"] - summary_1["total_sales"],
            total_quantity=summary_2["total_quantity"] - summary_1["total_quantity"],
            total_revenue=round(summary_2["total_revenue"] - summary_1["total_revenue"], 2),
            total_profit=round(summary_2["total_profit"] - summary_1["total_profit"], 2),
            total_sales_pct_change=pct_change(summary_1["total_sales"], summary_2["total_sales"]),
            total_revenue_pct_change=pct_change(summary_1["total_revenue"], summary_2["total_revenue"]),
            total_profit_pct_change=pct_change(summary_1["total_profit"], summary_2["total_profit"]),
        )

        return SalesComparisonResponse(
            period_1=period_1,
            period_2=period_2,
            difference=difference
        )
