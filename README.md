# ESG Platform

A full-stack ESG (Environmental, Social, Governance) data management and reporting platform.

**Live Demo**
- Frontend: https://breathe-esg-project-3.onrender.com
- Backend API: https://breathe-esg-project-2-jwck.onrender.com/api/v1/
- API Docs: https://breathe-esg-project-2-jwck.onrender.com/api/docs/

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Tailwind CSS + Vite |
| State | Zustand + React Query |
| Backend | Django 5 + Django REST Framework |
| Auth | Simple JWT (access + refresh tokens, blacklist) |
| Database | PostgreSQL |
| Cache / Queue | Redis + Celery + Celery Beat |
| Reports | ReportLab (PDF) + Pandas |
| Deployment | Render (backend + frontend + PostgreSQL + Redis) |

## Project Structure

```
breathe_esg_project/
├── backend/
│   ├── apps/
│   │   ├── core/          # Base models, pagination, permissions
│   │   ├── users/         # Custom user model, JWT auth
│   │   ├── organizations/ # Multi-tenant orgs, facilities, memberships
│   │   ├── esg_data/      # Metrics, data points, targets
│   │   ├── reports/       # Async PDF report generation
│   │   ├── frameworks/    # ESG framework catalogue (GRI, TCFD, SASB, CSRD)
│   │   ├── audit/         # Immutable audit log
│   │   ├── notifications/ # In-app notifications
│   │   └── integrations/  # External data connectors
│   └── config/
│       └── settings/      # base / local / production
├── frontend/
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       ├── services/api/
│       ├── store/
│       └── types/
├── docker-compose.yml
└── render.yaml
```

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate --settings=config.settings.local
python manage.py seed_esg_data --settings=config.settings.local
python manage.py runserver --settings=config.settings.local
```

API runs at http://127.0.0.1:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

> Local settings use SQLite — no PostgreSQL or Redis needed.

## Key Features

- Metric catalogue with GRI / TCFD / SASB / CSRD framework mappings
- Multi-step approval workflow: Draft → Submitted → Under Review → Approved → Published
- Bulk CSV/Excel import with field mapping
- Async PDF report generation (GRI, TCFD, SASB, CDP, CSRD)
- Multi-tenant: organization-scoped data via `X-Organization-Id` header
- Role-based access: Owner, Admin, ESG Manager, Analyst, Viewer, Auditor
- JWT with silent refresh and token blacklisting
- Immutable audit log for all data mutations

## Environment Variables

See `backend/.env.example` and `frontend/.env.example` for all required variables.

Key backend vars for production:
- `DATABASE_URL` — PostgreSQL connection string (auto-injected by Render)
- `DJANGO_SECRET_KEY` — secret key
- `DJANGO_ALLOWED_HOSTS` — comma-separated allowed hosts
- `DJANGO_CORS_ALLOWED_ORIGINS` — frontend URL(s)
- `REDIS_URL` — Redis connection string

## Deployment (Render)

The `render.yaml` defines all services. On first deploy:
1. Render provisions PostgreSQL and Redis automatically
2. Backend runs `migrate`, `create_default_superuser`, and `seed_esg_data` on startup
3. Frontend is built with `VITE_API_BASE_URL` pointing to the backend

## API Documentation

Swagger UI available at `/api/docs/` on the running backend.
