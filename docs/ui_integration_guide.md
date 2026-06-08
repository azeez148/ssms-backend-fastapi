# UI Integration Guide: Server-Side Product Filtering & Sorting

This document provides instructions for frontend developers on how to transition from local product filtering to server-side filtering using the updated Product API.

## Updated Endpoints

The following endpoints have been updated to support advanced filtering and sorting:

- `GET /api/products/all`
- `GET /api/products/all-minimal`

## Query Parameters

You can now pass the following optional query parameters to these endpoints:

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `category_id` | Integer | Filter by category ID. |
| `shop_id` | Integer | Filter by shop ID. |
| `search` | String | Search in product name and description. |
| `has_image` | Boolean | `true` for products with images, `false` for products without. |
| `is_in_stock` | Boolean | `true` for products with quantity > 0 in any size, `false` for out of stock. |
| `has_offer` | Boolean | `true` for products with an active offer, `false` for those without. |
| `tag_id` | Integer | Filter by a specific tag ID. |
| `sort_by` | String | `newest` (default, sorts by ID DESC) or `oldest` (sorts by ID ASC). |
| `skip` | Integer | Number of items to skip (for pagination). |
| `limit` | Integer | Number of items to return (for pagination). |

## Integration Steps

### 1. Update `loadProducts()`

Modify your `loadProducts()` (or equivalent) method to include these new parameters when making the API call.

```typescript
loadProducts() {
  const params: any = {
    skip: (this.p - 1) * this.pageSize,
    limit: this.pageSize,
    sort_by: this.sortBy === 'newest' ? 'newest' : 'oldest'
  };

  if (this.selectedCategoryId !== 'all') params.category_id = this.selectedCategoryId;
  if (this.selectedShopId !== 'all') params.shop_id = this.selectedShopId;
  if (this.filterValue) params.search = this.filterValue;

  if (this.selectedImageStatus === 'uploaded') params.has_image = true;
  else if (this.selectedImageStatus === 'missing') params.has_image = false;

  if (this.selectedStockStatus === 'in-stock') params.is_in_stock = true;
  else if (this.selectedStockStatus === 'out-of-stock') params.is_in_stock = false;

  if (this.selectedOfferStatus === 'in-offer') params.has_offer = true;
  else if (this.selectedOfferStatus === 'no-offer') params.has_offer = false;

  if (this.selectedTagId !== 'all') params.tag_id = this.selectedTagId;

  this.productService.getAllProductsMinimal(params).subscribe(response => {
    this.products = response.items;
    this.totalProducts = response.total;
  });
}
```

### 2. Update Filter Handlers

Update your filter event handlers to trigger a reload from the server instead of calling `applyFilters()` locally.

```typescript
onFilterByImage(event: any) {
  this.selectedImageStatus = event.target.value;
  this.p = 1; // Reset to first page
  this.loadProducts();
}

onFilterByStockStatus(event: any) {
  this.selectedStockStatus = event.target.value;
  this.p = 1;
  this.loadProducts();
}

// ... repeat for other filters
```

### 3. Remove Local `applyFilters()`

Since the backend now handles filtering, sorting, and pagination, you can simplify or remove your local `applyFilters()` logic that operates on `this.allProducts`.

## Schema Changes

`ProductMinimalResponse` now includes additional fields for convenience:

- `is_in_stock`: Boolean (computed on server based on size quantities)
- `offer_id`: Integer (ID of the associated offer, if any)

Use these fields for UI indicators (e.g., "In Stock" badge) without needing to inspect the `size_map` or other related objects.
