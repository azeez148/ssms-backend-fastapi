# API Pagination and Dashboard Optimization Documentation

This document describes the changes made to the API to support pagination for large datasets and optimizations for the dashboard data.

## 1. Paginated Endpoints

The following endpoints have been updated to return paginated responses:

### GET `/api/sales/all`
Returns a paginated list of all sales.

**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip.
- `limit` (int, default: 100, max: 500): Maximum number of records to return.

**Response Body:**
```json
{
  "items": [
    {
      "id": 1,
      "date": "2023-10-27",
      "total_quantity": 2,
      "total_price": 100.0,
      "status": "COMPLETED",
      ...
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 100
}
```

### GET `/api/customers/all`
Returns a paginated list of all customers.

**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip.
- `limit` (int, default: 100): Maximum number of records to return.

**Response Body:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "John Doe",
      "mobile": "1234567890",
      ...
    }
  ],
  "total": 500,
  "page": 1,
  "per_page": 100
}
```

### GET `/api/products/all`
Returns a paginated list of all products.

**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip.
- `limit` (int, default: 100, max: 500): Maximum number of records to return.
- ... other filters

**Response Body:**
```json
{
  "items": [...],
  "total": 200,
  "page": 1,
  "per_page": 100
}
```

### GET `/api/purchases/all`
Returns a paginated list of all purchases.

**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip.
- `limit` (int, default: 100, max: 500): Maximum number of records to return.

**Response Body:**
```json
{
  "items": [...],
  "total": 80,
  "page": 1,
  "per_page": 100
}
```

## 2. Dashboard Optimization

The dashboard data has been optimized to return only the most relevant information.

### Dashboard Data Structure (`GET /api/dashboard/`)

The following fields now return only the **latest 5 items**:
- `most_sold_items`: Top 5 products by quantity sold.
- `recent_sales`: Latest 5 sales records.
- `recent_purchases`: Latest 5 purchase records.

**Example Response Snippet:**
```json
{
  "total_sales": { ... },
  "total_products": 100,
  "total_categories": 10,
  "most_sold_items": {
    "1": { "product_name": "Product A", "total_quantity": 50, ... },
    ... (up to 5 items)
  },
  "recent_sales": [ ... (up to 5 items) ],
  "total_purchases": { ... },
  "recent_purchases": [ ... (up to 5 items) ]
}
```

## 3. General Implementation Details

- **Consistency**: All paginated responses follow the same structure: `items`, `total`, `page`, and `per_page`.
- **Default Limits**: Default page size is set to 100 to balance performance and usability.
- **Server-side Sorting**: "Recent" endpoints are sorted by date and ID in descending order to ensure the newest items are always returned first.
