# Shura Task & Follow-up Management System

Angular 19 + FastAPI + Supabase PostgreSQL

## Windows Setup (PowerShell)

### 1. Backend

```powershell
cd D:\shura-task-system\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
copy .env.example .env
notepad .env
```

Edit `.env` carefully:

1. Open Supabase → Project Settings → Database
2. Use **Connection pooling** (Session or Transaction)
3. Username format: `postgres.PROJECT_REF` (example: `postgres.uezgsfsmtbphunhfiznr`)
4. Host: `aws-0-....pooler.supabase.com` (NOT `db.xxx.supabase.co` if DNS fails)
5. If password contains `@`, replace with `%40`

Example:

```env
DATABASE_URL=postgresql+asyncpg://postgres.uezgsfsmtbphunhfiznr:YOUR_PASS@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
```

```powershell
pip install -r requirements.txt
python test_db.py
uvicorn app.main:app --reload --port 8000
python seed_data.py
```

Swagger: http://127.0.0.1:8000/docs

Demo logins after seed:
- admin@shura.local / admin123
- shura@shura.local / shura123
- assistant@shura.local / assistant123
- ahmed@shura.local / helper123

### 2. Frontend

```powershell
cd D:\shura-task-system\frontend
npm install
npm start
```

Open http://localhost:4200

## Project Ref

Your project ref is in the Supabase URL:
`https://uezgsfsmtbphunhfiznr.supabase.co` → ref = `uezgsfsmtbphunhfiznr`

Pooler username = `postgres.` + ref = `postgres.uezgsfsmtbphunhfiznr`

## API

All routes under `/api/v1` — see Swagger at `/docs`
