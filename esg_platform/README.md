# ESG Emissions Ingestion & Analyst Review Platform

A production-grade Django + React platform that ingests emissions and activity data from enterprise systems, normalizes it, flags suspicious records, and lets analysts review and approve data before it is audit-locked.

---

## Live Demo

> Deploy to Render/Railway using the Docker setup below.

**Local credentials:**
- Admin: `admin@esg.local` / `Admin123!`
- Analyst: `test@gmail.com` / `Test123!test`

---

## Architecture

```
esg_platform/
├── backend/                  Django REST Framework API
│   ├── apps/
│   │   ├── accounts/         Custom user model, JWT auth, RBAC
│   │   ├── organizations/    Multi-tenant: Org → Facility → Department
│   │   ├── ingestion/        Upload batches, raw record storage, parsers
│   │   │   └── parsers/      SAP, Utility, Travel CSV/Excel parsers
│   │   ├── normalization/    Transformation engine, emission factors, CO2e
│   │   ├── audit/            Immutable audit log, middleware
│   │   ├── analytics/        Dashboard widgets, charts, trend APIs
│   │   └── review/           Approval workflow proxy
│   └── config/               Django settings, URLs, Celery, WSGI
├── frontend/                 React + TypeScript + Bootstrap
│   └── src/
│       ├── pages/            Dashboard, Review, Upload, Audit
│       ├── hooks/            React Query hooks per domain
│       ├── services/api/     Axios service layer
│       ├── context/          Auth context (JWT storage)
│       └── types/            TypeScript interfaces
└── nginx/                    Reverse proxy config
```

---

## Quick Start (Local)

```bash
# Backend
cd esg_platform/backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser --email admin@esg.local
python manage.py runserver 8001

# Frontend (separate terminal)
cd esg_platform/frontend
npm install
npm run dev
```

Frontend: http://localhost:3000  
Backend API: http://localhost:8001/api/  
API Docs: http://localhost:8001/api/docs/

---

## Docker Deployment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your values
docker compose up --build
```

---

## Key Features

### Data Ingestion
- **SAP flat-file CSV/Excel** — handles German column names (`Menge`, `Buchungsdatum`, `Kostenstelle`), mixed date formats, inconsistent units
- **Utility electricity portal CSV** — billing period normalization, kWh/MWh/GWh conversion, meter ID tracking
- **Corporate travel CSV** — IATA airport code validation, distance-based emission factors, cabin class multipliers

### Normalization Engine
- Unit conversion to SI: liters, kWh, km
- Date parsing: 10+ formats including German DD.MM.YYYY
- Scope assignment: Scope 1 (fuel combustion), Scope 2 (electricity), Scope 3 (procurement, travel)
- CO2e calculation using DEFRA 2023 / CEA 2023 emission factors
- Suspicious data detection: negative values, zero values, future dates, extreme outliers
- Duplicate detection across batches
- Full transformation log per record (lineage)

### Analyst Review Dashboard
- Status widgets: total, pending, suspicious, flagged, approved, rejected, locked
- Filterable table: by scope, source, status, date range, vendor
- Row detail drawer: raw data, transformation log, decision history
- Approve / Reject / Flag with mandatory comment
- Bulk actions on selected rows
- Audit-locked records are immutable after approval

### Audit Trail
- Every API mutation logged to `AuditLog` (append-only)
- Before/after values stored
- IP address, user, timestamp, resource type

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | JWT login |
| POST | `/api/auth/register/` | Register (analyst role) |
| GET | `/api/analytics/dashboard/` | Dashboard widget data |
| GET | `/api/analytics/emissions/monthly/` | Monthly trend chart |
| POST | `/api/ingestion/batches/` | Upload CSV/Excel file |
| GET | `/api/ingestion/template/{sap\|utility\|travel}/` | Download sample template |
| GET | `/api/normalization/records/` | List records with filters |
| POST | `/api/normalization/records/{id}/approve/` | Approve record |
| POST | `/api/normalization/records/{id}/reject/` | Reject record |
| POST | `/api/normalization/records/bulk-action/` | Bulk approve/reject |
| GET | `/api/audit/logs/` | Audit trail |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.0, Django REST Framework 3.15 |
| Auth | Simple JWT (access + refresh, blacklist) |
| Database | MySQL 8 (SQLite for local dev) |
| Task Queue | Celery + Redis |
| Frontend | React 18, TypeScript, Bootstrap 5 |
| State | React Query (server), Context API (auth) |
| HTTP | Axios with auto token refresh |
| Charts | Recharts |
| Proxy | Nginx |
| Container | Docker + Docker Compose |
