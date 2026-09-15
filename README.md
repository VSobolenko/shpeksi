# Forkly — Food Ordering with Self-Pickup

A white-label **food ordering platform with self-pickup**. Customers browse the
menu, place an order, and pick it up at the restaurant — no delivery, no riders.

This repository is a monorepo containing the customer mobile app, the merchant
admin panel, the public marketing site, and a self-hosted backend.

## Modules

| Module             | Description                                              | Stack |
| ------------------ | -------------------------------------------------------- | ----- |
| `backend/`         | Self-hosted GraphQL API (HTTP + WebSocket)               | Python (FastAPI + Strawberry + Beanie/MongoDB + Redis) |
| `Admin Dashboard/` | Merchant web panel for menu, orders, and settings        | React 18 + Vite 5 + Apollo Client 3.8 |
| `CustomerApp/`     | Customer mobile app for ordering and self-pickup         | React Native 0.86 + Expo SDK 57 + React 19 + Apollo Client 3.8 |
| `Website/`         | Public marketing/landing site                            | React 18 + Vite + i18next |

> The legacy rider/delivery module (`RiderApp/`) has been removed. The platform
> is pickup-only.

## Prerequisites

- **Node.js 18 or 20 LTS** (the frontends target modern LTS).
- **Python 3.11+** for the backend.
- **MongoDB** (local instance or Atlas) and optionally **Redis**.

## Repository layout

```
backend/            Python GraphQL backend
Admin Dashboard/    React admin panel
CustomerApp/        React Native customer app (Expo)
Website/            Public marketing/landing site
openspec/           OpenSpec change proposals and task tracking
AGENTS.md           Project conventions for AI agents
```

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then fill in your MongoDB/Redis/secret values
uvicorn app.main:app --reload --port 8000
```

The GraphQL endpoint is served at `http://localhost:8000/graphql` (HTTP and
WebSocket for subscriptions). See `backend/README.md` for full details.

### 2. Admin Dashboard

```bash
cd "Admin Dashboard"
npm install
cp .env.example .env          # then fill in VITE_* values
npm run dev                   # Vite dev server
# or: npm run build && npm run preview
```

### 3. CustomerApp

```bash
cd CustomerApp
npm install
cp .env.example .env          # then fill in your keys
npm start                     # expo start
```

Scan the QR code with Expo Go, or press `a`/`i` for an Android/iOS simulator.

### 4. Website

```bash
cd Website
npm install
cp .env.example .env          # then fill in VITE_* link targets
npm run dev                   # Vite dev server
# or: npm run build && npm run preview
```

A single-page, seven-language marketing site (`en`, `ar`, `de`, `fr`, `km`, `ru`,
`zh`) with Arabic RTL support. It is fully static — it does not call the
GraphQL API. `npm run build` produces a static `dist/` that can be served by any
static host.

## Configuration

Secrets are kept out of source control. Each module ships an `.env.example`:

- `backend/.env.example` — MongoDB URI, JWT secret, SMTP, Stripe/PayPal, Firebase.
- `Admin Dashboard/.env.example` — `VITE_SERVER_URL`, `VITE_WS_SERVER_URL`, Firebase.
- `CustomerApp/.env.example` — `GRAPHQL_URL`, `WS_GRAPHQL_URL`, Stripe, Google
  OAuth, Amplitude.
- `Website/.env.example` — `VITE_CUSTOMER_APP_URL`, `VITE_ADMIN_URL` (CTA link
  targets).

The frontends point at the self-hosted backend (`http://localhost:8000/graphql`)
by default.

## Tech stack

- **Backend**: FastAPI, Strawberry GraphQL, Beanie (MongoDB ODM), Redis, JWT,
  `subscriptions-transport-ws` + `graphql-transport-ws` dual-protocol WebSockets.
- **Admin Dashboard**: React 18, Vite 5, Apollo Client 3.8, Chart.js 4, React Router 6.
- **CustomerApp**: React Native 0.86, Expo SDK 57, React 19, React Navigation 7,
  Apollo Client 3.8, i18n-js.

## GraphQL contract

The frontends define the GraphQL operations (template-literal strings in
`src/apollo/`). The backend implements them 1:1. Auth is via
`Authorization: Bearer <token>`.

## License

MIT.
