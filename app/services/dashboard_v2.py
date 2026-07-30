from datetime import date, timedelta
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session, joinedload

from app.models.sale import Sale, SaleItem
from app.models.shop import Shop
from app.schemas.dashboard_v2 import (
    DashboardV2Response, KpiStats, BranchData, CategorySplit,
    Transaction, TopProduct, TrafficHeatmap
)
from app.schemas.enums import SaleStatus

ACTIVE_STATUSES = {SaleStatus.COMPLETED, SaleStatus.SHIPPED}

# Store Performance Index is a composite score (0–10) computed externally
# and supplied here as a fixed value until a dynamic calculation is integrated.
STORE_PERFORMANCE_INDEX = 8.4

FOOTWEAR_KEYWORDS = {"footwear", "shoe", "shoes", "sneaker", "sneakers", "boot", "boots", "sandal", "sandals"}
APPAREL_KEYWORDS = {"apparel", "clothing", "clothes", "shirt", "jersey", "shorts", "pants", "jacket", "hoodie", "top", "wear"}

DAY_MAP = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}


def _classify_category(category: str) -> str:
    """Classify a product category string into footwear, apparel, or other."""
    lower = (category or "").lower()
    for kw in FOOTWEAR_KEYWORDS:
        if kw in lower:
            return "footwear"
    for kw in APPAREL_KEYWORDS:
        if kw in lower:
            return "apparel"
    return "other"


def _get_period_bounds(view: str) -> Tuple[str, str, str, str]:
    """Return (current_start, current_end, prev_start, prev_end) as ISO date strings."""
    today = date.today()

    if view == "daily":
        current_start = today.isoformat()
        current_end = today.isoformat()
        prev_day = today - timedelta(days=1)
        prev_start = prev_day.isoformat()
        prev_end = prev_day.isoformat()

    elif view == "monthly":
        current_start = today.replace(day=1).isoformat()
        # Last day of current month
        next_month = today.replace(day=28) + timedelta(days=4)
        current_end = (next_month - timedelta(days=next_month.day)).isoformat()
        # Previous month
        first_of_current = today.replace(day=1)
        prev_month_end = first_of_current - timedelta(days=1)
        prev_start = prev_month_end.replace(day=1).isoformat()
        prev_end = prev_month_end.isoformat()

    else:  # yearly
        current_start = date(today.year, 1, 1).isoformat()
        current_end = date(today.year, 12, 31).isoformat()
        prev_start = date(today.year - 1, 1, 1).isoformat()
        prev_end = date(today.year - 1, 12, 31).isoformat()

    return current_start, current_end, prev_start, prev_end


def _query_sales_in_period(db: Session, start: str, end: str) -> List[Sale]:
    """Fetch all sales within the given date range, eagerly loading relationships."""
    return (
        db.query(Sale)
        .options(
            joinedload(Sale.customer),
            joinedload(Sale.sale_items),
            joinedload(Sale.shop),
        )
        .filter(Sale.date >= start, Sale.date <= end)
        .all()
    )


def _total_revenue(sales: List[Sale]) -> float:
    return sum(
        s.total_price for s in sales if s.status in ACTIVE_STATUSES
    )


def _traffic(sales: List[Sale]) -> int:
    return sum(1 for s in sales if s.status in ACTIVE_STATUSES)


def _compute_growth(current_rev: float, prev_rev: float) -> float:
    if prev_rev == 0:
        return 0.0
    return round(((current_rev - prev_rev) / prev_rev) * 100, 1)


def _build_branch_data(db: Session, sales: List[Sale]) -> List[BranchData]:
    """Group sales by shop and build branch data objects."""
    shop_sales: Dict[int, List[Sale]] = {}
    for sale in sales:
        if sale.shop_id is not None:
            shop_sales.setdefault(sale.shop_id, []).append(sale)

    # Fetch all relevant shops in one query
    shop_ids = list(shop_sales.keys())
    shops: Dict[int, Shop] = {}
    if shop_ids:
        for shop in db.query(Shop).filter(Shop.id.in_(shop_ids)).all():
            shops[shop.id] = shop

    branches: List[BranchData] = []
    for idx, (shop_id, s_list) in enumerate(shop_sales.items(), start=1):
        shop = shops.get(shop_id)
        shop_name = shop.name if shop else f"Branch {shop_id}"
        shop_code = (shop.shop_code or f"BR-{idx:02d}") if shop else f"BR-{idx:02d}"

        active_sales = [s for s in s_list if s.status in ACTIVE_STATUSES]
        branch_revenue = sum(s.total_price for s in active_sales)

        # Category split
        category_totals = {"footwear": 0.0, "apparel": 0.0, "other": 0.0}
        for sale in active_sales:
            for item in sale.sale_items:
                bucket = _classify_category(item.product_category)
                category_totals[bucket] += item.total_price

        total_cat = sum(category_totals.values()) or 1.0
        split = CategorySplit(
            footwear=round(category_totals["footwear"] / total_cat * 100, 1),
            apparel=round(category_totals["apparel"] / total_cat * 100, 1),
            other=round(category_totals["other"] / total_cat * 100, 1),
        )

        # Recent transactions (last 5 active sales, sorted descending by date)
        sorted_sales = sorted(active_sales, key=lambda s: s.date or "", reverse=True)[:5]
        transactions: List[Transaction] = []
        for sale in sorted_sales:
            customer_name = "Unknown"
            if sale.customer:
                customer_name = getattr(sale.customer, "name", "Unknown") or "Unknown"

            first_item = sale.sale_items[0] if sale.sale_items else None
            item_name = first_item.product_name if first_item else "-"

            status_val = sale.status.value if hasattr(sale.status, "value") else str(sale.status)
            display_status = "Returned" if status_val == SaleStatus.RETURNED.value else "Completed"

            transactions.append(Transaction(
                id=f"#{sale.id:05d}",
                customer=customer_name,
                item=item_name,
                amount=sale.total_price,
                time=sale.date or "",
                status=display_status,
            ))

        branches.append(BranchData(
            id=shop_code,
            name=shop_name,
            sales=branch_revenue,
            split=split,
            recent_transactions=transactions,
        ))

    return branches


def _build_top_products(sales: List[Sale], top_n: int = 5) -> List[TopProduct]:
    """Aggregate sale items and return the top N products by units sold."""
    product_units: Dict[str, int] = {}
    for sale in sales:
        if sale.status not in ACTIVE_STATUSES:
            continue
        for item in sale.sale_items:
            product_units[item.product_name] = product_units.get(item.product_name, 0) + item.quantity

    sorted_products = sorted(product_units.items(), key=lambda x: x[1], reverse=True)
    return [TopProduct(name=name, units=units) for name, units in sorted_products[:top_n]]


def _build_traffic_heatmap(sales: List[Sale]) -> TrafficHeatmap:
    """Count active sales per day of week."""
    day_counts = {day: 0 for day in DAY_MAP.values()}
    for sale in sales:
        if sale.status not in ACTIVE_STATUSES:
            continue
        try:
            sale_date = date.fromisoformat(sale.date)
            day_name = DAY_MAP[sale_date.weekday()]
            day_counts[day_name] += 1
        except (ValueError, TypeError):
            pass
    return TrafficHeatmap(**day_counts)


class DashboardV2Service:
    def get_dashboard_data(self, db: Session, view: str) -> DashboardV2Response:
        current_start, current_end, prev_start, prev_end = _get_period_bounds(view)

        current_sales = _query_sales_in_period(db, current_start, current_end)
        prev_sales = _query_sales_in_period(db, prev_start, prev_end)

        curr_revenue = _total_revenue(current_sales)
        prev_revenue = _total_revenue(prev_sales)
        curr_traffic = _traffic(current_sales)

        avg_ticket = round(curr_revenue / curr_traffic, 2) if curr_traffic else 0.0

        kpi = KpiStats(
            total_revenue=curr_revenue,
            growth=_compute_growth(curr_revenue, prev_revenue),
            traffic=curr_traffic,
            avg_ticket_size=avg_ticket,
            store_performance_index=STORE_PERFORMANCE_INDEX,
        )

        branch_data = _build_branch_data(db, current_sales)
        top_products = _build_top_products(current_sales)
        heatmap = _build_traffic_heatmap(current_sales)

        return DashboardV2Response(
            view=view,
            kpi_stats=kpi,
            branch_data=branch_data,
            top_products=top_products,
            traffic_heatmap=heatmap,
        )
