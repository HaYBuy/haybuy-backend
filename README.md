# � HaYBuy Backend - Complete Documentation

> A modern, scalable RESTful API backend for HaYBuy e-commerce platform

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 📚 Documentation Index

### Quick Links

- **[API Documentation](./docs/API_DOCUMENTATION.md)** - Complete API endpoint reference
- **[Database Schema](./docs/DATABASE_SCHEMA.md)** - Database structure and relationships
- **[Architecture Guide](./docs/ARCHITECTURE.md)** - System design and patterns
- **[Development Guide](#-development-guide)** - Setup and development workflow

---

## 🎯 Project Overview

HaYBuy Backend is a comprehensive e-commerce API platform built with modern Python technologies, featuring:

### 🌟 Key Features

- ✅ **User Management** - Registration, authentication, profiles
- ✅ **Product Management** - Items, categories, wish lists
- ✅ **Group Shopping** - Create groups, manage members, shared shopping
- ✅ **Transaction System** - Order processing and tracking
- ✅ **Price History** - Track price changes over time
- ✅ **Geographic Support** - Location-based features with GIS
- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **RESTful API** - Standard HTTP methods and status codes

### 🛠️ Technology Stack

- **FastAPI (Python 3.13)** - Modern, fast web framework
- **PostgreSQL 16** - Robust relational database
- **SQLAlchemy 2.0+** - Powerful ORM
- **Docker & Docker Compose** - Containerization
- **JWT + bcrypt** - Authentication & security
- **Pydantic** - Data validation
- **GeoAlchemy2** - Geographic data support

---

## ⚙️ Prerequisites

Make sure the following are installed on your system:

| Tool                | Recommended Version          | Notes                                    |
| ------------------- | ---------------------------- | ---------------------------------------- |
| Docker Desktop      | ≥ 4.31                       | Required for running containers          |
| Docker Compose (v2) | Built-in with Docker Desktop | Check via `docker compose version`       |
| Python              | ≥ 3.13                       | Optional (for local runs without Docker) |
| Git                 | ≥ 2.40                       | For source control                       |

---

## 🚀 Quick Start (Docker Compose)

1. **Clone the repository**

   ```bash
   git clone https://github.com/HaYBuy/haybuy-backend.git
   cd haybuy-backend
   ```

2. **Create the environment file**

   ```bash
   cp .env.example .env
   ```

   Update variables as needed:

   ```env
   POSTGRES_USER=admin
   POSTGRES_PASSWORD=admin
   POSTGRES_DB=haybuy_db
   JWT_SECRET_KEY=your_secret_key
   ```

3. **Build and start the containers**

   ```bash
   docker compose up -d --build
   ```

4. **Check logs**

   ```bash
   docker compose logs -f db
   docker compose logs -f api
   ```

5. **Open the API**
   - Swagger UI → [http://localhost:8000/docs](http://localhost:8000/docs)
   - Redoc → [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧩 Live Reload (Development Mode)

When actively developing the backend, use live reload to auto-restart FastAPI when code changes.

### Create `docker-compose.dev.yml`

```yaml
services:
  api:
    volumes:
      - .:/app
    command:
      [
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
      ]
```

### Run in dev mode

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

You should see:

```
Uvicorn running on http://0.0.0.0:8000 (Reload)
```

Every time you edit files in your local machine, the API inside Docker will reload automatically.

---

## 🧱 Project Structure

```
haybuy-backend/
│
├── app/
│   ├── main.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   └── ...
│
├── Dockerfile
├── docker-compose.yml
├── docker-compose.dev.yml
├── requirements.txt
├── .env
└── DEVELOPMENT_GUIDE.md
```

---

## 🐘 Database (PostgreSQL)

To connect from your local machine:

```bash
psql -h localhost -p 5432 -U admin -d haybuy_db
```

Default credentials (from `.env`):

```
User: admin
Password: admin
Database: haybuy_db
```

---

## 🧪 Running Tests (Optional)

If `pytest` is configured inside the image:

```bash
docker compose exec api pytest -v
```

To view coverage:

```bash
docker compose exec api pytest --cov=app --cov-report=term-missing
```

---

## 🧹 Useful Commands

| Command                                         | Description           |
| ----------------------------------------------- | --------------------- |
| `docker compose up -d`                          | Start containers      |
| `docker compose down`                           | Stop containers       |
| `docker compose logs -f api`                    | View FastAPI logs     |
| `docker compose exec api bash`                  | Enter API container   |
| `docker volume rm haybuy-backend_haybuy_pgdata` | Reset DB data         |
| `docker system prune -a`                        | Clean up Docker cache |

---

## 🧠 Tips

- Use `--no-cache` when rebuilding after changing `requirements.txt`  
  → `docker compose build --no-cache`
- Always check container logs if a service doesn't start
- Keep your `.env` and database credentials private
- In production, disable `--reload` and use `gunicorn` instead of `uvicorn`

---

## 📖 Full Documentation

For comprehensive documentation, please refer to:

### Core Documentation

- **[API Documentation](./docs/API_DOCUMENTATION.md)**

  - All API endpoints
  - Request/response examples
  - Authentication guide
  - Error handling

- **[Database Schema](./docs/DATABASE_SCHEMA.md)**

  - Complete table definitions
  - Relationships and foreign keys
  - Indexes and constraints
  - ER diagrams

- **[Architecture Guide](./docs/ARCHITECTURE.md)**
  - System architecture
  - Design patterns
  - Security architecture
  - Scalability considerations

### API Endpoints Overview

| Category          | Endpoints             | Description             |
| ----------------- | --------------------- | ----------------------- |
| **Auth**          | `/v1/auth/*`          | Login, token management |
| **Users**         | `/v1/users/*`         | User CRUD operations    |
| **Profiles**      | `/v1/profiles/*`      | User profile management |
| **Items**         | `/v1/items/*`         | Product management      |
| **Categories**    | `/v1/categories/*`    | Category management     |
| **Wish Lists**    | `/v1/wish-items/*`    | User wish lists         |
| **Groups**        | `/v1/groups/*`        | Group management        |
| **Group Members** | `/v1/group-members/*` | Member management       |
| **Group Items**   | `/v1/group-items/*`   | Group shopping lists    |
| **Transactions**  | `/v1/transactions/*`  | Order processing        |

### Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤝 Contributing

### Development Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Write/update tests
4. Update documentation
5. Create a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions/classes
- Keep functions small and focused

---

## 📄 License

This project is proprietary software developed for HaYBuy.

---

## 👥 Authors

- **Charif** - hifrook.zen5@gmail.com
- **Adithep** - adithepbaebmueann@gmail.com

---

## 📞 Support

For issues and questions:

- Create an issue in the repository
- Contact the development team
- Check the documentation

---

## 🗺️ Roadmap

### Planned Features

- [ ] Payment gateway integration
- [ ] Email notifications
- [ ] Real-time chat support
- [ ] Advanced search and filtering
- [ ] Product recommendations
- [ ] Admin dashboard
- [ ] Mobile app API optimization
- [ ] GraphQL endpoint (optional)

### Performance Improvements

- [ ] Redis caching layer
- [ ] Database query optimization
- [ ] CDN integration
- [ ] API rate limiting
- [ ] Response compression

---

> © 2025 HaYBuy Backend — Developed with ❤️ using FastAPI + PostgreSQL + Docker
