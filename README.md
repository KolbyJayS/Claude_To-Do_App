# Claude To-Do App

Full-stack todo application with JWT auth, PostgreSQL persistence, and Redis caching.

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 18 + Vite + Tailwind CSS + React Router |
| Backend | Python Flask (raw psycopg2, no ORM) |
| Database | PostgreSQL (Supabase) |
| Cache | Redis (Upstash) — cache-aside on todo reads |
| Auth | Roll-your-own JWT (bcrypt passwords, access + refresh tokens) |
| Migrations | Alembic with raw `op.execute()` SQL — no SQLAlchemy models |
| CI | GitHub Actions (lint + build + migration smoke test) |
| Deploy | Vercel (frontend static + Flask serverless) |

## Local development

### Prerequisites
- Python 3.12+, Node 20+
- PostgreSQL instance (local or Supabase)
- Redis instance (local or Upstash)

### Backend

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # fill in DATABASE_URL, REDIS_URL, JWT_SECRET

# Run DB migrations first
alembic upgrade head

# Start Flask dev server
python api/index.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api/*` to `localhost:5000` automatically.

### Environment variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | `postgresql://user:pass@host/db` |
| `REDIS_URL` | `redis://...` or `rediss://...` (Upstash) |
| `JWT_SECRET` | Random secret string, keep it secret |
| `CORS_ORIGINS` | Comma-separated allowed origins |

## Architecture

```
Browser → React → Flask API → Redis (cache check)
                           ↓ (miss)
                        Postgres → Redis (populate) → response
```

Todo list reads: check Redis first (120s TTL), fall back to PG on miss.  
Todo writes: write to PG, then invalidate Redis key.  
Auth: bcrypt password hash in PG, JWT access (1hr) + refresh (7d) tokens, refresh token in httpOnly cookie.

## Deployment (Vercel)

1. Connect repo to Vercel
2. Set env vars in Vercel dashboard
3. Push to `main` — Vercel builds frontend + deploys Flask as a serverless function
4. Run `alembic upgrade head` once against production DB (or add it to a pre-deploy hook)
