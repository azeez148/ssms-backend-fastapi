# Frontend Integration Guide for Optimized Product Retrieval

To resolve the high latency and large response sizes observed in the product listing pages, the backend has been updated with two main optimization strategies. Frontend changes are required to leverage these improvements.

## 1. Implementation of Pagination

The standard `/products/all` endpoint now supports optional pagination parameters. It is highly recommended to update the product list view to fetch data in chunks rather than loading the entire catalog at once.

### API Changes
- **Endpoint:** `GET /products/all`
- **New Query Parameters:**
  - `skip` (integer, default: 0): The number of items to skip.
  - `limit` (integer, optional): The maximum number of items to return.

### Recommended Frontend Changes
- **Implement Infinite Scroll or Pagination UI:** Instead of calling `/products/all` without parameters, the frontend should manage a page state and request a specific number of products (e.g., `limit=50`).
- **Update API Service:** Modify the product service in the frontend to include these optional parameters in the request.

---

## 2. Adoption of the Minimal Product Endpoint

For views that only require a summary of product information (such as search results, grid views, or simple lists), a new minimal endpoint has been provided. This endpoint significantly reduces serialization time and payload size by omitting heavy nested relationships and metadata.

### API Changes
- **Endpoint:** `GET /products/all-minimal`
- **Response Schema:** `ProductMinimalResponse`
  - Includes essential fields: `id`, `name`, `description`, `unit_price`, `selling_price`, `category_id`, `is_active`, `can_listed`, `image_url`, `discounted_price`.
  - Includes minimal nested data: `category_name`, and a list of `shops` containing only `id`, `name`, and `shop_code`.
  - **Does NOT include:** full `Category` object, `tags`, `size_map`, or audit fields (`created_date`, etc.).

### Recommended Frontend Changes
- **Switch to Minimal Fetch for Listing Views:** Update the main product grid or list components to call `/products/all-minimal` instead of the full `/products/all`.
- **Lazy Load Details:** Only call the full product detail endpoint (or the original `/all` with a filter) when the user navigates to a specific product's detail page or opens a "Quick View" that requires sizes and tags.

---

## Performance Impact Summary
Based on internal benchmarks with 3,000 products:
- **Payload Size:** Reduced from **3.56 MB** to **2.02 MB** (~40% reduction).
- **Latency:** Total processing time reduced by ~50% due to optimized serialization and reduced DB eager loading.
