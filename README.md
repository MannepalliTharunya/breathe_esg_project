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
3. Frontend is built with `VITE_API_BASE_URL` pointing to the backend<img width="1897" height="914" alt="Screenshot 2026-05-29 225857" src="https://github.com/user-attachments/assets/b8b1f413-16be-4c44-90e1-8b6fbf27741d" />

## API Documentation
Swagger UI available at `/api/docs/` on the running backend.
<img width="1919" height="891" alt="Screenshot 2026-05-29 225847" src="https://github.com/user-attachments/assets/f11939f8-f395-46b5-9348-bd045ac74f1b" />
<img width="1897" height="914" alt="Screenshot 2026-05-29 225857" src="https://github.com/user-attachments/assets/b5132889-eea9-40e6-8e84-27d3cc3b7135" />
<img width="1914" height="916" alt="Screenshot 2026-05-29 225954" src="https://github.com/user-attachments/assets/0c85bf3c-a35b-4f33-971d-4fce3ecf78d1" />
<img width="1918" height="900" alt="Screenshot 2026-05-29 230003" src="https://github.com/user-attachments/assets/6d780a5e-2000-472c-a0ae-2d840963d807" />
<img width="1919" height="914" alt="Screenshot 2026-05-29 230013" src="https://github.com/user-attachments/assets/685f5a8b-b6b6-4e91-902f-91cde598e815" />

<img width="1919" height="900" alt="Screenshot 2026-05-29 230023" src="https://github.com/user-attachments/assets/ea68a573-af2d-41fe-81fd-dbeae1bbf9e1" />
<img width="1918" height="874" alt="Screenshot 2026-05-29 230037" src="https://github.com/user-attachments/assets/64fa3278-5e6d-495f-99ce-cc3e10db72aa" />
<img width="1919" height="918" alt="Screenshot 2026-05-29 230053" src="https://github.com/user-attachments/assets/827bdc9b-cfd5-4102-a424-910dd3cc1098" />
<img width="1919" height="879" alt="Screenshot 2026-05-29 230100" src="https://github.com/user-attachments/assets/964bbe4f-541f-4789-8055-2f570a979f38" />
<img width="1919" height="869" alt="Screenshot 2026-05-29 230106" src="https://github.com/user-attachments/assets/37122988-b1bb-43c5-b7f9-853462bff0b2" />
<img width="1912" height="861" alt="Screenshot 2026-05-29 230112" src="https://github.com/user-attachments/assets/499791b0-ee1f-4a80-aa88-99c4088d455f" />
<img width="1919" height="900" alt="Screenshot 2026-05-29 230118" src="https://github.com/user-attachments/assets/4b356fa2-1854-4a91-8345-c6fa6fad979b" />
<img width="1919" height="901" alt="Screenshot 2026-05-29 230127" src="https://github.com/user-attachments/assets/ea6d83c7-e3f9-4400-8444-9f6f32a8fa91" />
<img width="1914" height="887" alt="Screenshot 2026-05-29 230134" src="https://github.com/user-attachments/assets/e421fcb7-7d8a-4bfb-875a-6d7b3e32592b" />





























<img width="1919" height="914" alt="Screenshot 2026-05-29 230013" src="https://github.com/user-attachments/assets/3172d315-3220-4faf-aa9d-cc45db6651f2" />
<img width="1918" height="900" alt="Screenshot 2026-05-29 230003" src="https://github.com/user-attachments/assets/de3520ca-7efb-4664-b30e-50847b68515a" />
<img width="1914" height="916" alt="Screenshot 2026-05-29 225954" src="https://github.com/user-attachments/assets/ce119cd6-2624-43ee-8126-4ac27572842d" />
![Uploading Screenshot 2026-05-29 225857.png…]()
