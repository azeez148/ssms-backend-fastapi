# Database Query Performance Report

**Project:** SSMS Backend (FastAPI)  
**Date:** 2026-03-04  
**Scope:** Full analysis of all database queries across service layer  

---

## Executive Summary

This report identifies **10 categories of database performance issues** found across the service layer of this FastAPI application. The most critical issues are N+1 query patterns in reporting and event services, full-table-scan aggregations in the dashboard service, missing composite indexes on frequently-joined columns, and the absence of any connection pool configuration or query caching. These issues will cause increasingly severe slowdowns as data volume grows.

---

## Issue Index

| # | Issue | Severity | Affected File(s) |
|---|-------|----------|-----------------|
| 1 | N+1 queries in `_calculate_summary` | 🔴 Critical | `services/report.py` |
| 2 | Full-table aggregation done in Python | 🔴 Critical | `services/sale.py`, `services/purchase.py`, `services/dashboard.py` |
| 3 | N+1 queries in event offer apply/remove | 🔴 Critical | `services/event.py` |
| 4 | N+1 queries when creating purchases | 🟠 High | `services/purchase.py` |
| 5 | Missing composite indexes on hot columns | 🟠 High | `models/product_size.py`, `models/sale.py` |
| 6 | Dashboard makes 7+ sequential full-table queries | 🟠 High | `services/dashboard.py` |
| 7 | `product_ids` / `category_ids` stored as comma-separated strings | 🟠 High | `models/event.py`, `services/event.py` |
| 8 | No database connection pool configuration | 🟡 Medium | `core/database.py` |
| 9 | Duplicate-check event listeners open extra sessions | 🟡 Medium | `models/customer.py` |
| 10 | No caching for stable reference data | 🟡 Medium | Multiple services |

---

## Detailed Issue Descriptions

---

### Issue 1 — N+1 Queries in `_calculate_summary` (Report Service)

**Severity:** 🔴 Critical  
**File:** `app/services/report.py`, method `_calculate_summary`

#### What is happening

For every `SaleItem` that belongs to any sale in the requested date range, the service fires a **separate SELECT query** to the `products` table:

```python
# report.py – lines inside _calculate_summary
for sale in active_sales:
    for item in sale.sale_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()  # ← 1 query per item
        unit_price = product.unit_price if product else 0.0
        item_profit = (item.sale_price - unit_price) * item.quantity
```

If a date range contains 500 sales with an average of 3 items each, this loop alone fires **1,500 individual product lookups** to compute the report.

#### Root cause

The code fetches sale items eagerly (via `joinedload(Sale.sale_items)`) but then queries `Product` one-by-one in Python instead of joining or bulk-loading product prices.

Note also that `SaleItem.product_id` is **not a foreign key column** in the model (`models/sale.py`), so SQLAlchemy cannot join it automatically.

#### Suggestion to fix

**Option A – Collect all product IDs first, then bulk-load in one query:**

```python
# Collect unique product IDs from all sale items
product_ids = {item.product_id for sale in active_sales for item in sale.sale_items}

# Single query to fetch all required products
products_by_id = {
    p.id: p
    for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
}

# Then use products_by_id[item.product_id] inside the loop — no extra DB hits
```

**Option B – Denormalise `unit_price` into `SaleItem`:**  
Store the `unit_price` at the time of sale directly on `SaleItem`. This eliminates the lookup entirely and also preserves historical accuracy if prices change later.

---

### Issue 2 — Full-Table Aggregation Done in Python

**Severity:** 🔴 Critical  
**Files:** `app/services/sale.py`, `app/services/purchase.py`, `app/services/dashboard.py`

#### What is happening

**`sale.py` – `get_total_sales`:**

```python
def get_total_sales(self, db: Session) -> dict:
    sales = db.query(Sale).all()          # ← loads EVERY row into memory
    return {
        'total_count': len(sales),
        'total_revenue': sum(sale.total_price for sale in sales),
        'total_items_sold': sum(sale.total_quantity for sale in sales)
    }
```

**`sale.py` – `get_most_sold_items`:**

```python
def get_most_sold_items(self, db: Session) -> Dict[int, Dict]:
    sales_items = db.query(SaleItem).all()   # ← loads EVERY sale item into memory
    item_stats = {}
    for item in sales_items:                 # ← aggregation in Python
        ...
```

**`purchase.py` – `get_total_purchases`:**

```python
def get_total_purchases(self, db: Session) -> dict:
    purchases = self.get_all_purchases(db)   # ← loads ALL purchases
    return {
        'total_count': len(purchases),
        'total_cost': sum(purchase.total_price for purchase in purchases),
        ...
    }
```

As records grow (thousands of sales, tens of thousands of sale items), this pattern transfers all data across the network, materialises Python objects for every row, and discards them after counting — a massive waste.

#### Suggestion to fix

Push aggregation to the database using SQL functions:

```python
from sqlalchemy import func

# get_total_sales – one query, no row materialisation
def get_total_sales(self, db: Session) -> dict:
    result = db.query(
        func.count(Sale.id),
        func.coalesce(func.sum(Sale.total_price), 0),
        func.coalesce(func.sum(Sale.total_quantity), 0)
    ).one()
    return {
        'total_count': result[0],
        'total_revenue': result[1],
        'total_items_sold': result[2]
    }

# get_most_sold_items – GROUP BY at the database level
def get_most_sold_items(self, db: Session):
    rows = (
        db.query(
            SaleItem.product_id,
            SaleItem.product_name,
            SaleItem.product_category,
            func.sum(SaleItem.quantity).label("total_quantity"),
            func.sum(SaleItem.total_price).label("total_revenue")
        )
        .group_by(SaleItem.product_id, SaleItem.product_name, SaleItem.product_category)
        .all()
    )
    ...
```

---

### Issue 3 — N+1 Queries in Event Offer Apply / Remove

**Severity:** 🔴 Critical  
**File:** `app/services/event.py`, methods `apply_offer_to_products`, `remove_offer_from_products`, `update_product_offer`

#### What is happening

**`apply_offer_to_products`:**

```python
for product_id in set(product_ids_to_update):
    product = product_service.get_product_by_id(db, product_id)   # ← 1 query per product
    if product:
        ...
        db.add(product)
db.commit()
```

If an offer applies to 200 products, this fires **200 individual SELECT queries** before the update.

**`remove_offer_from_products`:**

```python
for product in products_in_categories:
    product_ids_to_clear.append(product.id)

for product_id in set(product_ids_to_clear):
    product = product_service.get_product_by_id(db, product_id)   # ← 1 query per product
    if product:
        product.offer_id = None
        product.discounted_price = self.find_original_discounted_price(db, product)  # ← 1 more query per product (CategoryDiscount)
```

Two queries per product: one for the product, one for its category discount.

**`update_product_offer`:**  
Same pattern — fetches each `EventOffer` by ID in a loop, fires one query per old offer.

#### Suggestion to fix

Use bulk operations:

```python
# apply_offer_to_products – bulk fetch, then bulk update
products = db.query(Product).filter(Product.id.in_(product_ids_to_update)).all()
for product in products:
    product.offer_id = offer.id
    product.offer_name = offer.name
    ...
db.commit()

# remove_offer_from_products – use a single UPDATE statement
from sqlalchemy import update
db.execute(
    update(Product)
    .where(Product.id.in_(product_ids_to_clear))
    .values(offer_id=None, offer_price=None, offer_name=None)
)
db.commit()
```

---

### Issue 4 — N+1 Queries When Creating Purchases

**Severity:** 🟠 High  
**File:** `app/services/purchase.py`, method `create_purchase`

#### What is happening

```python
for item in purchase.purchase_items:
    product = db.query(Product).filter(Product.id == item.product_id).first()  # ← 1 query per item
    if product:
        product_size = None
        for size in product.size_map:   # ← product.size_map is already joined (lazy="joined"), but iterates in Python
            if size.size == item.size:
                ...
```

For a purchase with 50 line items, this fires 50 individual product queries. Additionally, `product.size_map` uses `lazy="joined"` on the `Product` model, so each product fetch also joins the `product_sizes` table.

#### Suggestion to fix

Pre-fetch all required products in one query:

```python
product_ids = [item.product_id for item in purchase.purchase_items]
products_by_id = {
    p.id: p
    for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
}

for item in purchase.purchase_items:
    product = products_by_id.get(item.product_id)
    if product:
        ...
```

Also consider replacing the Python loop over `product.size_map` with a targeted query:

```python
product_size = db.query(ProductSize).filter(
    ProductSize.product_id == item.product_id,
    ProductSize.size == item.size
).first()
```

---

### Issue 5 — Missing Composite Indexes on Hot Columns

**Severity:** 🟠 High  
**Files:** `app/models/product_size.py`, `app/models/sale.py`

#### What is happening

**`product_sizes` table:**  
The `update_product_stock` method (called every time a sale or purchase is created or cancelled) filters on **both** `product_id` and `size`:

```python
product_size = db.query(ProductSize).filter(
    ProductSize.product_id == product_id,
    ProductSize.size == size
).first()
```

The `ProductSize` model has no index on `(product_id, size)`:

```python
class ProductSize(BaseModel):
    id = Column(Integer, primary_key=True, ...)
    product_id = Column(Integer, ForeignKey("products.id"))   # ← no index
    size = Column(String)                                      # ← no index
```

Without an index, every stock update requires a full scan of `product_sizes` filtered by product.

**`sales` table:**  
`Sale.date` (a `String` column) is used for ORDER BY in `get_recent_sales` and range filters in reports. There is no index on it. `Sale.status` is frequently filtered (e.g., `status != SaleStatus.CANCELLED`) but also has no index.

**`sale_items` table:**  
`SaleItem.product_id` is not a foreign key and has no index, yet it appears in GROUP BY aggregations.

#### Suggestion to fix

Add indexes via Alembic migration (no code change required in service layer):

```python
# In ProductSize model
product_id = Column(Integer, ForeignKey("products.id"), index=True)
# Add a composite unique index
__table_args__ = (
    UniqueConstraint("product_id", "size", name="uq_product_size"),
)

# In Sale model
date = Column(String, index=True)
status = Column(Enum(SaleStatus), ..., index=True)

# In SaleItem model
product_id = Column(Integer, index=True)
```

---

### Issue 6 — Dashboard Makes 7+ Sequential Full-Table Queries

**Severity:** 🟠 High  
**File:** `app/services/dashboard.py`, method `get_dashboard_data`

#### What is happening

```python
def get_dashboard_data(self, db: Session) -> Dict:
    return {
        "total_sales": self.sale_service.get_total_sales(db),        # loads ALL sales
        "total_products": len(self.product_service.get_all_products(db)),  # loads ALL products
        "total_categories": len(self.category_service.get_all_categories(db)),  # loads ALL categories
        "most_sold_items": self.sale_service.get_most_sold_items(db),  # loads ALL sale items
        "recent_sales": self.sale_service.get_recent_sales(db),       # loads 10 sales
        "total_purchases": self.purchase_service.get_total_purchases(db),  # loads ALL purchases
        "recent_purchases": self.purchase_service.get_recent_purchases(db)  # loads 10 purchases
    }
```

Every call to the dashboard endpoint triggers at least **7 database queries**, several of which load entire tables into Python memory (see Issue 2). All are executed **sequentially**. The dashboard endpoint will become unusably slow as data grows.

#### Suggestion to fix

1. Replace full-table loads with SQL aggregate queries (see Issue 2).
2. For counts (`total_products`, `total_categories`), use `db.query(func.count(Product.id)).scalar()` instead of `len(get_all_products(db))`.
3. Consider caching the dashboard response (e.g., 60-second TTL with Redis or in-memory cache) since it does not need to be real-time.

---

### Issue 7 — `product_ids` / `category_ids` Stored as Comma-Separated Strings

**Severity:** 🟠 High  
**Files:** `app/models/event.py`, `app/services/event.py`

#### What is happening

```python
class EventOffer(BaseModel):
    product_ids = Column(String)   # e.g. "1,5,23,47"
    category_ids = Column(String)  # e.g. "2,3"
```

All product/category association logic splits and joins these strings in Python on every read and write:

```python
product_ids_to_update.extend([int(pid) for pid in offer.product_ids.split(',')])
...
new_offer.product_ids = ",".join(current_pids)
```

This pattern:
- Cannot be indexed or efficiently queried in the database.
- Requires loading the entire offer row into Python just to modify one ID.
- Makes it impossible to query "which offers contain product X?" at the SQL level.
- Is error-prone (trailing commas, empty strings, type coercion).

There is also a separate `products` relationship on `EventOffer` (via a proper foreign key on `Product.offer_id`), making this doubly redundant.

#### Suggestion to fix

Replace the comma-separated columns with a proper join table (similar to the existing `shop_products` pattern already used in this project):

```sql
CREATE TABLE offer_products (
    offer_id INTEGER REFERENCES event_offers(id),
    product_id INTEGER REFERENCES products(id),
    PRIMARY KEY (offer_id, product_id)
);

CREATE TABLE offer_categories (
    offer_id INTEGER REFERENCES event_offers(id),
    category_id INTEGER REFERENCES categories(id),
    PRIMARY KEY (offer_id, category_id)
);
```

Then use SQLAlchemy `relationship` with `secondary` — the same approach used for `Shop.products` and `Shop.purchases`.

---

### Issue 8 — No Database Connection Pool Configuration

**Severity:** 🟡 Medium  
**File:** `app/core/database.py`

#### What is happening

```python
engine = create_engine(SQLALCHEMY_DATABASE_URL)
```

No pool parameters are set. SQLAlchemy's default pool configuration (`pool_size=5`, `max_overflow=10`, no `pool_pre_ping`) is used. In production under concurrent load:
- The pool can be exhausted under concurrent requests, causing requests to queue or time out.
- Stale connections (e.g., after a database restart or network hiccup) are not detected until a query fails.

#### Suggestion to fix

```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,          # maintain up to 10 persistent connections
    max_overflow=20,       # allow up to 20 additional temporary connections
    pool_timeout=30,       # raise after 30s if no connection is available
    pool_recycle=1800,     # recycle connections older than 30 minutes
    pool_pre_ping=True,    # test connections before use to detect stale ones
)
```

---

### Issue 9 — Duplicate-Check Event Listeners Open Extra Sessions

**Severity:** 🟡 Medium  
**File:** `app/models/customer.py`

#### What is happening

```python
@event.listens_for(Customer, 'before_insert')
@event.listens_for(Customer, 'before_update')
def before_insert_update_customer(mapper, connection, target):
    if target.mobile:
        Session = sessionmaker(bind=connection)
        session = Session()
        existing_customer = session.query(Customer).filter(...).first()  # ← extra query
        session.close()
    if target.email:
        Session = sessionmaker(bind=connection)
        session = Session()
        existing_customer = session.query(Customer).filter(...).first()  # ← extra query
        session.close()
```

For **every** customer insert or update, this listener:
1. Creates a new `sessionmaker` bound to the connection.
2. Opens a new session.
3. Fires a query to check for duplicate mobile.
4. Closes the session.
5. Repeats steps 1–4 for email.

This adds **2 extra queries per customer write**, plus the overhead of creating and destroying sessions. The checks are also redundant because both `mobile` and `email` columns are already declared with `unique=True` — the database will enforce uniqueness and raise an `IntegrityError` on violation.

#### Suggestion to fix

Remove the event listener entirely and rely on the database's `UNIQUE` constraints. Catch `IntegrityError` in the service layer and return a friendly error message:

```python
from sqlalchemy.exc import IntegrityError

def create_customer(db: Session, customer: CustomerCreate):
    ...
    try:
        db.add(db_customer)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("A customer with this mobile or email already exists.")
```

---

### Issue 10 — No Caching for Stable Reference Data

**Severity:** 🟡 Medium  
**Files:** Multiple services

#### What is happening

Every request re-queries the database for data that almost never changes:

| Data | Query location | Change frequency |
|------|---------------|-----------------|
| Payment types | `day_management.py` (every sale) | Rarely |
| Delivery types | `delivery.py` | Rarely |
| Categories | `category.py`, `dashboard.py` | Rarely |
| Active event offers | `home.py` on every home page load | Infrequently |
| Shop by ID | Multiple services | Rarely |

For example, `update_day_from_sale` fires a `PaymentType` query on **every single sale creation or cancellation**:

```python
def update_day_from_sale(self, db: Session, amount_change: float, payment_type_id: int):
    ...
    payment_type = db.query(PaymentType).filter(PaymentType.id == payment_type_id).first()  # ← every sale
```

#### Suggestion to fix

Add a lightweight in-process cache (e.g., `functools.lru_cache` for process-scoped data, or Redis for distributed deployments):

```python
# Simple in-process cache for payment types (acceptable for a single-process deployment)
from functools import lru_cache

@lru_cache(maxsize=None)
def get_payment_type_by_id(payment_type_id: int, db_session_id: int):
    # Note: lru_cache with a db session requires care; a better approach is
    # to cache at startup and invalidate on write.
    ...
```

For production, use a proper cache (Redis via `fastapi-cache2`) with short TTLs for data that changes occasionally, and invalidate on writes.

---

## Additional Observations

### `get_all_sales` and `get_all_products` — No Pagination

`SaleService.get_all_sales` and `ProductService.get_all_products` return **all rows** with no limit. As data grows these endpoints will transfer increasingly large payloads. Both should accept `skip`/`limit` (offset pagination) or cursor-based pagination.

### `Product.size_map` — Always Eagerly Loaded

```python
# models/product.py
size_map = relationship(ProductSize, ..., lazy="joined")
```

`lazy="joined"` means every product query — even those that do not need sizes — will always JOIN the `product_sizes` table. For endpoints that only need product names, prices, or IDs (e.g., search results, category listings), this adds an unnecessary join.

Consider changing to `lazy="select"` (the default) and using explicit `joinedload` only where sizes are actually needed (e.g., the product detail endpoint).

### `sale.py` — `update_product_stock` Called Inside a Loop, Each With Its Own `db.commit()`

When processing sale items during creation or cancellation, `update_product_stock` is called per item, and each call ends with `db.commit()`. Inside `create_sale` the outer code calls `db.flush()` → items are added → then one final `db.commit()`. However during `cancel_sale` and `update_sale`, `update_product_stock` is called per item, and the service also calls `db.commit()` at the end of the outer method. Multiple commits per request increase round-trip overhead and can leave data in a partially-committed state if an exception occurs mid-loop. All changes within a single request should be committed in one transaction.

### `purchase.py` — Python Loop Over `product.size_map` Instead of a Direct Query

```python
for size in product.size_map:  # Python loop over an already-loaded collection
    if size.size == item.size:
        product_size = size
        break
```

This is correct but relies on `size_map` being fully loaded (which it is due to `lazy="joined"`). Once `lazy` is changed to `select`, this will cause an additional query per item. The direct query in `ProductService.update_product_stock` is the correct approach and already benefits from a potential index.

---

## Summary of Suggested Fixes by Priority

| Priority | Fix | Impact |
|----------|-----|--------|
| 🔴 1 | Replace per-item `Product` lookup in `_calculate_summary` with bulk fetch | Reduces report query count from O(N) to O(1) |
| 🔴 2 | Replace Python aggregations with SQL `COUNT`/`SUM` | Eliminates full-table loads from dashboard and summary endpoints |
| 🔴 3 | Replace per-product loops in `event.py` with bulk fetch + bulk update | Reduces offer-apply query count from O(N) to O(1) |
| 🟠 4 | Add composite index on `(product_id, size)` in `product_sizes` | Eliminates full table scan on every stock update |
| 🟠 5 | Add indexes on `Sale.date` and `Sale.status` | Speeds up all date-range reports and status filters |
| 🟠 6 | Replace comma-separated `product_ids`/`category_ids` with join tables | Enables SQL-level filtering and proper indexing |
| 🟠 7 | Pre-fetch products in `create_purchase` loop | Reduces purchase creation queries from O(N) to O(1) |
| 🟡 8 | Configure connection pool (`pool_size`, `pool_pre_ping`, etc.) | Prevents pool exhaustion and stale connections under load |
| 🟡 9 | Remove redundant customer uniqueness event listeners | Saves 2 queries per customer insert/update |
| 🟡 10 | Cache payment types, delivery types, and categories | Saves repeated lookups for static reference data |

---

*Report generated by automated codebase analysis. No code was modified.*
