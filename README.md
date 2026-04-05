# PTA Simulator SaaS Platform

## Overview
PTA Simulator is a SaaS platform for audiometry training. It supports multi-tenant isolation, Role-Based Access Control (RBAC), and domain-based access.

### Key Features
- **Multi-Tenant Isolation**: Each university has its own domain and data isolation.
- **RBAC**: Supports Super Admin, University Admin, Lab Admin, and Student roles.
- **Domain-Based Access**: Automatic university detection based on the request domain.
- **Subscription Validation**: Enforces active subscriptions for university access.

## Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
# If you encounter bcrypt issues: pip install bcrypt==4.0.1

alembic upgrade head
export PYTHONPATH=.
python scripts/seed.py
python scripts/import_patients_json.py data/test_patient.json

python -m uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Local Development & Testing

### University Domain Testing
The system detects the university context from the subdomain or a `domain` query parameter.

For local testing, you can use:
- **Subdomain**: `http://najah.localhost:5173`
- **Query Param**: `http://localhost:5173?domain=najah`

**Note**: If you use `localhost` directly without a query parameter, domain detection will fail on the login page.

### Demo Accounts
| Role | Email | Password | Domain |
|------|-------|----------|--------|
| Super Admin | admin@system.com | admin123 | any |
| University Admin | admin@najah.com | 123456 | najah |
| Lab Admin | lab@najah.com | 123456 | najah |
| Student | student@najah.com | 123456 | najah |

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=yoursecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
```

## API Endpoints
- `POST /auth/login`: Authenticate and get JWT.
- `POST /sessions/startSession`: Start a new simulation.
- `POST /sessions/playTone`: Play a tone and get patient response.
- `POST /sessions/storeTone`: Store a detected threshold.
- `POST /sessions/endSession`: End simulation and get evaluation.

## Important Notes
- **Domain Detection**: The frontend automatically extracts the university domain and sends it to the backend.
- **Subscription**: Users (except Super Admin) can only log in if their university has an active subscription.
- **RBAC**: UI elements and navigation items are shown/hidden based on the user's role.
