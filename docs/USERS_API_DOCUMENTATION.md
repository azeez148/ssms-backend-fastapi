# Users API Documentation

## Overview
The Users API provides endpoints for managing staff and admin users in the SSMS system. This API is designed exclusively for managing non-customer users (staff and admin roles only).

**Base URL:** `/users`

---

## Endpoints

### 1. List All Users
Get all staff and admin users in the system.

**Endpoint:** `GET /users`

**Method:** GET

**Authentication:** Required (Bearer Token)

**Query Parameters:** None

**Request Body:** None

**Response Model:**
```json
[
  {
    "id": "string",
    "mobile": "string",
    "email": "string (optional)",
    "role": "staff | admin",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

**Example Response (200 OK):**
```json
[
  {
    "id": "user_123",
    "mobile": "9876543210",
    "email": "john@example.com",
    "role": "staff",
    "created_at": "2025-02-19T10:30:00",
    "updated_at": "2025-02-19T10:30:00"
  },
  {
    "id": "admin_001",
    "mobile": "9123456789",
    "email": "admin@example.com",
    "role": "admin",
    "created_at": "2025-02-19T09:15:00",
    "updated_at": "2025-02-19T09:15:00"
  }
]
```

**Error Responses:**
- **500 Internal Server Error:** Server-side error occurred

---

### 2. Get User by ID
Retrieve a specific user's details.

**Endpoint:** `GET /users/{user_id}`

**Method:** GET

**Authentication:** Required (Bearer Token)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | string | The unique identifier of the user |

**Request Body:** None

**Response Model:**
```json
{
  "id": "string",
  "mobile": "string",
  "email": "string (optional)",
  "role": "staff | admin",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Example Response (200 OK):**
```json
{
  "id": "user_123",
  "mobile": "9876543210",
  "email": "john@example.com",
  "role": "staff",
  "created_at": "2025-02-19T10:30:00",
  "updated_at": "2025-02-19T10:30:00"
}
```

**Error Responses:**
- **404 Not Found:** User not found
- **500 Internal Server Error:** Server-side error occurred

---

### 3. Create New User
Create a new staff or admin user.

**Endpoint:** `POST /users`

**Method:** POST

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "id": "string (required)",
  "mobile": "string (required, 10-15 characters)",
  "password": "string (required, stored as plain text)",
  "email": "string (optional)",
  "role": "staff | admin (required)",
  "shop_id": "integer (required for staff, optional for admin)"
}
```

**Request Example:**
```json
{
  "id": "user_456",
  "mobile": "9876543210",
  "password": "mypassword123",
  "email": "jane@example.com",
  "role": "staff",
  "shop_id": 1
}
```

**Response Model:**
```json
{
  "id": "string",
  "mobile": "string",
  "email": "string (optional)",
  "role": "staff | admin",
  "shop_id": "integer (optional for admin, required for staff)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Example Response (200 OK):**
```json
{
  "id": "user_456",
  "mobile": "9876543210",
  "email": "jane@example.com",
  "role": "staff",
  "shop_id": 1,
  "created_at": "2025-02-19T11:45:00",
  "updated_at": "2025-02-19T11:45:00"
}
```

**Error Responses:**
- **400 Bad Request:** 
  - Invalid role (must be 'staff' or 'admin')
  - Mobile number format invalid (must be 10-15 characters)
  - User with this mobile already exists
  - Missing required fields
- **500 Internal Server Error:** Server-side error occurred

**Validation Rules:**
- `id`: Required, must be unique
- `mobile`: Required, must be between 10-15 characters and unique
- `password`: Required, stored as plain text for staff/admin users
- `email`: Optional
- `role`: Required, must be 'staff' or 'admin'

---

### 4. Update User
Update an existing user's details.

**Endpoint:** `PUT /users/{user_id}`

**Method:** PUT

**Authentication:** Required (Bearer Token)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | string | The unique identifier of the user |

**Request Body (all fields optional):**
```json
{
  "mobile": "string (optional, 10-15 characters)",
  "password": "string (optional, stored as plain text)",
  "email": "string (optional)",
  "role": "string (optional, staff | admin)",
  "shop_id": "integer (optional, required for staff role)"
}
```

**Request Example:**
```json
{
  "mobile": "9876543211",
  "email": "jane.updated@example.com",
  "password": "newpassword456",
  "shop_id": 2
}
```

**Response Model:**
```json
{
  "id": "string",
  "mobile": "string",
  "email": "string (optional)",
  "role": "staff | admin",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Example Response (200 OK):**
```json
{
  "id": "user_456",
  "mobile": "9876543211",
  "email": "jane.updated@example.com",
  "role": "staff",
  "shop_id": 2,
  "created_at": "2025-02-19T11:45:00",
  "updated_at": "2025-02-19T12:30:00"
}
```

**Error Responses:**
- **404 Not Found:** User not found
- **400 Bad Request:**
  - Mobile number format invalid (must be 10-15 characters)
  - Mobile already exists for another user
  - Invalid role format
- **500 Internal Server Error:** Server-side error occurred

**Notes:**
- Only provided fields will be updated (partial updates supported)
- If password is provided, it will be stored as plain text
- Dates are automatically updated to current timestamp on update

---

### 5. Delete User
Delete a user from the system.

**Endpoint:** `DELETE /users/{user_id}`

**Method:** DELETE

**Authentication:** Required (Bearer Token)

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | string | The unique identifier of the user |

**Request Body:** None

**Response Model:**
```json
{
  "message": "string"
}
```

**Example Response (200 OK):**
```json
{
  "message": "User deleted successfully"
}
```

**Error Responses:**
- **404 Not Found:** User not found
- **500 Internal Server Error:** Server-side error occurred

---

## Response Status Codes

| Status Code | Description |
|------------|-------------|
| 200 | OK - Request successful |
| 400 | Bad Request - Invalid parameters or validation error |
| 404 | Not Found - User not found |
| 500 | Internal Server Error - Server-side error |

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Example Error Response:**
```json
{
  "detail": "User with mobile 9876543210 already exists"
}
```

---

## Data Types

### User Object
```typescript
{
  id: string;                    // Unique identifier
  mobile: string;                // Phone number (10-15 characters)
  email: string | null;          // Optional email address
  role: "staff" | "admin";       // User role
  shop_id: number | null;        // Assigned shop (required for staff, optional for admin)
  created_at: ISO8601DateTime;   // Creation timestamp
  updated_at: ISO8601DateTime;   // Last update timestamp
}
```

---

## Important Notes

### Shops/Staff Assignment
- **Staff users:** MUST be assigned to a shop (shop_id is required)
- **Admin users:** CAN be assigned to a shop (optional)
- **Customer users:** NOT managed by this API
- Existing staff users without a shop assignment will be automatically assigned to shop ID 1 on first migration
- Staff can only operate within their assigned shop scope

### Password Storage
- **Staff and Admin users:** Passwords are stored as **plain text** in the `hashed_password` field
- Passwords are NOT encrypted or hashed for security purposes (as per system design)

### Mobile Number
- Must be between 10 and 15 characters
- Must be unique across all users
- Required field

### Role Restrictions
- Only 'staff' and 'admin' roles are allowed in this API
- Customer users should NOT be created or managed through this endpoint

### Email
- Optional field
- Must be unique if provided
- Can be null

### Shop Relationship
- A staff user's scope of operations is limited to their assigned shop
- This enables multi-shop operations with shop-specific staff management
- Admin users can have cross-shop visibility
- Consider implementing shop-scoped queries in future features

---

## Usage Examples

### cURL Examples

**List all users:**
```bash
curl -X GET "http://localhost:8000/users" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get specific user:**
```bash
curl -X GET "http://localhost:8000/users/user_123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Create new staff user:**
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "user_789",
    "mobile": "9876543210",
    "password": "staffpass123",
    "email": "staff@example.com",
    "role": "staff",
    "shop_id": 1
  }'
```

**Update user:**
```bash
curl -X PUT "http://localhost:8000/users/user_123" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile": "9876543211",
    "password": "newpass456",
    "shop_id": 2
  }'
```

**Delete user:**
```bash
curl -X DELETE "http://localhost:8000/users/user_123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Implementation Notes for Frontend

1. **Token-based Authentication:** All endpoints require a valid Bearer token in the Authorization header
2. **Partial Updates:** PUT endpoint supports partial updates - only include fields you want to change
3. **Plain Text Passwords:** Remember that passwords for staff/admin are stored as plain text
4. **Unique Constraints:** Mobile numbers and emails must be unique
5. **Role Validation:** Only 'staff' and 'admin' roles are permitted (validated server-side)
6. **Shop Assignment:** 
   - Staff users MUST have a shop_id assigned
   - Admin users can optionally have a shop_id
   - API will reject staff user creation/update without shop assignment
7. **Error Handling:** Always check the `detail` field in error responses for specific error messages
8. **Future Features:** Shop assignment enables:
   - Shop-scoped access control for staff users
   - Multi-shop operations with staff management
   - Reporting and analytics per shop
   - Inventory management per shop location

---

## Support

For issues or questions regarding this API, please contact the backend team.

**Last Updated:** February 19, 2025
**API Version:** 1.1
**Features:** User management with shop assignment for staff users
