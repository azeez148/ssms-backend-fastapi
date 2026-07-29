# Public Home API Documentation

These endpoints are available under the `/public` prefix and are intended for public access on the home page.

## Endpoints

### 1. Get Categories
Returns a list of all product categories.

* **URL**: `/public/categories`
* **Method**: `GET`
* **Response Body**: `List[CategoryResponse]`

### 2. Search Products
Search for products by name or description.

* **URL**: `/public/search`
* **Method**: `GET`
* **Query Parameters**:
    * `search` (string, required): The search string.
* **Response Body**: `List[ProductResponse]`

### 3. Get New Arrivals
Returns the latest 20 products added to the system, ordered by creation date descending.

* **URL**: `/public/new-arrivals`
* **Method**: `GET`
* **Response Body**: `List[ProductResponse]`

### 4. Get Offer Products
Returns products that have an associated active offer.

* **URL**: `/public/offer-products`
* **Method**: `GET`
* **Response Body**: `List[ProductResponse]`

### 5. Get Product By ID
Returns detailed information for a single product.

* **URL**: `/public/products/{product_id}`
* **Method**: `GET`
* **Path Parameters**:
    * `product_id` (integer, required): The ID of the product.
* **Response Body**: `ProductResponse`
