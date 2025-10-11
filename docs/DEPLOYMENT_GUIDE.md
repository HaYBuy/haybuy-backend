# 🚀 Deployment Guide - HaYBuy Backend

## 📖 Table of Contents

- [Overview](#overview)
- [Pre-deployment Checklist](#pre-deployment-checklist)
- [Production Environment Setup](#production-environment-setup)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment Options](#cloud-deployment-options)
- [CI/CD with Jenkins](#cicd-with-jenkins)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)

---

## 🎯 Overview

This guide covers deploying HaYBuy Backend to production environments.

---

## ✅ Pre-deployment Checklist

### Security

- [ ] Change all default passwords
- [ ] Generate new JWT_SECRET_KEY
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS properly (no wildcards)
- [ ] Enable firewall rules
- [ ] Set up rate limiting
- [ ] Review environment variables

### Database

- [ ] Set up production database
- [ ] Configure database backups
- [ ] Set up connection pooling
- [ ] Create database indexes
- [ ] Test database migrations

### Application

- [ ] Set DEBUG=False
- [ ] Configure proper logging
- [ ] Set up error monitoring
- [ ] Test all endpoints
- [ ] Review security settings
- [ ] Optimize Docker image size

### Infrastructure

- [ ] Set up load balancer (if needed)
- [ ] Configure auto-scaling
- [ ] Set up monitoring
- [ ] Configure alerts
- [ ] Test disaster recovery

---

## 🌍 Production Environment Setup

### 1. Environment Variables

Create production `.env`:

```env
# Production Database
POSTGRES_USER=haybuy_prod
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=haybuy_production
DATABASE_URL=postgresql+psycopg2://haybuy_prod:<password>@db:5432/haybuy_production

# JWT (Generate new key!)
JWT_SECRET_KEY=<generate-new-secret-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=False
ENVIRONMENT=production
RUNNING_IN_DOCKER=true

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Server
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=WARNING
```

### 2. Generate Secure Keys

```bash
# Generate JWT secret
openssl rand -hex 32

# Generate database password
openssl rand -base64 32
```

---

## 🐳 Docker Deployment

### Production Dockerfile

Create `Dockerfile.prod`:

```dockerfile
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY ./app ./app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: "3.8"

services:
  db:
    image: postgres:16-alpine
    container_name: haybuy-db-prod
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - haybuy-network

  api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: haybuy-api-prod
    restart: always
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"
    networks:
      - haybuy-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: haybuy-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - haybuy-network

volumes:
  postgres_data:

networks:
  haybuy-network:
    driver: bridge
```

### Deploy with Docker Compose

```bash
# Build and start
docker compose -f docker-compose.prod.yml up -d --build

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Stop services
docker compose -f docker-compose.prod.yml down

# Update application
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

---

## ☁️ Cloud Deployment Options

### 1. AWS Deployment

#### Using AWS ECS (Elastic Container Service)

```bash
# Install AWS CLI
pip install awscli

# Configure AWS
aws configure

# Create ECR repository
aws ecr create-repository --repository-name haybuy-backend

# Build and push image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t haybuy-backend -f Dockerfile.prod .
docker tag haybuy-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/haybuy-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/haybuy-backend:latest
```

#### Using AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker haybuy-backend

# Create environment
eb create haybuy-prod

# Deploy
eb deploy
```

### 2. Google Cloud Platform (GCP)

#### Using Google Cloud Run

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/haybuy-backend
gcloud run deploy haybuy-backend \
  --image gcr.io/YOUR_PROJECT_ID/haybuy-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 3. Azure

#### Using Azure Container Instances

```bash
# Install Azure CLI
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login
az login

# Create resource group
az group create --name haybuy-rg --location eastus

# Create container registry
az acr create --resource-group haybuy-rg --name haybuyregistry --sku Basic

# Build and push
az acr build --registry haybuyregistry --image haybuy-backend:latest .

# Deploy
az container create \
  --resource-group haybuy-rg \
  --name haybuy-backend \
  --image haybuyregistry.azurecr.io/haybuy-backend:latest \
  --dns-name-label haybuy-backend \
  --ports 8000
```

### 4. DigitalOcean

#### Using App Platform

```bash
# Create app via CLI or web interface
doctl apps create --spec app-spec.yaml

# app-spec.yaml example:
name: haybuy-backend
services:
  - name: api
    dockerfile_path: Dockerfile.prod
    source_dir: /
    github:
      repo: HaYBuy/haybuy-backend
      branch: main
    envs:
      - key: DATABASE_URL
        value: ${db.DATABASE_URL}
databases:
  - name: db
    engine: PG
    version: "16"
```

---

## 🔄 CI/CD with Jenkins

### Jenkinsfile

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'haybuy-backend'
        DOCKER_TAG = "${BUILD_NUMBER}"
        REGISTRY = 'your-registry.com'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}", "-f Dockerfile.prod .")
                }
            }
        }

        stage('Test') {
            steps {
                sh '''
                    docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} pytest
                '''
            }
        }

        stage('Push to Registry') {
            steps {
                script {
                    docker.withRegistry("https://${REGISTRY}", 'docker-credentials') {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push('latest')
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    ssh user@production-server "
                        cd /opt/haybuy-backend &&
                        docker compose -f docker-compose.prod.yml pull &&
                        docker compose -f docker-compose.prod.yml up -d
                    "
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
```

---

## 📊 Monitoring and Logging

### 1. Application Logging

Update `app/main.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=10),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 2. Prometheus Metrics

```bash
# Add to requirements.txt
prometheus-client>=0.18.0

# Add to app
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_latency = Histogram('http_request_duration_seconds', 'HTTP request latency')
```

### 3. Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## 💾 Backup and Recovery

### Database Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="haybuy_backup_${TIMESTAMP}.sql"

# Create backup
docker exec haybuy-db-prod pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > ${BACKUP_DIR}/${BACKUP_FILE}

# Compress
gzip ${BACKUP_DIR}/${BACKUP_FILE}

# Keep only last 7 days
find ${BACKUP_DIR} -name "haybuy_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

### Restore Database

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1

gunzip -c ${BACKUP_FILE} | docker exec -i haybuy-db-prod psql -U ${POSTGRES_USER} ${POSTGRES_DB}

echo "Database restored from ${BACKUP_FILE}"
```

### Automated Backups with Cron

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/haybuy-backend/scripts/backup.sh
```

---

## 🔗 Related Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Architecture Guide](./ARCHITECTURE.md)
- [Development Guide](../README.md)

---

> Last Updated: October 11, 2025
