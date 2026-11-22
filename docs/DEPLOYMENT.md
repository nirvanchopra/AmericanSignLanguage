# SignBridge AI — Production Deployment Guide

## 1. Quick Start (Local Development)

The fastest way to launch the entire platform is with the unified runner:

```bash
# 1. Activate virtual environment
.v\Scripts\activate

# 2. Run both Backend and Frontend concurrently
python run_signbridge.py
```
- **Backend API & Swagger**: `http://localhost:8000/docs`
- **Frontend Web Studio**: `http://localhost:3000`

---

## 2. Docker Compose Deployment (Production)

The system includes a production-ready `docker-compose.yml` orchestrating PostgreSQL 16, Redis 7, FastAPI Backend, and Nginx Frontend:

```bash
# Build and start all 4 containers
docker compose up -d --build

# View container logs
docker compose logs -f backend

# Verify health status
docker compose ps
```

---

## 3. Environment Variables Configuration

Create a `.env` file in the `backend/` directory based on the template below:

```ini
# Application
PROJECT_NAME="SignBridge AI"
VERSION="1.0.0"

# Security
SECRET_KEY="replace-with-a-64-char-random-string-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database
# For Local SQLite:
DATABASE_URL="sqlite+aiosqlite:///./signbridge.db"
# For Production PostgreSQL:
# DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/signbridge"

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
```
