# Fuqarolar Monitoring Platformasi — Backend

GovTech civic monitoring system for schools and kindergartens in Uzbekistan.

## Tech Stack
- Django 4.2 + DRF 3.14
- PostgreSQL 15
- Redis 7 (Cache + Rate limiting)
- Celery + Celery Beat (Queue)
- Docker + docker-compose

## Local Setup

1. **Clone the repository**
2. **Create .env file**
   ```bash
   cp .env.example .env
   ```
3. **Run with Docker**
   ```bash
   docker-compose up --build
   ```
4. **Access the API**
   - API Base: `http://localhost:8000/api/v1/`
   - Swagger Docs: `http://localhost:8000/api/docs/`
   - Redoc: `http://localhost:8000/api/redoc/`

## API Endpoints Summary

### Auth
- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/`
- `GET /api/v1/auth/me/`

### Institutions
- `GET /api/v1/institutions/`
- `GET /api/v1/institutions/{id}/`
- `GET /api/v1/institutions/regions/`

### Reports & Problems
- `POST /api/v1/reports/` - Submit verification of a promise
- `POST /api/v1/problems/` - Report a new problem
- `POST /api/v1/reports/{id}/verify/` - Verify another user's report

### Dashboard
- `GET /api/v1/dashboard/stats/`
- `GET /api/v1/dashboard/map/`

## Manual GeoASR Sync
To manually trigger a sync from terminal:
```bash
docker-compose exec web python manage.py shell -c "from integrations.geoasr.sync import GeoASRSyncService; GeoASRSyncService.sync_all()"
```

## Running Tests
```bash
docker-compose exec web pytest
```
