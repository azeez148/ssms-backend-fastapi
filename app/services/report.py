from datetime import date, timedelta
from sqlalchemy.orm import Session, joinedload
from app.models.sale import Sale
from app.models.product import Product
from app.schemas.report import (
    SalesReportResponse, SalesComparisonResponse,
    SalesReportSummary, SalesComparisonDifference,
    SalesPerformanceResponse,
    SalesPerformanceSummary,
    DailySalesPerformance,
    SalesPerformanceItemDetail,
    ShopPerformanceSummary,
    StatusBreakdownItem,
)
from app.schemas.enums import SaleStatus
from typing import Optional

class ReportService:
    @staticmethod
    def _normalized_date(value: str) -> str:
        """Normalize sale date strings to YYYY-MM-DD."""
        return (value or "")[:10]

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

    def get_detailed_sales_performance(
        self,
        db: Session,
        start_date: str,
        end_date: str,
    ) -> SalesPerformanceResponse:
        start_dt = date.fromisoformat(start_date)
        end_dt = date.fromisoformat(end_date)
        end_exclusive = (end_dt + timedelta(days=1)).isoformat()

        all_sales = (
            db.query(Sale)
            .options(joinedload(Sale.sale_items), joinedload(Sale.shop))
            .filter(Sale.date >= start_dt.isoformat())
            .filter(Sale.date < end_exclusive)
            .all()
        )

        status_breakdown_map = {}
        for sale in all_sales:
            status = sale.status.value if hasattr(sale.status, "value") else str(sale.status)
            status_breakdown_map[status] = status_breakdown_map.get(status, 0) + 1

        included_statuses = {SaleStatus.COMPLETED, SaleStatus.SHIPPED}
        included_sales = [sale for sale in all_sales if sale.status in included_statuses]

        product_ids = {
            item.product_id
            for sale in included_sales
            for item in sale.sale_items
            if item.product_id is not None
        }
        products = db.query(Product.id, Product.unit_price).filter(Product.id.in_(product_ids)).all() if product_ids else []
        product_unit_price_map = {product_id: float(unit_price or 0.0) for product_id, unit_price in products}

        daily_map = {}
        shop_map = {}
        total_revenue = 0.0
        total_profit = 0.0
        total_items = 0

        for sale in included_sales:
            day_key = self._normalized_date(sale.date)
            if day_key not in daily_map:
                daily_map[day_key] = {
                    "date": day_key,
                    "no_of_orders": 0,
                    "no_of_items": 0,
                    "total_revenue": 0.0,
                    "total_profit_loss": 0.0,
                    "sale_items": [],
                }

            day_entry = daily_map[day_key]
            day_entry["no_of_orders"] += 1
            day_entry["total_revenue"] += float(sale.total_price or 0.0)

            sale_item_qty_total = 0
            sale_profit = 0.0

            for item in sale.sale_items:
                quantity = int(item.quantity or 0)
                sale_item_qty_total += quantity

                unit_price = float(product_unit_price_map.get(item.product_id, 0.0))
                sale_price = float(item.sale_price or 0.0)
                revenue = float(item.total_price or (sale_price * quantity))
                profit_loss = quantity * (sale_price - unit_price)
                sale_profit += profit_loss

                day_entry["sale_items"].append(
                    {
                        "item_name": item.product_name,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "sale_price": sale_price,
                        "revenue": revenue,
                        "profit_loss": profit_loss,
                    }
                )

                shop_key = sale.shop_id
                if shop_key not in shop_map:
                    shop_map[shop_key] = {
                        "shop_name": sale.shop.name if sale.shop else "Unknown",
                        "shop_code": sale.shop.shop_code if sale.shop else None,
                        "revenue": 0.0,
                        "profit": 0.0,
                        "sale_items": [],
                        "daily_map": {},
                    }
                shop_map[shop_key]["profit"] += profit_loss
                shop_map[shop_key]["sale_items"].append(
                    {
                        "item_name": item.product_name,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "sale_price": sale_price,
                        "revenue": revenue,
                        "profit_loss": profit_loss,
                    }
                )

                if day_key not in shop_map[shop_key]["daily_map"]:
                    shop_map[shop_key]["daily_map"][day_key] = {
                        "date": day_key,
                        "no_of_orders": 0,
                        "no_of_items": 0,
                        "total_revenue": 0.0,
                        "total_profit_loss": 0.0,
                        "sale_items": [],
                    }

                shop_map[shop_key]["daily_map"][day_key]["no_of_items"] += quantity
                shop_map[shop_key]["daily_map"][day_key]["total_profit_loss"] += profit_loss
                shop_map[shop_key]["daily_map"][day_key]["sale_items"].append(
                    {
                        "item_name": item.product_name,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "sale_price": sale_price,
                        "revenue": revenue,
                        "profit_loss": profit_loss,
                    }
                )

            day_entry["no_of_items"] += sale_item_qty_total
            day_entry["total_profit_loss"] += sale_profit

            total_items += sale_item_qty_total
            total_revenue += float(sale.total_price or 0.0)
            total_profit += sale_profit

            shop_key = sale.shop_id
            if shop_key not in shop_map:
                shop_map[shop_key] = {
                    "shop_name": sale.shop.name if sale.shop else "Unknown",
                    "shop_code": sale.shop.shop_code if sale.shop else None,
                    "revenue": 0.0,
                    "profit": 0.0,
                    "sale_items": [],
                    "daily_map": {},
                }
            shop_map[shop_key]["revenue"] += float(sale.total_price or 0.0)

            if day_key not in shop_map[shop_key]["daily_map"]:
                shop_map[shop_key]["daily_map"][day_key] = {
                    "date": day_key,
                    "no_of_orders": 0,
                    "no_of_items": 0,
                    "total_revenue": 0.0,
                    "total_profit_loss": 0.0,
                    "sale_items": [],
                }
            shop_map[shop_key]["daily_map"][day_key]["no_of_orders"] += 1
            shop_map[shop_key]["daily_map"][day_key]["total_revenue"] += float(sale.total_price or 0.0)

        daily_performance = [
            DailySalesPerformance(
                date=entry["date"],
                no_of_orders=entry["no_of_orders"],
                no_of_items=entry["no_of_items"],
                total_revenue=round(entry["total_revenue"], 2),
                total_profit_loss=round(entry["total_profit_loss"], 2),
                sale_items=[
                    SalesPerformanceItemDetail(
                        item_name=item["item_name"],
                        quantity=item["quantity"],
                        unit_price=round(item["unit_price"], 2),
                        sale_price=round(item["sale_price"], 2),
                        revenue=round(item["revenue"], 2),
                        profit_loss=round(item["profit_loss"], 2),
                    )
                    for item in entry["sale_items"]
                ],
            )
            for entry in sorted(daily_map.values(), key=lambda x: x["date"])
        ]

        shop_wise_performance = [
            ShopPerformanceSummary(
                shop_name=entry["shop_name"],
                shop_code=entry["shop_code"],
                revenue=round(entry["revenue"], 2),
                profit=round(entry["profit"], 2),
                sale_items=[
                    SalesPerformanceItemDetail(
                        item_name=item["item_name"],
                        quantity=item["quantity"],
                        unit_price=round(item["unit_price"], 2),
                        sale_price=round(item["sale_price"], 2),
                        revenue=round(item["revenue"], 2),
                        profit_loss=round(item["profit_loss"], 2),
                    )
                    for item in entry["sale_items"]
                ],
                daily_performance=[
                    DailySalesPerformance(
                        date=shop_day_entry["date"],
                        no_of_orders=shop_day_entry["no_of_orders"],
                        no_of_items=shop_day_entry["no_of_items"],
                        total_revenue=round(shop_day_entry["total_revenue"], 2),
                        total_profit_loss=round(shop_day_entry["total_profit_loss"], 2),
                        sale_items=[
                            SalesPerformanceItemDetail(
                                item_name=item["item_name"],
                                quantity=item["quantity"],
                                unit_price=round(item["unit_price"], 2),
                                sale_price=round(item["sale_price"], 2),
                                revenue=round(item["revenue"], 2),
                                profit_loss=round(item["profit_loss"], 2),
                            )
                            for item in shop_day_entry["sale_items"]
                        ],
                    )
                    for shop_day_entry in sorted(entry["daily_map"].values(), key=lambda x: x["date"])
                ],
            )
            for entry in sorted(shop_map.values(), key=lambda x: x["shop_name"])
        ]

        status_breakdown = [
            StatusBreakdownItem(status=status, count=count)
            for status, count in sorted(status_breakdown_map.items(), key=lambda item: item[0])
        ]

        return SalesPerformanceResponse(
            start_date=start_dt.isoformat(),
            end_date=end_dt.isoformat(),
            daily_performance=daily_performance,
            summary=SalesPerformanceSummary(
                total_sales=len(included_sales),
                total_revenue=round(total_revenue, 2),
                total_items=total_items,
                total_profit=round(total_profit, 2),
            ),
            shop_wise_performance=shop_wise_performance,
            status_breakdown=status_breakdown,
        )
