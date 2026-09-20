# Pikupo — Production Deploy Runbook

Self-hosted deployment guide for the **Pikupo** backend (FastAPI + Strawberry +
MongoDB + Redis) and its TLS reverse proxy. The frontends (`Admin Dashboard`,
`CustomerApp`) are built and served separately.

## 1. Prerequisites

- Docker Engine + Docker Compose v2 on the host.
- A domain name pointed at the host (e.g. `pikupo.example.com`).
- Ports `80` and `443` reachable from the internet (for Caddy's automatic TLS).

## 2. Provision secrets (`.env`)

Copy `backend/.env.example` to `backend/.env` and fill in **real** values. Never
commit this file (it is git-ignored).

| Variable | Production value |
|----------|------------------|
| `ENV` | `production` |
| `DEBUG` | `false` |
| `JWT_SECRET` | long random string (e.g. `openssl rand -hex 32`) |
| `ADMIN_EMAIL` | real admin login email |
| `ADMIN_PASSWORD` | strong password (not `change-me`) |
| `MONGO_INITDB_ROOT_USERNAME` | e.g. `pikupo` |
| `MONGO_INITDB_ROOT_PASSWORD` | strong password (not `change-me`) |
| `REDIS_PASSWORD` | strong password (not `change-me`) |
| `CORS_ORIGINS` | `https://admin.example.com,https://app.example.com` |
| `SITE_ADDRESS` | `pikupo.example.com` (enables HTTPS) |

> The backend refuses to start in production if `JWT_SECRET`, `ADMIN_PASSWORD`,
> `MONGODB_URL`, or `REDIS_URL` are unset or still `change-me` (fail-fast).

## 3. Cutover (first deploy)

```bash
cd backend
docker compose up -d --build
docker compose ps          # all services healthy
curl -fsS https://pikupo.example.com/health   # {"status":"ok"}
curl -fsS https://pikupo.example.com/ready    # {"status":"ready"}
```

Caddy obtains and renews Let's Encrypt certificates automatically for
`SITE_ADDRESS`. The app container is not published to the host (it is reachable
only via the internal network); Caddy is the sole public entry point.

## 4. Rolling update

```bash
cd backend
docker compose up -d --build --remove-orphans
docker compose ps
```

Compose recreates only changed containers. Healthchecks gate startup order
(mongo/redis healthy → app → caddy).

## 5. Backups

Automated: the `backup` service dumps the `pikupo` database to
`backend/backups/pikupo_<timestamp>.archive` (gzipped) every
`BACKUP_INTERVAL_SECONDS` (default daily), keeping the newest `BACKUP_KEEP`
(default 14) archives. Store `backend/backups/` off-host (S3/rsync) as part of
your backup retention.

Manual backup:

```bash
docker compose exec -T mongo mongodump \
  --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase admin --db pikupo \
  --archive --gzip > backup.archive
```

Restore:

```bash
docker compose exec -T mongo mongorestore \
  --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase admin --drop --gzip --archive < backup.archive
```

## 6. Rollback

```bash
cd backend
git checkout <last-good-tag>
docker compose up -d --build --remove-orphans
```

Data lives in the named `mongo_data` volume and is untouched by code rollbacks.
If a schema migration must be reverted, restore the pre-migration backup first
(see above), then redeploy the matching code.

## 7. Monitoring

- Liveness: `GET /health` → `200 {"status":"ok"}`.
- Readiness: `GET /ready` → `200` when MongoDB is reachable, else `503`.
- Logs are structured JSON; level via `LOG_LEVEL`. No secrets are logged.

Point your alerting at `/health` and `/ready` (the same probes Compose uses for
healthchecks).
