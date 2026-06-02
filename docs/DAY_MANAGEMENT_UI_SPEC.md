# Day Management — UI Development Specification

**Base URL:** `/day-management`  
**Auth:** All endpoints require a Bearer token in the `Authorization` header.

---

## Roles

| Role    | Scope                                                  |
|---------|--------------------------------------------------------|
| `admin` | Can see/manage all shops. Must pass `shop_id` where required. |
| `staff` | Scoped to their own shop automatically.                |

---

## Endpoints

### 1. Start Day

**`POST /day-management/startDay`**

Opens a new day for a shop with an opening balance. If a day was already started and ended today, it reopens it. If a day is already active, it returns the active day.

**Request Body**
```json
{
  "opening_balance": 5000.00,
  "shop_id": 1
}
```

| Field             | Type    | Required | Notes                                     |
|------------------|---------|----------|-------------------------------------------|
| `opening_balance` | float   | Yes      | Cash in hand at start of day              |
| `shop_id`         | integer | Yes (admin) / Auto (staff) | Staff gets their shop_id from token |

**Success Response `200`**
```json
{
  "id": 12,
  "shop_id": 1,
  "opening_balance": 5000.00,
  "start_time": "2026-05-11T08:00:00Z",
  "end_time": null,
  "closing_balance": null,
  "total_expense": 0.0,
  "cash_in_hand": 5000.00,
  "cash_in_account": 0.0,
  "total_sales": null,
  "total_cash_sales": null,
  "total_account_sales": null,
  "variance": null,
  "variance_reason": null,
  "expenses": []
}
```

**Error Responses**

| Code | Reason                                              |
|------|-----------------------------------------------------|
| 400  | Active day from a previous date not yet ended       |
| 403  | Staff trying to start day for another shop          |

**UI Behaviour**
- Show "Start Day" button only when `GET /today` returns `day_started: false`.
- After start, redirect to the Day Dashboard.

---

### 2. Add Expense

**`POST /day-management/addExpense`**

Adds an expense to the current active day. Automatically deducts from `cash_in_hand`.

**Request Body**
```json
{
  "description": "Delivery charges",
  "amount": 250.00,
  "shop_id": 1
}
```

| Field         | Type    | Required | Notes                                             |
|--------------|---------|----------|---------------------------------------------------|
| `description` | string  | Yes      |                                                   |
| `amount`      | float   | Yes      |                                                   |
| `shop_id`     | integer | Admin only | Staff's shop inferred from token               |
| `day_id`      | integer | Optional | Admin alternative to `shop_id`                   |

**Success Response `200`**
```json
{
  "id": 5,
  "description": "Delivery charges",
  "amount": 250.00,
  "timestamp": "2026-05-11T10:30:00Z"
}
```

**Error Responses**

| Code | Reason                                         |
|------|------------------------------------------------|
| 400  | No active day found for shop                   |
| 403  | Staff trying to add to another shop's day      |

**UI Behaviour**
- Accessible only when day is active (`day_started: true`, `day_ended: false`).
- Show form with Description and Amount fields.
- Refresh the expenses list after success.

---

### 3. Get Expenses for a Day

**`GET /day-management/expenses/{day_id}`**

Returns the list of all expenses recorded for a specific day.

**Path Parameter:** `day_id` (integer)

**Success Response `200`**
```json
[
  {
    "id": 5,
    "description": "Delivery charges",
    "amount": 250.00,
    "timestamp": "2026-05-11T10:30:00Z"
  }
]
```

**Error Responses**

| Code | Reason                                 |
|------|----------------------------------------|
| 404  | Day not found                          |
| 403  | No access to that shop's day           |

---

### 4. Get Active Day

**`GET /day-management/activeDay?shop_id={id}`**

Returns the currently active (not ended) day for a shop.

**Query Parameter:** `shop_id` — required for admin, ignored for staff.

**Success Response `200`** — same shape as Start Day response.

**Error Responses**

| Code | Reason                           |
|------|----------------------------------|
| 404  | No active day for this shop      |
| 400  | Admin didn't provide `shop_id`   |

**UI Behaviour**
- Call on page load to check if a day is active and get `day_id` for subsequent operations.

---

### 5. End Day

**`POST /day-management/endDay/{day_id}`**

Closes the day. Calculates totals from actual sales and expenses. Variance is automatically computed.

**Path Parameter:** `day_id` (integer)

**Request Body**
```json
{
  "closing_balance": 7500.00,
  "variance_reason": "Short change given to customer"
}
```

| Field              | Type    | Required | Notes                                               |
|-------------------|---------|----------|-----------------------------------------------------|
| `closing_balance`  | float   | Yes      | Actual cash counted by staff at end of day          |
| `variance_reason`  | string  | No       | Required if variance is non-zero (enforce in UI)    |

**How Variance is Calculated (server-side)**

```
expected_cash_in_hand = opening_balance + total_cash_sales - total_expense
variance = closing_balance - expected_cash_in_hand
```

- Positive variance → surplus cash
- Negative variance → cash short

**Success Response `200`** — Full `DaySummary` (see Section 6).

**Error Responses**

| Code | Reason                              |
|------|-------------------------------------|
| 400  | Day already ended                   |
| 404  | Day not found                       |
| 403  | No access to this shop's day        |

**UI Behaviour**
- Show "End Day" button only when `day_started: true` and `day_ended: false`.
- Show closing balance input and optional variance reason textarea.
- If `variance_reason` is blank and the computed variance is non-zero, prompt user to enter a reason before submitting.
- After success, redirect to or display the Day Summary screen.

---

### 6. Get Day Summary

**`GET /day-management/day/{day_id}`**

Returns the full financial summary and status of a specific day.

**Path Parameter:** `day_id` (integer)

**Success Response `200`**
```json
{
  "day_id": 12,
  "date": "2026-05-11",
  "shop_id": 1,
  "shop_name": "Main Branch",
  "opening_balance": 5000.00,
  "total_expense": 450.00,
  "expenses": [
    { "id": 5, "description": "Delivery charges", "amount": 250.00, "timestamp": "..." },
    { "id": 6, "description": "Stationery", "amount": 200.00, "timestamp": "..." }
  ],
  "total_sales": 8500.00,
  "total_cash_sales": 6000.00,
  "total_account_sales": 2500.00,
  "cash_in_hand": 10550.00,
  "cash_in_account": 2500.00,
  "closing_balance": 10500.00,
  "variance": -50.00,
  "variance_reason": "Short change given to customer",
  "day_started": true,
  "day_ended": true,
  "start_time": "2026-05-11T08:00:00Z",
  "end_time": "2026-05-11T20:00:00Z",
  "message": "Day summary retrieved successfully."
}
```

**Field Glossary**

| Field                  | Description                                              |
|------------------------|----------------------------------------------------------|
| `opening_balance`      | Cash in hand at start of day                             |
| `total_expense`        | Sum of all expenses for the day                          |
| `total_sales`          | Total value of all non-cancelled sales                   |
| `total_cash_sales`     | Sales paid via Cash on Delivery                          |
| `total_account_sales`  | Sales paid via non-cash (card, transfer, etc.)           |
| `cash_in_hand`         | Expected cash: `opening + cash_sales - expenses`         |
| `cash_in_account`      | Same as `total_account_sales`                            |
| `closing_balance`      | Actual cash counted by staff                             |
| `variance`             | `closing_balance - cash_in_hand` (negative = short)      |
| `variance_reason`      | Staff-entered reason if variance ≠ 0                     |
| `day_started`          | Whether the day has been started                         |
| `day_ended`            | Whether the day has been closed                          |

**Error Responses**

| Code | Reason                        |
|------|-------------------------------|
| 404  | Day not found                 |
| 403  | No access to this shop's day  |

---

### 7. Today's Status (All Shops)

**`GET /day-management/today`**

Returns the day status for all shops (admin) or the current shop (staff).

**Success Response `200`**
```json
[
  {
    "shop_id": 1,
    "shop_name": "Main Branch",
    "day_started": true,
    "day_ended": false,
    "active_day": { ... }
  },
  {
    "shop_id": 2,
    "shop_name": "City Store",
    "day_started": false,
    "day_ended": false,
    "active_day": null
  }
]
```

| Field         | Description                                         |
|--------------|-----------------------------------------------------|
| `day_started` | A day was opened today for this shop                |
| `day_ended`   | The day was also closed today                       |
| `active_day`  | The active day object if open, `null` if ended/not started |

**UI Behaviour**
- Admin: Show a table/card grid of all shops with status badges (Not Started / Active / Ended).
- Staff: Show single shop card.
- Use `day_started` + `day_ended` to determine which action buttons to show:

| `day_started` | `day_ended` | Visible Actions              |
|--------------|-------------|------------------------------|
| `false`      | `false`     | "Start Day" button           |
| `true`       | `false`     | "Add Expense", "End Day"     |
| `true`       | `true`      | "View Summary" only (read-only) |

---

## Recommended UI Flow

```
App Load
  └─ GET /today
       ├─ day_started: false  →  Show "Start Day" screen
       ├─ day_started: true, day_ended: false  →  Show "Day Dashboard"
       │     ├─ Display: opening balance, expenses, live cash in hand
       │     ├─ Action: Add Expense
       │     └─ Action: End Day (enter closing balance + reason)
       └─ day_started: true, day_ended: true  →  Show "Day Summary" (read-only)
             └─ GET /day/{day_id}  →  Display full financial summary
```

---

## Data Formats

- All datetimes are ISO 8601: `"2026-05-11T08:00:00Z"`
- All monetary values are `float` (display with 2 decimal places)
- `variance` can be negative (short) or positive (surplus)

## Error Handling

All errors return:
```json
{ "detail": "Human-readable error message" }
```

Show error messages inline (not alert boxes) for 400/403/404 responses.
