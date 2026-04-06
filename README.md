# PTA Simulator SaaS Platform

## Overview
PTA Simulator is a SaaS platform for audiometry training. It supports multi-tenant isolation, Role-Based Access Control (RBAC), and email-based university access.

### Key Features
- **Multi-Tenant Isolation**: Users are isolated based on their university assignment.
- **RBAC**: Supports Super Admin, University Admin, Lab Admin, and Student roles.
- **Email-Based Access**: Login using email and password; university context is automatically derived from the user profile.
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

# New setup script (recommended)
python scripts/setup.py

# Manual steps
alembic upgrade head
export PYTHONPATH=.
python scripts/seed.py

# Import patient data
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

### Authentication
The system uses email-based login. There is no need for subdomains or domain query parameters. Simply log in with your email and password.

### Demo Accounts
| Role | Email | Password | University |
|------|-------|----------|------------|
| Super Admin | admin@system.com | admin123 | System |
| University Admin | admin@najah.com | 123456 | An-Najah |
| Lab Admin | lab@najah.com | 123456 | An-Najah |
| Student | student@najah.com | 123456 | An-Najah |

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
- **User Context**: The system automatically identifies the user's university from their profile upon login.
- **Subscription**: Users (except Super Admin) can only log in if their university has an active subscription.
- **RBAC**: UI elements and navigation items are shown/hidden based on the user's role.
