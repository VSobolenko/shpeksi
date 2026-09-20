# Pikupo — Backend

Self-hosted backend for the **self-pickup** food-ordering platform.

Serves the GraphQL contract used by the `Admin Dashboard` and `CustomerApp`
frontends over **HTTP + WebSocket** at `/graphql`, matching the operation/field
names fixed by those frontends (snake_case fields, `_id`, JWT bearer auth).

## Stack

- **FastAPI** (ASGI) + **Uvicorn**
- **Strawberry GraphQL** (code-first, async, subscriptions)
- **MongoDB** + **Beanie** (Motor + Pydantic v2)
- **Redis** (optional; in-memory pub/sub is used when `REDIS_URL` is empty)
- **python-jose** (JWT) + **bcrypt** (password hashing)
- **Stripe** + **PayPal** (payments), **firebase-admin** (FCM push), **aiosmtplib** (email)

Both WebSocket subscription protocols are supported on the same endpoint:
`graphql-transport-ws` (new) and `graphql-ws` / `subscriptions-transport-ws` (legacy).

## Setup

```bash
cd backend
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # then edit .env with your Mongo URL, JWT secret, admin creds
```

Prereqs: Python 3.11+ and a running MongoDB (default `mongodb://localhost:27017`).

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

GraphQL endpoint: `http://localhost:8000/graphql` (GraphiQL available in dev).

## Configuration

All configuration is read from `.env` (see `.env.example`). Business settings
(Stripe keys, PayPal keys, SMTP, currency) are stored in the `configuration`
singleton document and managed through the admin GraphQL mutations.

## Production deployment

The stack ships a non-root `Dockerfile` and `docker-compose.yml` that start the
app with **authenticated** MongoDB and Redis, a **Caddy** TLS reverse proxy
(automatic HTTPS via Let's Encrypt), a scheduled **MongoDB backup** service, and
healthchecks. CORS origins, log level, and all secrets come from environment.

In production the app refuses to start with placeholder secrets (`change-me`) or
unauthenticated data stores (fail-fast).

Full instructions — provisioning, cutover, updates, backups/restore, rollback,
and monitoring — are in [`DEPLOY.md`](DEPLOY.md).
