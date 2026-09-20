## Context

The repo contains only three frontends talking to a third-party demo GraphQL server over HTTP + WebSocket (`subscriptions-transport-ws`, Apollo Client v2). There is no backend. The environment is Windows/PowerShell. Frontends are plain JavaScript (ES modules, StandardJS style). The GraphQL contract (operation/field names, snake_case fields, `/graphql` path, JWT bearer auth) is fixed by the frontends and must be implemented 1:1. See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- A self-hosted, production-ready Python backend that is a drop-in replacement for the demo server.
- A working end-to-end self-collect flow: customer orders → store sees it in real time → store prepares → customer picks up.
- Removal of every delivery/rider trace from code, config, and README.
- A modernized, buildable Admin Dashboard and CustomerApp with no hardcoded secrets.

**Non-Goals:**
- Changing the menu catalog domain logic (Category/Food/Addon/Option/Coupon) — it is already working.
- Migrating the admin from Reactstrap/MUI v4 or replacing charting beyond the required version bumps.
- Server-side PayPal processing (PayPal remains client-side by contract).
- Rewriting the localization mechanism; only delivery/rider strings are removed.

## Decisions

### 1. Backend stack and layout
Use FastAPI (ASGI) + Strawberry GraphQL (code-first) + Beanie/Motor (MongoDB) + Redis for pub/sub. Layout is a top-level `backend/` package per the spec (`app/main.py`, `app/config.py`, `app/db.py`, `app/models/`, `app/graphql/`, `app/services/`, `app/integrations/`, `tests/`).
- **Why**: fixed by the team (Python) and matches the frontend's Mongo-native, nested-document, snake_case data model; Strawberry gives typed async resolvers and subscriptions.
- **Alternatives**: Ariadne (schema-first) — rejected because code-first keeps types and resolvers co-located with Beanie models; Node/TS backend — rejected (team is Python).

### 2. WebSocket dual-protocol strategy
Implement a dual-protocol WebSocket handler on `/graphql` that accepts both the legacy `subscriptions-transport-ws` protocol (`GQL_CONNECTION_INIT`/`GQL_START`/`GQL_STOP`) and the newer `graphql-transport-ws` protocol. In parallel, migrate both frontends from Apollo Client v2 to `@apollo/client` 3.x using the `subscriptions-transport-ws` `WebSocketLink` (which keeps the legacy protocol on the client).
- **Why**: the current Apollo v2 frontends speak the legacy protocol, but Strawberry/`graphql-ws` natively speaks the new one. Dual-protocol makes the backend safe regardless of which client version is live during the migration window.
- **Alternatives**: legacy-only backend (simplest, but blocks any future `graphql-ws` client); new-protocol-only (requires the full frontend migration to land first, which is a big-bang risk). Both rejected in favor of dual-protocol.

### 3. Apollo Client migration order
Migrate CustomerApp and Admin Dashboard to `@apollo/client` 3.x first, replacing `apollo-client`/`apollo-boost`/`react-apollo`/`@apollo/react-hooks`/`apollo-link-ws`. Keep the legacy `subscriptions-transport-ws` transport via `WebSocketLink` so the backend dual-protocol choice is not a hard dependency.
- **Why**: reduces the migration to a single client package and keeps the wire protocol unchanged, decoupling it from the backend rollout.
- **Alternatives**: switch the client to `graphql-ws` (`graphql-transport-ws`) — rejected for now; it can be a follow-up since the backend already supports both.

### 4. Self-pickup (self-collect) model
The `Order` document drops `delivery_address`, `delivery_charges`, and `rider`. `placeOrder` accepts items + contact (name/phone) + coupon + payment method only. Checkout collects contact details, not an address. `status_queue` becomes `pending`, `preparing`, `ready`, `completed`, `cancelled`. Order statuses are `PENDING → ACCEPTED → READY → COMPLETED` (+ `CANCELLED`). `Configuration` drops `delivery_charges`.
- **Why**: the product is self-collect; there is nothing to deliver, so address and fees are meaningless and must be removed end-to-end.
- **Decisions deferred in this design**: a "ready for pickup" push/email is sent on `READY`; no pickup time slot field is added (recorded as an open question below).

### 5. Payments
Keep all three methods: `COD` (primary for pickup), `STRIPE` (server-side charge via `POST /stripe/charge?id=<order_id>` using the configured secret key), and `PAYPAL` (client-side; server only stores `client_id`/`client_secret`/`sandbox`). `payment_status` is `PENDING`/`PAID`.
- **Why**: matches the fixed frontend contract and keeps commercial scope.
- **Alternatives**: COD-only MVP — rejected by the user (full scope selected).

### 6. Auth and roles
JWT (`python-jose`) with `exp`, bcrypt hashes (`passlib[bcrypt]`). Two roles: `ADMIN` (from `adminLogin`) and `CUSTOMER` (from `login`/`createUser`). A Strawberry permission/guard rejects cross-role operations. Customer `login` supports `type` (`DEFAULT`/`FACEBOOK`/`APPLE`) with OAuth token verification for social login.
- **Why**: the contract has distinct admin vs customer entry points; the guard enforces the least-privilege rule.

### 7. Pub/sub
Use Redis pub/sub for production and an in-memory `PubSub` for the MVP/dev, behind a small interface. Events: `subscribePlaceOrder` (order created) and `orderStatusChanged(userId)` (status update).
- **Why**: Redis is the production target but in-memory keeps the first prototype runnable with zero extra services.
- **Alternatives**: Redis-only — rejected to keep MVP startup minimal.

### 8. Secrets and configuration
Move every hardcoded secret to `.env`/`.env.example` for backend and Admin; remove Firebase keys from `Admin Dashboard/src/index.js`, Stripe/Google/Amplitude keys from `CustomerApp/environment.js`, and Google Maps keys from `app.json`. Repoint the apps from the third-party demo GraphQL endpoint to the self-hosted backend. Backend reads config via `pydantic-settings`.
- **Why**: security rule; no secrets in source control.

### 9. Admin modernization
Migrate Admin to React 18 + Vite (from CRA 2.1.8), `@apollo/client` 3.x, chart.js 4 + react-chartjs-2 4, firebase modular (9+/10), react-router-dom v6, `sass` (dart-sass), dayjs, and remove the stray `"npm"` dependency. Reactstrap stays; MUI stays v4 (out of scope to upgrade).
- **Why**: Vite is preferred over CRA5 (faster, modern); the rest are the required version bumps.
- **Alternatives**: CRA 5 — acceptable fallback if Vite migration proves disruptive.

### 10. CustomerApp modernization
Upgrade Expo SDK 47 → 50+ via the official upgrade path, unify on `@apollo/client` 3.x, remove `deprecated-react-native-prop-types` if unused, replace `react-native-material-textfield` with a maintained input, and remove now-unused native deps (`react-native-maps`, `react-native-maps-directions`, `react-native-gifted-chat`, `react-native-timeline-flatlist`). Keep `i18n-js` (single solution after RiderApp removal).

### 11. Pikupo naming
Brand the product "Pikupo" everywhere in production artifacts: MongoDB database `pikupo`, order prefix `PKP`, backend package `pikupo-backend`, API title "Pikupo API", and app display name "Pikupo" (`app.json` name/slug/scheme/bundleId, branding components such as `PikupoImage`, and translation/UI strings). Root policy/docs files (`LICENSE`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CONTRIBUTING.md`, `AGENTS.md`, `README.md`, `README_RU.md`) are updated in the same pass.
- **Why**: the product is branded Pikupo end-to-end; the repository and the product name align.
- **Alternatives**: keep the previous technical names — rejected.

### 12. Production secrets fail-fast
`JWT_SECRET`, `ADMIN_PASSWORD`, and payment/FCM credentials come only from environment. When `ENV=production`, startup fails with a clear error if a required secret is unset or still a placeholder (`change-me`).
- **Why**: prevents shipping with default credentials.

### 13. Redis pub/sub
Extends decision 7: use Redis when `REDIS_URL` is set, with an in-memory broker for development. This makes subscriptions correct across multiple backend instances in production.

### 14. Operability and deployment
Add `GET /health` (liveness) and `GET /ready` (readiness incl. MongoDB ping), a non-root `Dockerfile`, and a `docker-compose.yml` (app + MongoDB + Redis) with healthchecks.

### 15. CI and automated verification
Add a pytest suite (auth, catalog, orders, payments config, notifications no-op) plus the pickup E2E smoke test, and a CI workflow (lint + test + build for backend and Admin Dashboard).

### 16. Authenticated data stores
MongoDB and Redis run with authentication enabled in production. MongoDB is initialized with a root user via `MONGO_INITDB_ROOT_USERNAME`/`MONGO_INITDB_ROOT_PASSWORD`; Redis uses `requirepass` (`REDIS_PASSWORD`). The app connects using credentials from environment (`MONGODB_URL` with user/password, `REDIS_URL` with password). When `ENV=production`, startup fails fast if a store credential is missing or still a placeholder.
- **Why**: an open MongoDB/Redis is the most common production data breach; least-privilege credentials are required by the security rule.
- **Alternatives**: network-only isolation without auth — rejected (does not protect against in-network access).

### 17. TLS termination via reverse proxy
Deploy a TLS-terminating reverse proxy (Caddy) in front of the app. Caddy serves `/graphql` and `/health` over HTTPS (automatic ACME certs), terminates TLS, and forwards to the app on an internal address; the app itself stays plain HTTP and is not exposed directly.
- **Why**: the app does not do TLS itself; a reverse proxy is the standard, low-config way to provide HTTPS, which Stripe redirects, FCM, and GraphQL over WSS all require in production.
- **Alternatives**: TLS inside uvicorn via cert files — rejected (cert rotation/ACME is easier in a proxy).

### 18. Environment-driven CORS
The `CORS_ORIGINS` value comes only from environment. The `docker-compose.yml` must not hardcode localhost origins; it defaults to the real deployment origins. Localhost is only a development default.
- **Why**: hardcoded localhost in a production compose file would block the real site or accidentally allow wrong origins.

### 19. Database backups
Provide a documented backup/restore procedure for MongoDB (`mongodump`/`mongorestore`) plus a scheduled job (cron or a container sidecar) so order and configuration data can be recovered.
- **Why**: orders and configuration are the business data; a restore path is required before production.

### 20. Structured logging and monitoring
Emit structured (JSON) logs with the log level controlled by environment, and never write secrets, tokens, or connection strings to logs. `/health` and `/ready` are the probes consumed by the monitoring/alerting stack.
- **Why**: auditable, greppable logs and health probes are prerequisites for incident response.

### 21. Deploy runbook / continuous delivery
Document a production deploy runbook (release build, env provisioning, cutover, rollback) and, optionally, add a CD workflow that builds and deploys a release from clean state.
- **Why**: a repeatable, documented release path removes "works on my machine" ambiguity at cutover.

## Risks / Trade-offs

- [Legacy WS protocol mismatch] → Mitigation: dual-protocol handler on the backend; verify a subscription reaches a real client in the first backend prototype before building the rest.
- [Large, multi-phase change] → Mitigation: phased task breakdown (backend core → orders/realtime → delivery removal → cleanup → modernization → E2E verification) with a buildable checkpoint after each phase.
- [Frontend contract drift] → Mitigation: treat `*/apollo/server.js` as the source of truth; implement field/operation names 1:1 and keep both sides in sync in the same change.
- [Stripe legacy checkout deprecation] → Mitigation: keep the working legacy flow for now; migrate to Payment Intents carefully in a follow-up if needed, without breaking `POST /stripe/charge`.
- [Windows/PowerShell portability] → Mitigation: cross-platform scripts (Python entrypoints, npm scripts), no POSIX-only shell assumptions.
- [Secrets still present during migration] → Mitigation: `.env.example` with placeholders; secret-guard hook blocks reintroducing known patterns.

## Migration Plan

1. Phase 0 — inventory: confirm the exact frontend GraphQL operations and current run state.
2. Phase 1 — backend core: FastAPI + Strawberry + Beanie + JWT; implement catalog/auth/config operations; stand up the dual-protocol WS prototype and verify a subscription.
3. Phase 2 — backend orders/realtime: `placeOrder`, order queries, status lifecycle, subscriptions, payments (COD/Stripe/PayPal), email, push.
4. Phase 3 — delivery removal: delete `RiderApp/`; strip rider/delivery from Admin and CustomerApp; align statuses and backend schema.
5. Phase 4 — cleanup: secrets to env, dead code, unused deps, i18n normalization.
6. Phase 5 — modernization: React 18 + Vite, Apollo 3, Expo SDK, README.
7. Phase 6 — E2E verification: full pickup scenario + lint/build of all modules.
8. Phase 7 — production hardening & release: Pikupo naming, secrets fail-fast, health/readiness, Redis pub/sub, Docker/compose, CI + test suite, final build/lint/validate.

Rollback: the backend is additive (new `backend/` dir), so the demo URL can be restored via env/config until cutover. Frontend modernizations land per-module and can be reverted via git (no history rewrite).

## Open Questions

- Whether to add a configurable "ready for pickup" estimate / pickup time slot to the order flow (spec currently sends no time slot; can be added later without changing the status model).
- Whether to migrate the client WebSocket transport from `subscriptions-transport-ws` to `graphql-ws` after the `@apollo/client` migration (backend already supports both, so it is non-blocking).
