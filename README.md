# ESG Platform

Production-grade full-stack ESG (Environmental, Social, Governance) data management and reporting platform.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Tailwind CSS + Vite |
| State | Zustand (auth, org, UI) + React Query (server state) |
| Backend | Django 5 + Django REST Framework |
| Auth | Simple JWT (access + refresh tokens, blacklist) |
| Database | MySQL 8 |
| Cache / Queue | Redis + Celery + Celery Beat |
| Reports | ReportLab (PDF) + Pandas (data processing) |
| Monitoring | Sentry + Prometheus |
| Proxy | Nginx |
| Container | Docker + Docker Compose |

## Project Structure

```
esg-platform/
├── backend/
│   ├── apps/
│   │   ├── core/          # Base models, pagination, permissions, exceptions
│   │   ├── users/         # Custom user model, JWT auth, password reset
│   │   ├── organizations/ # Multi-tenant orgs, facilities, memberships
│   │   ├── esg_data/      # Metrics, data points, targets, materiality
│   │   ├── reports/       # Async PDF report generation (GRI, TCFD, SASB)
│   │   ├── frameworks/    # ESG framework catalogue (GRI, TCFD, SASB, CSRD)
│   │   ├── audit/         # Immutable audit log
│   │   ├── notifications/ # In-app + email notifications via Celery
│   │   └── integrations/  # External data source connectors
│   ├── config/
│   │   ├── settings/      # base / development / production
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── wsgi.py
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/    # UI, navigation, ESG, dashboard, notifications
│       ├── hooks/         # React Query hooks for every domain
│       ├── layouts/       # AppLayout, AuthLayout
│       ├── pages/         # Route-level page components
│       ├── services/api/  # Axios service layer
│       ├── store/         # Zustand stores (auth, org, ui)
│       ├── types/         # TypeScript interfaces
│       └── utils/         # cn, formatters, validators
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
└── Makefile
```

## Quick Start

### 1. Clone and configure environment

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit both .env files with your values
```

### 2. Start with Docker Compose

```bash
make build
make up
make migrate
make createsuperuser
```

The platform will be available at:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/api/v1/
- **API Docs**: http://localhost:8000/api/docs/
- **Admin**: http://localhost:8000/admin/

### 3. Local development (without Docker)

```bash
# Backend
make install-backend
make dev-backend

# Frontend (separate terminal)
make install-frontend
make dev-frontend
```

## Key Features

### ESG Data Management
- Metric catalogue with GRI/TCFD/SASB/CSRD framework mappings
- Multi-step approval workflow: Draft → Submitted → Under Review → Approved → Published
- Bulk import via CSV/Excel with field mapping
- Confidence scoring and data provenance tracking
- Facility-level data collection

### Reporting
- Async PDF report generation via Celery
- Supports GRI Standards, TCFD, SASB, CDP, CSRD, and custom formats
- Auto-notification when reports are ready

### Multi-tenancy
- Organization-scoped data via `X-Organization-Id` header
- Role-based access: Owner, Admin, ESG Manager, Analyst, Viewer, Auditor
- Facility management

### Security
- JWT with automatic silent refresh
- Token blacklisting on logout
- Account lockout after failed login attempts
- Immutable audit log for all mutations
- Rate limiting on auth endpoints (nginx)
- HSTS, CSP, and security headers in production

### Integrations
- REST API connector with field mapping
- SFTP connector (extensible)
- Celery-based scheduled sync

## Running Tests

```bash
make test
make test-coverage
```

## API Documentation

Interactive Swagger UI is available at `/api/docs/` when the backend is running.

## Environment Variables

See `backend/.env.example` and `frontend/.env.example` for all required variables.

## Production Deployment

1. Set `DJANGO_DEBUG=False` in `backend/.env`
2. Configure real `DJANGO_SECRET_KEY` and `JWT_SIGNING_KEY`
3. Set up SSL certificates in `nginx/ssl/`
4. Configure S3 for file storage (`USE_S3=True`)
5. Set `SENTRY_DSN` for error tracking
6. Run `make build && make up`
