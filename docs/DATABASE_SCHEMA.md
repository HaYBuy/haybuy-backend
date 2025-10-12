# 🗄️ HaYBuy Backend - Database Schema

## 📖 Table of Contents

- [Overview](#overview)
- [Database Configuration](#database-configuration)
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Tables](#tables)
- [Relationships](#relationships)
- [Indexes](#indexes)

---

## 🎯 Overview

HaYBuy Backend ใช้ **PostgreSQL 16** เป็นฐานข้อมูล พร้อม **SQLAlchemy 2.0+** เป็น ORM

### Database Information

- **Database Engine**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0+
- **Migration Tool**: Alembic (recommended)
- **Default Database Name**: `haybuy_db`
- **Default Port**: 5432

---

## ⚙️ Database Configuration

### Connection String Format

```
postgresql+psycopg2://[user]:[password]@[host]:[port]/[database]
```

### Development Configuration

```env
DATABASE_URL=postgresql+psycopg2://admin:admin@localhost:5432/haybuy_db
```

### Docker Configuration

```env
DATABASE_URL=postgresql+psycopg2://admin:admin@db:5432/haybuy_db
```

---

## 📊 Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐
│    User     │────────│ UserProfile  │
└─────────────┘         └──────────────┘
      │
      │ 1:N
      ▼
┌─────────────┐         ┌──────────────┐
│   Item      │────────│  WishItem    │
└─────────────┘         └──────────────┘
      │
      │ N:1
      ▼
┌─────────────┐
│  Category   │
└─────────────┘

┌─────────────┐         ┌──────────────┐
│    Group    │────────│ GroupMember  │
└─────────────┘         └──────────────┘
      │                        │
      │ 1:N                 N:1│
      ▼                        ▼
┌─────────────┐         ┌──────────────┐
│ GroupItem   │         │     User     │
└─────────────┘         └──────────────┘

┌──────────────┐        ┌──────────────┐
│    Item      │────────│ PriceHistory │
└──────────────┘   1:N  └──────────────┘

┌──────────────┐
│ Transaction  │
└──────────────┘
```

---

## 📋 Tables

### 1. Users Table

**Table Name**: `users`

| Column          | Type        | Constraints                 | Description         |
| --------------- | ----------- | --------------------------- | ------------------- |
| id              | Integer     | PRIMARY KEY, AUTO_INCREMENT | รหัสผู้ใช้          |
| username        | String(50)  | UNIQUE, NOT NULL            | ชื่อผู้ใช้          |
| email           | String(100) | UNIQUE, NOT NULL            | อีเมล               |
| hashed_password | String(255) | NOT NULL                    | รหัสผ่านที่เข้ารหัส |
| is_active       | Boolean     | DEFAULT TRUE                | สถานะการใช้งาน      |
| is_superuser    | Boolean     | DEFAULT FALSE               | สถานะผู้ดูแลระบบ    |
| created_at      | DateTime    | DEFAULT NOW()               | วันที่สร้าง         |
| updated_at      | DateTime    | DEFAULT NOW()               | วันที่อัปเดต        |

**Indexes**:

- `idx_users_username` on `username`
- `idx_users_email` on `email`

---

### 2. User Profiles Table

**Table Name**: `user_profiles`

| Column        | Type        | Constraints                    | Description    |
| ------------- | ----------- | ------------------------------ | -------------- |
| id            | Integer     | PRIMARY KEY, AUTO_INCREMENT    | รหัส Profile   |
| user_id       | Integer     | FOREIGN KEY → users.id, UNIQUE | รหัสผู้ใช้     |
| first_name    | String(50)  | NULL                           | ชื่อจริง       |
| last_name     | String(50)  | NULL                           | นามสกุล        |
| phone_number  | String(20)  | NULL                           | เบอร์โทรศัพท์  |
| address       | Text        | NULL                           | ที่อยู่        |
| date_of_birth | Date        | NULL                           | วันเกิด        |
| avatar_url    | String(255) | NULL                           | URL รูปโปรไฟล์ |
| created_at    | DateTime    | DEFAULT NOW()                  | วันที่สร้าง    |
| updated_at    | DateTime    | DEFAULT NOW()                  | วันที่อัปเดต   |

**Relationships**:

- One-to-One with `users`

---

### 3. Categories Table

**Table Name**: `categories`

| Column      | Type        | Constraints                 | Description    |
| ----------- | ----------- | --------------------------- | -------------- |
| id          | Integer     | PRIMARY KEY, AUTO_INCREMENT | รหัสหมวดหมู่   |
| name        | String(100) | UNIQUE, NOT NULL            | ชื่อหมวดหมู่   |
| description | Text        | NULL                        | คำอธิบาย       |
| icon_url    | String(255) | NULL                        | URL ไอคอน      |
| parent_id   | Integer     | FOREIGN KEY → categories.id | หมวดหมู่แม่    |
| is_active   | Boolean     | DEFAULT TRUE                | สถานะการใช้งาน |
| created_at  | DateTime    | DEFAULT NOW()               | วันที่สร้าง    |
| updated_at  | DateTime    | DEFAULT NOW()               | วันที่อัปเดต   |

**Relationships**:

- Self-referencing (parent-child categories)
- One-to-Many with `items`

---

### 4. Items Table

**Table Name**: `items`

| Column         | Type             | Constraints                 | Description          |
| -------------- | ---------------- | --------------------------- | -------------------- |
| id             | Integer          | PRIMARY KEY, AUTO_INCREMENT | รหัสสินค้า           |
| name           | String(200)      | NOT NULL                    | ชื่อสินค้า           |
| description    | Text             | NULL                        | คำอธิบาย             |
| price          | Decimal(10,2)    | NOT NULL                    | ราคา                 |
| category_id    | Integer          | FOREIGN KEY → categories.id | รหัสหมวดหมู่         |
| user_id        | Integer          | FOREIGN KEY → users.id      | รหัสผู้สร้าง         |
| image_url      | String(255)      | NULL                        | URL รูปสินค้า        |
| stock_quantity | Integer          | DEFAULT 0                   | จำนวนคงเหลือ         |
| is_available   | Boolean          | DEFAULT TRUE                | สถานะพร้อมขาย        |
| location       | Geography(Point) | NULL                        | ตำแหน่งที่ตั้ง (GIS) |
| created_at     | DateTime         | DEFAULT NOW()               | วันที่สร้าง          |
| updated_at     | DateTime         | DEFAULT NOW()               | วันที่อัปเดต         |

**Indexes**:

- `idx_items_category` on `category_id`
- `idx_items_user` on `user_id`
- `idx_items_is_available` on `is_available`

**Relationships**:

- Many-to-One with `categories`
- Many-to-One with `users`
- One-to-Many with `price_histories`
- One-to-Many with `wish_items`

---

### 5. Wish Items Table

**Table Name**: `wish_items`

| Column     | Type     | Constraints                 | Description     |
| ---------- | -------- | --------------------------- | --------------- |
| id         | Integer  | PRIMARY KEY, AUTO_INCREMENT | รหัส Wish Item  |
| user_id    | Integer  | FOREIGN KEY → users.id      | รหัสผู้ใช้      |
| item_id    | Integer  | FOREIGN KEY → items.id      | รหัสสินค้า      |
| priority   | Integer  | DEFAULT 0                   | ระดับความสำคัญ  |
| notes      | Text     | NULL                        | บันทึกเพิ่มเติม |
| created_at | DateTime | DEFAULT NOW()               | วันที่เพิ่ม     |

**Constraints**:

- UNIQUE constraint on (`user_id`, `item_id`)

**Relationships**:

- Many-to-One with `users`
- Many-to-One with `items`

---

### 6. Price Histories Table

**Table Name**: `price_histories`

| Column     | Type          | Constraints                 | Description          |
| ---------- | ------------- | --------------------------- | -------------------- |
| id         | Integer       | PRIMARY KEY, AUTO_INCREMENT | รหัสประวัติราคา      |
| item_id    | Integer       | FOREIGN KEY → items.id      | รหัสสินค้า           |
| price      | Decimal(10,2) | NOT NULL                    | ราคา                 |
| changed_at | DateTime      | DEFAULT NOW()               | วันที่เปลี่ยนแปลง    |
| changed_by | Integer       | FOREIGN KEY → users.id      | ผู้เปลี่ยนแปลง       |
| reason     | String(255)   | NULL                        | เหตุผลการเปลี่ยนแปลง |

**Indexes**:

- `idx_price_history_item` on `item_id`
- `idx_price_history_date` on `changed_at`

**Relationships**:

- Many-to-One with `items`
- Many-to-One with `users`

---

### 7. Groups Table

**Table Name**: `groups`

| Column      | Type        | Constraints                 | Description       |
| ----------- | ----------- | --------------------------- | ----------------- |
| id          | Integer     | PRIMARY KEY, AUTO_INCREMENT | รหัสกลุ่ม         |
| name        | String(100) | NOT NULL                    | ชื่อกลุ่ม         |
| description | Text        | NULL                        | คำอธิบาย          |
| owner_id    | Integer     | FOREIGN KEY → users.id      | รหัสเจ้าของกลุ่ม  |
| is_active   | Boolean     | DEFAULT TRUE                | สถานะกลุ่ม        |
| max_members | Integer     | DEFAULT NULL                | จำนวนสมาชิกสูงสุด |
| created_at  | DateTime    | DEFAULT NOW()               | วันที่สร้าง       |
| updated_at  | DateTime    | DEFAULT NOW()               | วันที่อัปเดต      |

**Relationships**:

- Many-to-One with `users` (owner)
- One-to-Many with `group_members`
- One-to-Many with `group_items`

---

### 8. Group Members Table

**Table Name**: `group_members`

| Column    | Type     | Constraints                 | Description    |
| --------- | -------- | --------------------------- | -------------- |
| id        | Integer  | PRIMARY KEY, AUTO_INCREMENT | รหัสสมาชิก     |
| group_id  | Integer  | FOREIGN KEY → groups.id     | รหัสกลุ่ม      |
| user_id   | Integer  | FOREIGN KEY → users.id      | รหัสผู้ใช้     |
| role      | Enum     | 'admin', 'member'           | บทบาทในกลุ่ม   |
| joined_at | DateTime | DEFAULT NOW()               | วันที่เข้าร่วม |
| is_active | Boolean  | DEFAULT TRUE                | สถานะสมาชิก    |

**Constraints**:

- UNIQUE constraint on (`group_id`, `user_id`)

**Relationships**:

- Many-to-One with `groups`
- Many-to-One with `users`

---

### 9. Group Items Table

**Table Name**: `group_items`

| Column   | Type     | Constraints                       | Description     |
| -------- | -------- | --------------------------------- | --------------- |
| id       | Integer  | PRIMARY KEY, AUTO_INCREMENT       | รหัส Group Item |
| group_id | Integer  | FOREIGN KEY → groups.id           | รหัสกลุ่ม       |
| item_id  | Integer  | FOREIGN KEY → items.id            | รหัสสินค้า      |
| added_by | Integer  | FOREIGN KEY → users.id            | ผู้เพิ่มสินค้า  |
| quantity | Integer  | DEFAULT 1                         | จำนวน           |
| status   | Enum     | 'pending', 'approved', 'rejected' | สถานะ           |
| added_at | DateTime | DEFAULT NOW()                     | วันที่เพิ่ม     |

**Relationships**:

- Many-to-One with `groups`
- Many-to-One with `items`
- Many-to-One with `users`

---

### 10. Transactions Table

**Table Name**: `transactions`

| Column         | Type          | Constraints                         | Description     |
| -------------- | ------------- | ----------------------------------- | --------------- |
| id             | Integer       | PRIMARY KEY, AUTO_INCREMENT         | รหัสธุรกรรม     |
| buyer_id       | Integer       | FOREIGN KEY → users.id              | รหัสผู้ซื้อ     |
| seller_id      | Integer       | FOREIGN KEY → users.id              | รหัสผู้ขาย      |
| item_id        | Integer       | FOREIGN KEY → items.id              | รหัสสินค้า      |
| quantity       | Integer       | NOT NULL                            | จำนวน           |
| unit_price     | Decimal(10,2) | NOT NULL                            | ราคาต่อหน่วย    |
| total_price    | Decimal(10,2) | NOT NULL                            | ราคารวม         |
| status         | Enum          | 'pending', 'completed', 'cancelled' | สถานะ           |
| payment_method | String(50)    | NULL                                | วิธีการชำระเงิน |
| created_at     | DateTime      | DEFAULT NOW()                       | วันที่สร้าง     |
| completed_at   | DateTime      | NULL                                | วันที่เสร็จสิ้น |

**Indexes**:

- `idx_transactions_buyer` on `buyer_id`
- `idx_transactions_seller` on `seller_id`
- `idx_transactions_status` on `status`

**Relationships**:

- Many-to-One with `users` (buyer)
- Many-to-One with `users` (seller)
- Many-to-One with `items`

---

## 🔗 Relationships

### User Relationships

- **1:1** with UserProfile
- **1:N** with Items (as creator)
- **1:N** with WishItems
- **1:N** with Groups (as owner)
- **N:M** with Groups (as member through GroupMembers)
- **1:N** with Transactions (as buyer)
- **1:N** with Transactions (as seller)

### Item Relationships

- **N:1** with Category
- **N:1** with User (creator)
- **1:N** with PriceHistories
- **1:N** with WishItems
- **N:M** with Groups (through GroupItems)

### Group Relationships

- **N:1** with User (owner)
- **N:M** with Users (through GroupMembers)
- **N:M** with Items (through GroupItems)

---

## 📌 Indexes

### Performance Indexes

```sql
-- User indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Item indexes
CREATE INDEX idx_items_category ON items(category_id);
CREATE INDEX idx_items_user ON items(user_id);
CREATE INDEX idx_items_is_available ON items(is_available);

-- Transaction indexes
CREATE INDEX idx_transactions_buyer ON transactions(buyer_id);
CREATE INDEX idx_transactions_seller ON transactions(seller_id);
CREATE INDEX idx_transactions_status ON transactions(status);

-- Price history indexes
CREATE INDEX idx_price_history_item ON price_histories(item_id);
CREATE INDEX idx_price_history_date ON price_histories(changed_at);
```

---

## 🔧 Database Initialization

### Using SQLAlchemy (Current Method)

The application automatically creates all tables on startup:

```python
# In app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
```

### Using Alembic (Recommended for Production)

For better migration control:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

---

## 🗂️ Model Files Location

```
app/db/models/
├── Users/
│   ├── User.py
│   └── UserProfile.py
├── Categorys/
│   └── main.py
├── items/
│   ├── item.py
│   └── wishItem.py
├── Groups/
│   ├── group.py
│   ├── groupMember.py
│   └── group_item.py
├── PriceHistorys/
│   └── main.py
└── Transactions/
    └── transaction_model.py
```

---

## 📝 Notes

### GeoAlchemy2

- ใช้สำหรับจัดการข้อมูล Geographic (location ใน Items table)
- ต้องติดตั้ง PostGIS extension ใน PostgreSQL

### Password Hashing

- ใช้ bcrypt สำหรับเข้ารหัสรหัสผ่าน
- จัดการผ่าน `app/core/security.py`

### Timezone

- ใช้ UTC สำหรับ DateTime fields
- จัดการ timezone conversion ด้วย pytz

---

## 🔗 Related Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Setup Guide](../README.md)
- [Development Guide](./DEVELOPMENT_GUIDE.md)

---

> Last Updated: October 11, 2025
