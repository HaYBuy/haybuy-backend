# 🧑‍💻 HaYBuy Backend — Development Guide

This document describes how to set up and run the **HaYBuy Backend** in a local development environment using **Docker Compose**.  
It also explains how to use the **live reload (developer mode)** and how to integrate the project with **Jenkins CI/CD**.

---

## 📁 Project Overview

The backend uses:
- **FastAPI (Python 3.13)** — web framework
- **PostgreSQL** — database
- **Docker Compose** — for container orchestration
- **Jenkins** — CI/CD integration
- **Poetry / requirements.txt** — for dependency management

---

## ⚙️ Prerequisites

Make sure the following are installed on your system:

| Tool | Recommended Version | Notes |
|------|---------------------|-------|
| Docker Desktop | ≥ 4.31 | Required for running containers |
| Docker Compose (v2) | Built-in with Docker Desktop | Check via `docker compose version` |
| Python | ≥ 3.13 | Optional (for local runs without Docker) |
| Git | ≥ 2.40 | For source control |

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
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
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

| Command | Description |
|----------|-------------|
| `docker compose up -d` | Start containers |
| `docker compose down` | Stop containers |
| `docker compose logs -f api` | View FastAPI logs |
| `docker compose exec api bash` | Enter API container |
| `docker volume rm haybuy-backend_haybuy_pgdata` | Reset DB data |
| `docker system prune -a` | Clean up Docker cache |

---

## 🧠 Tips

- Use `--no-cache` when rebuilding after changing `requirements.txt`  
  → `docker compose build --no-cache`
- Always check container logs if a service doesn’t start
- Keep your `.env` and database credentials private
- In production, disable `--reload` and use `gunicorn` instead of `uvicorn`

---

> © 2025 HaYBuy Backend — Developed with ❤️ using FastAPI + PostgreSQL + Docker
