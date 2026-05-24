from calendar import monthrange
from datetime import date, timedelta
from typing import Dict, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.models.sale import Sale
from app.models.shop import Shop
from app.schemas.enums import SaleStatus


class DashboardV2Service:
    INCLUDED_STATUSES = {SaleStatus.COMPLETED, SaleStatus.SHIPPED}

    @staticmethod
    def _parse_iso_date(value: str) -> date:
        return date.fromisoformat((value or "")[:10])

    def _resolve_period_range(
        self,
        period: str,
        anchor_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Tuple[date, date]:
        period_key = (period or "").lower()
        base_date = self._parse_iso_date(anchor_date) if anchor_date else date.today()

        if period_key == "custom":
            if not start_date or not end_date:
                raise ValueError("Both 'start_date' and 'end_date' are required for custom period.")
            start_dt = self._parse_iso_date(start_date)
            end_dt = self._parse_iso_date(end_date)
            if start_dt > end_dt:
                raise ValueError("'start_date' cannot be greater than 'end_date'.")
            return start_dt, end_dt

        if start_date or end_date:
            raise ValueError("Use 'start_date' and 'end_date' only when period is 'custom'.")

        if period_key == "daily":
            return base_date, base_date
        if period_key == "weekly":
            start_dt = base_date - timedelta(days=base_date.weekday())
            return start_dt, start_dt + timedelta(days=6)
        if period_key == "monthly":
            start_dt = base_date.replace(day=1)
            end_day = monthrange(base_date.year, base_date.month)[1]
            return start_dt, base_date.replace(day=end_day)
        if period_key == "yearly":
            return base_date.replace(month=1, day=1), base_date.replace(month=12, day=31)

        raise ValueError("Invalid period. Supported values: daily, weekly, monthly, yearly, custom.")

    def get_dashboard_performance(
        self,
        db: Session,
        period: str,
        shop_id: Optional[int] = None,
        anchor_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sold_items_limit: int = 5,
    ) -> Dict:
        start_dt, end_dt = self._resolve_period_range(
            period=period,
            anchor_date=anchor_date,
            start_date=start_date,
            end_date=end_date,
        )

        shop_name = "All Shops"
        if shop_id is not None:
            shop = db.query(Shop).filter(Shop.id == shop_id).first()
            if not shop:
                raise LookupError(f"Shop with id {shop_id} not found.")
            shop_name = shop.name

        product_query = db.query(Product).options(joinedload(Product.size_map))
        if shop_id is not None:
            product_query = product_query.filter(Product.shops.any(Shop.id == shop_id))
        products = product_query.all()

        total_in_stock_value = 0.0
        expected_sales_value = 0.0
        expected_profit_loss = 0.0
        in_stock_product_ids = set()
        out_of_stock_product_ids = set()
        in_stock_units = 0
        out_of_stock_units = 0

        for product in products:
            unit_price = float(product.unit_price or 0.0)
            selling_price = float(product.selling_price or 0.0)

            for size in product.size_map:
                quantity = int(size.quantity or 0)
                variant_in_stock_value = quantity * unit_price
                variant_expected_sales = quantity * selling_price
                variant_expected_profit = quantity * (selling_price - unit_price)

                total_in_stock_value += variant_in_stock_value
                expected_sales_value += variant_expected_sales
                expected_profit_loss += variant_expected_profit

                if quantity > 0:
                    in_stock_product_ids.add(product.id)
                    in_stock_units += quantity
                else:
                    out_of_stock_product_ids.add(product.id)
                    out_of_stock_units += 1

        sales_query = (
            db.query(Sale)
            .options(joinedload(Sale.sale_items))
            .filter(Sale.date >= start_dt.isoformat())
            .filter(Sale.date <= end_dt.isoformat())
        )
        if shop_id is not None:
            sales_query = sales_query.filter(Sale.shop_id == shop_id)
        sales = sales_query.all()

        filtered_sales = [sale for sale in sales if sale.status in self.INCLUDED_STATUSES]
        current_sales = sum(float(sale.total_price or 0.0) for sale in filtered_sales)

        sold_items_map: Dict[str, Dict] = {}
        sale_product_ids = set()
        for sale in filtered_sales:
            for item in sale.sale_items:
                sale_product_ids.add(item.product_id)
                key = f"{item.product_id}:{item.product_name}"
                if key not in sold_items_map:
                    sold_items_map[key] = {
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "total_quantity": 0,
                        "total_revenue": 0.0,
                        "total_profit_loss": 0.0,
                    }
                sold_items_map[key]["total_quantity"] += int(item.quantity or 0)
                sold_items_map[key]["total_revenue"] += float(item.total_price or 0.0)

        unit_prices = (
            db.query(Product.id, Product.unit_price)
            .filter(Product.id.in_(sale_product_ids))
            .all()
            if sale_product_ids
            else []
        )
        unit_price_map = {product_id: float(unit_price or 0.0) for product_id, unit_price in unit_prices}

        current_profit_loss = 0.0
        for sale in filtered_sales:
            for item in sale.sale_items:
                quantity = int(item.quantity or 0)
                sale_price = float(item.sale_price or 0.0)
                item_profit = quantity * (sale_price - unit_price_map.get(item.product_id, 0.0))
                current_profit_loss += item_profit
                key = f"{item.product_id}:{item.product_name}"
                sold_items_map[key]["total_profit_loss"] += item_profit

        sold_items = list(sold_items_map.values())
        sold_items_sorted_desc = sorted(
            sold_items,
            key=lambda x: (x["total_quantity"], x["total_revenue"]),
            reverse=True,
        )
        sold_items_sorted_asc = sorted(
            sold_items,
            key=lambda x: (x["total_quantity"], x["total_revenue"]),
        )

        return {
            "context": {
                "period": period.lower(),
                "start_date": start_dt.isoformat(),
                "end_date": end_dt.isoformat(),
                "shop_id": shop_id,
                "shop_name": shop_name,
            },
            "metrics": {
                "in_stock_summary": {
                    "product_count": len(in_stock_product_ids),
                    "total_units": in_stock_units,
                    "total_value": round(total_in_stock_value, 2),
                },
                "out_of_stock_summary": {
                    "product_count": len(out_of_stock_product_ids),
                    "total_units": out_of_stock_units,
                    "total_value": 0.0,
                },
                "most_sold_items": [
                    {
                        "product_id": item["product_id"],
                        "product_name": item["product_name"],
                        "total_quantity": item["total_quantity"],
                        "total_revenue": round(item["total_revenue"], 2),
                        "total_profit_loss": round(item["total_profit_loss"], 2),
                    }
                    for item in sold_items_sorted_desc[:sold_items_limit]
                ],
                "least_sold_items": [
                    {
                        "product_id": item["product_id"],
                        "product_name": item["product_name"],
                        "total_quantity": item["total_quantity"],
                        "total_revenue": round(item["total_revenue"], 2),
                        "total_profit_loss": round(item["total_profit_loss"], 2),
                    }
                    for item in sold_items_sorted_asc[:sold_items_limit]
                ],
                "total_in_stock_value": round(total_in_stock_value, 2),
                "expected_sales_value": round(expected_sales_value, 2),
                "expected_profit_loss": round(expected_profit_loss, 2),
                "current_sales": round(current_sales, 2),
                "current_profit_loss": round(current_profit_loss, 2),
            },
        }
