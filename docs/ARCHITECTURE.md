# 🏗️ HaYBuy Backend - Architecture Documentation

## 📖 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Design Patterns](#design-patterns)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)

---

## 🎯 Overview

HaYBuy Backend เป็น RESTful API ที่สร้างด้วย FastAPI Framework โดยมีโครงสร้างแบบ **Layered Architecture** เพื่อความยืดหยุ่นและง่ายต่อการ maintain

### Key Principles

- **Separation of Concerns**: แยกส่วนต่างๆ ออกจากกันอย่างชัดเจน
- **Dependency Injection**: ใช้ FastAPI's Depends system
- **Type Safety**: ใช้ Pydantic สำหรับ validation และ type hints
- **RESTful Design**: ปฏิบัติตาม REST principles
- **Security First**: JWT authentication และ password hashing

---

## 🏛️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│              Client Applications                │
│    (Mobile App, Web App, Third-party APIs)     │
└────────────────────┬────────────────────────────┘
                     │ HTTP/HTTPS
                     │ REST API
┌────────────────────▼────────────────────────────┐
│              FastAPI Application                │
│  ┌───────────────────────────────────────────┐  │
│  │         Router Layer (v1)                 │  │
│  │  /auth, /users, /items, /groups, etc.    │  │
│  └───────────────────┬───────────────────────┘  │
│  ┌───────────────────▼───────────────────────┐  │
│  │         Core Layer                        │  │
│  │  Security, Dependencies, Middlewares      │  │
│  └───────────────────┬───────────────────────┘  │
│  ┌───────────────────▼───────────────────────┐  │
│  │         Schema Layer (Pydantic)           │  │
│  │  Request/Response Models                  │  │
│  └───────────────────┬───────────────────────┘  │
│  ┌───────────────────▼───────────────────────┐  │
│  │         Database Layer (SQLAlchemy)       │  │
│  │  Models, Session Management               │  │
│  └───────────────────┬───────────────────────┘  │
└────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│           PostgreSQL Database                   │
│              (haybuy_db)                        │
└─────────────────────────────────────────────────┘
```

### Container Architecture (Docker)

```
┌─────────────────────────────────────────────────┐
│              Docker Host                        │
│  ┌───────────────────┐  ┌──────────────────┐   │
│  │  haybuy-api       │  │   haybuy-db      │   │
│  │  Container        │  │   Container      │   │
│  │  (Python 3.13)    │  │   (PostgreSQL)   │   │
│  │  Port: 8000       │  │   Port: 5432     │   │
│  └─────────┬─────────┘  └────────┬─────────┘   │
│            │                     │              │
│            │   DATABASE_URL      │              │
│            └─────────────────────┘              │
│                                                  │
│  Volume: haybuy_pgdata (Persistent Storage)     │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend Framework

- **FastAPI 0.116+**: Modern, fast web framework
- **Uvicorn**: ASGI server
- **Python 3.13**: Latest Python version

### Database & ORM

- **PostgreSQL 16**: Primary database
- **SQLAlchemy 2.0+**: ORM and database toolkit
- **psycopg2-binary**: PostgreSQL adapter
- **GeoAlchemy2**: Geographic data support

### Authentication & Security

- **python-jose**: JWT token handling
- **PyJWT**: JWT implementation
- **bcrypt**: Password hashing
- **passlib**: Password utility library

### Validation & Serialization

- **Pydantic**: Data validation and settings management
- **python-multipart**: Form data support

### Development Tools

- **python-dotenv**: Environment variable management
- **pytz / tzdata**: Timezone support
- **Alembic**: Database migrations (recommended)

### Containerization

- **Docker**: Container platform
- **Docker Compose**: Multi-container orchestration

---

## 📁 Project Structure

```
haybuy-backend/
│
├── app/                          # Main application directory
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   │
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py           # JWT, authentication, authorization
│   │   └── dependencies.py       # Shared dependencies
│   │
│   ├── db/                       # Database layer
│   │   ├── __init__.py
│   │   ├── database.py           # Database connection, session
│   │   └── models/               # SQLAlchemy models
│   │       ├── __init__.py
│   │       ├── Users/
│   │       │   ├── User.py
│   │       │   └── UserProfile.py
│   │       ├── Categorys/
│   │       │   └── main.py
│   │       ├── items/
│   │       │   ├── item.py
│   │       │   └── wishItem.py
│   │       ├── Groups/
│   │       │   ├── group.py
│   │       │   ├── groupMember.py
│   │       │   └── group_item.py
│   │       ├── PriceHistorys/
│   │       │   └── main.py
│   │       └── Transactions/
│   │           └── transaction_model.py
│   │
│   ├── schemas/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── user_profile_schema.py
│   │   ├── item_schema.py
│   │   ├── category_schema.py
│   │   ├── wish_item_schema.py
│   │   ├── group_schema.py
│   │   ├── group_member_schema.py
│   │   ├── group_item_schema.py
│   │   ├── transaction_schema.py
│   │   └── price_history.py
│   │
│   └── routers/                  # API routes
│       ├── __init__.py
│       └── v1/                   # API version 1
│           ├── __init__.py
│           ├── auth_rounter.py
│           ├── user_rounter.py
│           ├── user_profile_rounter.py
│           ├── item_rounter.py
│           ├── category_rounter.py
│           ├── wish_item_rounter.py
│           ├── group_rounter.py
│           ├── group_member_rounter.py
│           ├── group_item_rounter.py
│           ├── transaction_rounter.py
│           └── hello.py
│
├── docs/                         # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SCHEMA.md
│   ├── ARCHITECTURE.md
│   └── DEVELOPMENT_GUIDE.md
│
├── tests/                        # Test suite (to be implemented)
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_items.py
│
├── alembic/                      # Database migrations (optional)
│   └── versions/
│
├── .env                          # Environment variables
├── .env.example                  # Environment template
├── .gitignore
├── docker-compose.yml            # Production compose file
├── docker-compose.dev.yml        # Development compose file
├── Dockerfile                    # Docker image definition
├── pyproject.toml               # Poetry configuration
├── requirements.txt             # Python dependencies
├── poetry.toml                  # Poetry settings
└── README.md                    # Project overview
```

---

## 🎨 Design Patterns

### 1. Layered Architecture

แบ่งเป็น 4 layers หลัก:

#### Router Layer (Presentation)

- จัดการ HTTP requests/responses
- Route definition และ path operations
- Input validation (ร่วมกับ Pydantic)

```python
# Example: app/routers/v1/item_rounter.py
@router.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    # Handle request
    pass
```

#### Schema Layer (Data Transfer)

- Pydantic models สำหรับ validation
- Request และ Response schemas
- Type safety และ auto-documentation

```python
# Example: app/schemas/item_schema.py
class ItemCreate(BaseModel):
    name: str
    price: Decimal
    category_id: int
```

#### Database Layer (Persistence)

- SQLAlchemy ORM models
- Database session management
- Query operations

```python
# Example: app/db/models/items/item.py
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
```

#### Core Layer (Business Logic)

- Authentication และ Authorization
- Shared utilities
- Dependencies injection

```python
# Example: app/core/security.py
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify JWT token
    pass
```

---

### 2. Dependency Injection

ใช้ FastAPI's Depends สำหรับ:

```python
# Database session injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Current user injection
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    # Verify and return user
    pass

# Usage in router
@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
```

---

### 3. Repository Pattern (Implicit)

แม้ไม่ได้สร้าง Repository classes แยก แต่ใช้ SQLAlchemy queries ใน routers:

```python
# Current approach
item = db.query(Item).filter(Item.id == item_id).first()

# Recommended: Create repository layer
class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, item_id: int) -> Optional[Item]:
        return self.db.query(Item).filter(Item.id == item_id).first()
```

---

### 4. Factory Pattern

ใช้ใน database session และ token creation:

```python
# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Token factory
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

---

## 🔄 Data Flow

### Request Flow (Authenticated Endpoint)

```
1. Client Request
   │
   ├─→ HTTP Request + JWT Token
   │
2. FastAPI Router
   │
   ├─→ Route matching: @router.get("/items/{id}")
   │
3. Dependency Injection
   │
   ├─→ get_db(): Database session
   ├─→ get_current_user(): Verify JWT, get user
   │
4. Schema Validation
   │
   ├─→ Pydantic validates request data
   │
5. Business Logic
   │
   ├─→ Query database via SQLAlchemy
   ├─→ Apply business rules
   │
6. Response Serialization
   │
   ├─→ Pydantic serializes response
   │
7. HTTP Response
   │
   └─→ JSON response to client
```

### Authentication Flow

```
1. Login Request
   │
   ├─→ POST /v1/auth/token
   │   Body: {username, password}
   │
2. Validate Credentials
   │
   ├─→ Query user from database
   ├─→ Verify password with bcrypt
   │
3. Generate JWT Token
   │
   ├─→ create_access_token()
   ├─→ Token payload: {sub: username, id: user_id, exp: timestamp}
   │
4. Return Token
   │
   └─→ Response: {access_token, token_type}

5. Subsequent Requests
   │
   ├─→ Header: Authorization: Bearer <token>
   ├─→ get_current_user() validates token
   └─→ Access granted/denied
```

---

## 🔒 Security Architecture

### Authentication Strategy

#### JWT (JSON Web Tokens)

- **Algorithm**: HS256
- **Expiration**: 30 minutes (configurable)
- **Payload**: username, user_id, expiration time
- **Secret Key**: Stored in environment variables

```python
# Token structure
{
  "sub": "username",
  "id": 123,
  "exp": 1699999999
}
```

### Password Security

#### Hashing Strategy

- **Algorithm**: bcrypt
- **Salt Rounds**: Default (auto-handled by bcrypt)
- **Storage**: Only hashed passwords stored in database

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash(plain_password)

# Verify password
pwd_context.verify(plain_password, hashed_password)
```

### Security Best Practices

✅ **Implemented**:

- JWT token authentication
- Password hashing with bcrypt
- CORS middleware configuration
- Environment variable for secrets
- SQL injection prevention (via ORM)

⚠️ **Recommended Enhancements**:

- Rate limiting
- HTTPS enforcement (production)
- Request size limits
- SQL query logging (dev only)
- Password complexity requirements
- Token refresh mechanism
- Account lockout after failed attempts
- Input sanitization
- API versioning

---

## 🚀 Scalability Considerations

### Current Architecture

- **Stateless**: No session storage, scales horizontally
- **Database Pooling**: SQLAlchemy connection pool
- **Container-Ready**: Docker support for easy deployment

### Future Enhancements

- **Caching**: Redis for frequently accessed data
- **Message Queue**: Celery for async tasks
- **Load Balancer**: Nginx/Traefik for multiple instances
- **Database Replication**: Read replicas for scaling
- **CDN**: Static file serving
- **Monitoring**: Prometheus + Grafana

---

## 📊 Performance Optimization

### Database Optimization

- **Indexes**: On frequently queried columns
- **Eager Loading**: Prevent N+1 queries
- **Connection Pooling**: Reuse database connections
- **Query Optimization**: Use SQLAlchemy efficiently

```python
# N+1 Problem (Bad)
items = db.query(Item).all()
for item in items:
    category = item.category  # Separate query each time

# Eager Loading (Good)
items = db.query(Item).options(joinedload(Item.category)).all()
```

### API Optimization

- **Pagination**: Limit result sets
- **Field Selection**: Return only needed fields
- **Compression**: Gzip response compression
- **Caching Headers**: ETag, Cache-Control

---

## 🧪 Testing Strategy (To Be Implemented)

### Test Pyramid

```
    ┌─────────────┐
    │   E2E Tests │ (Few)
    ├─────────────┤
    │  Integration│ (Some)
    │    Tests    │
    ├─────────────┤
    │   Unit Tests│ (Many)
    └─────────────┘
```

### Recommended Tools

- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **httpx**: API testing client
- **faker**: Test data generation

---

## 🔗 Related Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Database Schema](./DATABASE_SCHEMA.md)
- [Development Guide](./DEVELOPMENT_GUIDE.md)
- [Setup Guide](../README.md)

---

> Last Updated: October 11, 2025
