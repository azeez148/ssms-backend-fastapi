# Pricelist API Documentation

The Pricelist API allows managing unit prices, selling prices, and discounted prices for product categories.

## Base URL
`/pricelists`

## Endpoints

### 1. List All Pricelists
- **URL:** `/pricelists/`
- **Method:** `GET`
- **Response:** `List[PricelistResponse]`

### 2. Create Pricelist
- **URL:** `/pricelists/`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "category_id": 1,
    "unit_price": 100,
    "selling_price": 150,
    "discounted_price": 120
  }
  ```
- **Response:** `PricelistResponse`
- **Errors:** `400 Bad Request` if a pricelist already exists for the given category.

### 3. Get Pricelist by ID
- **URL:** `/pricelists/{pricelist_id}`
- **Method:** `GET`
- **Response:** `PricelistResponse`

### 4. Get Pricelist by Category ID
- **URL:** `/pricelists/category/{category_id}`
- **Method:** `GET`
- **Response:** `PricelistResponse`

### 5. Update Pricelist
- **URL:** `/pricelists/{pricelist_id}`
- **Method:** `PUT`
- **Request Body:** (All fields are optional)
  ```json
  {
    "unit_price": 110,
    "selling_price": 160,
    "discounted_price": 130
  }
  ```
- **Response:** `PricelistResponse`

### 6. Delete Pricelist
- **URL:** `/pricelists/{pricelist_id}`
- **Method:** `DELETE`
- **Response:**
  ```json
  {
    "message": "Pricelist deleted successfully"
  }
  ```

## Data Models

### PricelistResponse
```json
{
  "id": 1,
  "category_id": 1,
  "unit_price": 100,
  "selling_price": 150,
  "discounted_price": 120,
  "created_date": "2023-10-27T10:00:00",
  "updated_date": "2023-10-27T10:00:00",
  "created_by": "system",
  "updated_by": "system"
}
```
