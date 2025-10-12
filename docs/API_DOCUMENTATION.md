# 📚 HaYBuy Backend - API Documentation

## 📖 Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Request/Response Examples](#requestresponse-examples)
- [Error Handling](#error-handling)

---

## 🎯 Overview

HaYBuy Backend API เป็น RESTful API ที่ใช้ FastAPI Framework สำหรับจัดการระบบการซื้อขายและจัดการกลุ่ม

### Base URL

- **Development**: `http://localhost:8000`
- **Production**: TBD

### API Version

- **Current Version**: v1
- **Base Path**: `/v1`

---

## 🔐 Authentication

### JWT Token Authentication

API ใช้ JWT (JSON Web Token) สำหรับการ Authentication

#### การขอ Access Token

**Endpoint**: `POST /v1/auth/token`

**Request Body**:

```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### การใช้ Token

ส่ง Token ใน Header ของทุก Request ที่ต้องการ Authentication:

```
Authorization: Bearer <your_access_token>
```

#### Token Configuration

- **Algorithm**: HS256
- **Expiration**: 30 minutes (กำหนดใน `.env`)
- **Secret Key**: กำหนดใน environment variable `JWT_SECRET_KEY`

---

## 🛣️ API Endpoints

### 1. Authentication Routes (`/v1/auth`)

#### Login

- **POST** `/v1/auth/token`
  - **Description**: รับ Access Token สำหรับ Authentication
  - **Auth Required**: ❌ No
  - **Request Body**: Form data (username, password)
  - **Response**: Access token และ token type

---

### 2. User Routes (`/v1/users`)

#### Get All Users

- **GET** `/v1/users`
  - **Description**: ดึงข้อมูลผู้ใช้ทั้งหมด
  - **Auth Required**: ✅ Yes
  - **Response**: Array of user objects

#### Get User by ID

- **GET** `/v1/users/{user_id}`
  - **Description**: ดึงข้อมูลผู้ใช้ตาม ID
  - **Auth Required**: ✅ Yes
  - **Path Parameters**: `user_id` (integer)
  - **Response**: User object

#### Create User

- **POST** `/v1/users`
  - **Description**: สร้างผู้ใช้ใหม่
  - **Auth Required**: ❌ No
  - **Request Body**: User creation data
  - **Response**: Created user object

#### Update User

- **PUT** `/v1/users/{user_id}`
  - **Description**: อัปเดตข้อมูลผู้ใช้
  - **Auth Required**: ✅ Yes
  - **Path Parameters**: `user_id` (integer)
  - **Request Body**: User update data
  - **Response**: Updated user object

#### Delete User

- **DELETE** `/v1/users/{user_id}`
  - **Description**: ลบผู้ใช้
  - **Auth Required**: ✅ Yes
  - **Path Parameters**: `user_id` (integer)
  - **Response**: Success message

---

### 3. User Profile Routes (`/v1/profiles`)

#### Get User Profile

- **GET** `/v1/profiles/{user_id}`
  - **Description**: ดึงข้อมูล Profile ของผู้ใช้
  - **Auth Required**: ✅ Yes
  - **Response**: User profile object

#### Update User Profile

- **PUT** `/v1/profiles/{user_id}`
  - **Description**: อัปเดตข้อมูล Profile
  - **Auth Required**: ✅ Yes
  - **Request Body**: Profile update data
  - **Response**: Updated profile object

---

### 4. Category Routes (`/v1/categories`)

#### Get All Categories

- **GET** `/v1/categories`
  - **Description**: ดึงหมวดหมู่สินค้าทั้งหมด
  - **Auth Required**: ✅ Yes
  - **Response**: Array of category objects

#### Create Category

- **POST** `/v1/categories`
  - **Description**: สร้างหมวดหมู่ใหม่
  - **Auth Required**: ✅ Yes
  - **Request Body**: Category data
  - **Response**: Created category object

---

### 5. Item Routes (`/v1/items`)

#### Get All Items

- **GET** `/v1/items`
  - **Description**: ดึงข้อมูลสินค้าทั้งหมด
  - **Auth Required**: ✅ Yes
  - **Query Parameters**:
    - `skip` (integer): Number of records to skip
    - `limit` (integer): Maximum number of records
  - **Response**: Array of item objects

#### Get Item by ID

- **GET** `/v1/items/{item_id}`
  - **Description**: ดึงข้อมูลสินค้าตาม ID
  - **Auth Required**: ✅ Yes
  - **Response**: Item object

#### Create Item

- **POST** `/v1/items`
  - **Description**: สร้างสินค้าใหม่
  - **Auth Required**: ✅ Yes
  - **Request Body**: Item data
  - **Response**: Created item object

#### Update Item

- **PUT** `/v1/items/{item_id}`
  - **Description**: อัปเดตข้อมูลสินค้า
  - **Auth Required**: ✅ Yes
  - **Response**: Updated item object

#### Delete Item

- **DELETE** `/v1/items/{item_id}`
  - **Description**: ลบสินค้า
  - **Auth Required**: ✅ Yes
  - **Response**: Success message

---

### 6. Wish Item Routes (`/v1/wish-items`)

#### Get Wish List

- **GET** `/v1/wish-items`
  - **Description**: ดึงรายการสินค้าที่ต้องการ
  - **Auth Required**: ✅ Yes
  - **Response**: Array of wish items

#### Add to Wish List

- **POST** `/v1/wish-items`
  - **Description**: เพิ่มสินค้าลงรายการที่ต้องการ
  - **Auth Required**: ✅ Yes
  - **Request Body**: Wish item data
  - **Response**: Created wish item

---

### 7. Group Routes (`/v1/groups`)

#### Get All Groups

- **GET** `/v1/groups`
  - **Description**: ดึงข้อมูลกลุ่มทั้งหมด
  - **Auth Required**: ✅ Yes
  - **Response**: Array of group objects

#### Create Group

- **POST** `/v1/groups`
  - **Description**: สร้างกลุ่มใหม่
  - **Auth Required**: ✅ Yes
  - **Request Body**: Group data
  - **Response**: Created group object

#### Update Group

- **PUT** `/v1/groups/{group_id}`
  - **Description**: อัปเดตข้อมูลกลุ่ม
  - **Auth Required**: ✅ Yes
  - **Response**: Updated group object

---

### 8. Group Member Routes (`/v1/group-members`)

#### Get Group Members

- **GET** `/v1/group-members/{group_id}`
  - **Description**: ดึงข้อมูลสมาชิกในกลุ่ม
  - **Auth Required**: ✅ Yes
  - **Response**: Array of member objects

#### Add Member to Group

- **POST** `/v1/group-members`
  - **Description**: เพิ่มสมาชิกเข้ากลุ่ม
  - **Auth Required**: ✅ Yes
  - **Request Body**: Member data
  - **Response**: Success message

#### Remove Member from Group

- **DELETE** `/v1/group-members/{group_id}/{user_id}`
  - **Description**: ลบสมาชิกออกจากกลุ่ม
  - **Auth Required**: ✅ Yes
  - **Response**: Success message

---

### 9. Group Item Routes (`/v1/group-items`)

#### Get Group Items

- **GET** `/v1/group-items/{group_id}`
  - **Description**: ดึงสินค้าในกลุ่ม
  - **Auth Required**: ✅ Yes
  - **Response**: Array of group items

#### Add Item to Group

- **POST** `/v1/group-items`
  - **Description**: เพิ่มสินค้าเข้ากลุ่ม
  - **Auth Required**: ✅ Yes
  - **Request Body**: Group item data
  - **Response**: Created group item

---

### 10. Transaction Routes (`/v1/transactions`)

#### Get All Transactions

- **GET** `/v1/transactions`
  - **Description**: ดึงข้อมูลธุรกรรมทั้งหมด
  - **Auth Required**: ✅ Yes
  - **Response**: Array of transaction objects

#### Create Transaction

- **POST** `/v1/transactions`
  - **Description**: สร้างธุรกรรมใหม่
  - **Auth Required**: ✅ Yes
  - **Request Body**: Transaction data
  - **Response**: Created transaction object

---

## 📋 Request/Response Examples

### User Registration

**Request**:

```bash
curl -X POST "http://localhost:8000/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securePassword123"
  }'
```

**Response** (201 Created):

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2025-10-11T10:30:00Z"
}
```

### Get Items with Pagination

**Request**:

```bash
curl -X GET "http://localhost:8000/v1/items?skip=0&limit=10" \
  -H "Authorization: Bearer <your_token>"
```

**Response** (200 OK):

```json
[
  {
    "id": 1,
    "name": "Product A",
    "description": "Description of Product A",
    "price": 99.99,
    "category_id": 1,
    "created_at": "2025-10-11T10:30:00Z"
  },
  {
    "id": 2,
    "name": "Product B",
    "description": "Description of Product B",
    "price": 149.99,
    "category_id": 2,
    "created_at": "2025-10-11T11:00:00Z"
  }
]
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Status Code | Description                                      |
| ----------- | ------------------------------------------------ |
| 200         | OK - Request successful                          |
| 201         | Created - Resource created successfully          |
| 400         | Bad Request - Invalid input data                 |
| 401         | Unauthorized - Authentication required or failed |
| 403         | Forbidden - Insufficient permissions             |
| 404         | Not Found - Resource not found                   |
| 422         | Unprocessable Entity - Validation error          |
| 500         | Internal Server Error - Server error             |

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Common Error Examples

#### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

#### 404 Not Found

```json
{
  "detail": "Item not found"
}
```

#### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## 📱 Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔗 Related Documentation

- [Setup Guide](../README.md)
- [Database Schema](./DATABASE_SCHEMA.md)
- [Development Guide](./DEVELOPMENT_GUIDE.md)

---

> Last Updated: October 11, 2025
