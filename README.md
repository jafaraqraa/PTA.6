# PTA Simulator SaaS Platform

## Overview
PTA Simulator is a SaaS platform for audiometry training. It supports multi-tenant isolation, Role-Based Access Control (RBAC), and domain-based access.

### Key Features
- **Multi-Tenant Isolation**: Each university has its own domain and data isolation.
- **RBAC**: Supports Super Admin, University Admin, Lab Admin, and Student roles.
- **Domain-Based Access**: Automatic university detection based on the request domain.
- **Subscription Validation**: Enforces active subscriptions for university access.

## Setup Instructions

### 1. Environment Setup
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r backend/requirements.txt
```

### 2. Environment Variables
Create a `backend/.env` file:
```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=yoursecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### 3. Database Migrations
```bash
cd backend
alembic upgrade head
```

### 4. Seed Demo Data
```bash
cd backend
export PYTHONPATH=$PYTHONPATH:.
python scripts/seed.py
python scripts/import_patients_json.py data/test_patient.json
```

### 5. Run the Server
```bash
cd backend
python -m uvicorn app.main:app --reload
```

## How to Login
1. Open the domain (e.g., `najah.localhost:8000` or use `?domain=najah` query param for testing).
2. Use the demo accounts below.

### Demo Accounts
| Role | Email | Password | Domain |
|------|-------|----------|--------|
| Super Admin | admin@system.com | admin123 | any |
| University Admin | admin@najah.com | 123456 | najah |
| Lab Admin | lab@najah.com | 123456 | najah |
| Student | student@najah.com | 123456 | najah |

## API Examples

### Login
**POST** `/auth/login?domain=najah`
```json
{
  "email": "student@najah.com",
  "password": "123456"
}
```
**Response:**
```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

## Important Notes
- **Domain Required**: The system extracts the university from the subdomain or `domain` query parameter.
- **Subscription Required**: Universities must have an active subscription to allow access to non-super-admin users.
- **RBAC Enforced**: Access to specific features is restricted based on user roles.
