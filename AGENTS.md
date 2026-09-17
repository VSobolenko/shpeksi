# AGENTS.md — Project context for AI agents

> Single source of truth for how this repository is structured, built, and the
> conventions it follows. Read this before making changes. The main English doc
> is `README.md`; the Russian onboarding guide is `README_RU.md`.

## Overview

**Forkly** — a white-label food-ordering platform with **self-pickup**. Customers
browse the menu, place an order, and collect it at the store; there is no delivery
and no rider functionality.

The repo is a monorepo containing all four modules:

- `backend/` — Python GraphQL API (FastAPI + Strawberry + Beanie/MongoDB + Redis).
- `Admin Dashboard/` — React merchant web panel.
- `CustomerApp/` — React Native + Expo customer app.
- `Website/` — static business-to-business marketing/landing site.

All clients talk to the GraphQL server over **HTTP + WebSocket** (subscriptions).
The `RiderApp/` module and every delivery/rider feature have been removed — the
product is self-pickup only.

## Repository layout

```
backend/             Python GraphQL API (app/{graphql,models,services,integrations}, tests, scripts)
Admin Dashboard/     React admin panel (Vite) — src/, e2e/
CustomerApp/         React Native customer app (Expo) — src/, translations/, .maestro/
Website/             Static marketing/landing site (Vite + React 18) — src/i18n/locales/
assets/              README screenshots and logos
contributingGuides/  contributor guide
openspec/            OpenSpec change proposals and synced specs
.cursor/             rules, skills, commands, hooks, mcp.json
README.md            main English doc
README_RU.md         Russian onboarding doc
```

## Tech stack

| Module             | Stack |
|--------------------|-------|
| `backend/`         | Python 3.11+ — FastAPI, Strawberry GraphQL, Beanie/MongoDB, Redis, JWT |
| `Admin Dashboard/` | React 18, Vite 5, `@apollo/client` 3.8, reactstrap/MUI 4, Chart.js 4, React Router 6, i18next |
| `CustomerApp/`     | React Native 0.86, Expo SDK 57, React 19, `@apollo/client` 3.8, React Navigation 7, i18n-js |
| `Website/`         | Vite + React 18, i18next, 7 locales (`en`, `ar`, `de`, `fr`, `km`, `ru`, `zh`) |

The frontends are plain JavaScript (ES modules) — **no TypeScript**; the backend
is Python.

## How to run

Prereqs: **Node.js 18/20 LTS** and **Python 3.11+** (plus MongoDB, and optionally
Redis).

```bash
# Backend
cd backend && pip install -r requirements.txt
cp .env.example .env          # fill in MongoDB/Redis/secret values
uvicorn app.main:app --reload --port 8000

# Admin Dashboard (Vite dev server)
cd "Admin Dashboard" && npm install && npm run dev

# CustomerApp
cd CustomerApp && npm install && npm start            # expo start

# Website
cd Website && npm install && npm run dev              # Vite dev server
```

Env: the backend reads `backend/.env` (see `.env.example`); Admin reads `VITE_*`
from `.env.*` (see `.env.example`); CustomerApp reads `.env`; Website reads
`VITE_*`. The frontends point at the self-hosted backend
(`http://localhost:8000/graphql`) by default.

## Code conventions

- **Style**: StandardJS (no semicolons, single quotes, 2-space indent) +
  `plugin:react/recommended`, with `space-before-function-paren: never` and
  `react/prop-types: 0`. Prettier uses `prettier-config-standard`.
- Screens live in `src/screens/<Screen>/`, reusable UI in
  `src/components/<Group>/<Component>/`. Colocate a `styles.js`
  (`StyleSheet.create`) in RN, or CSS/SCSS in Admin/Website.
- i18n: CustomerApp uses `i18n-js` with keys in
  `CustomerApp/translations/*.js` (en, ar, de, fr, km, ru, zh). Every user-facing
  string must be added to **all** files. Website uses `i18next` with locale JSON
  in `Website/src/i18n/locales/` (7 locales; `ar` is RTL).

## GraphQL contract (important)

- Operations are template-literal strings exported from
  `Admin Dashboard/src/apollo/server.js` and `CustomerApp/src/apollo/*.js`.
- Field/operation names are **fixed by the frontends** — the backend must
  implement them 1:1. Do not invent or rename fields. Fields are snake_case
  (`order_amount`, `payment_status`); ids are `_id`.
- Auth: JWT via `Authorization: Bearer <token>` header.
- The endpoint is `/graphql` for both HTTP and WebSocket. The client subscriptions
  use the **legacy `subscriptions-transport-ws`** protocol
  (`apollo-link-ws`/`WebSocketLink`); the backend also supports the newer
  `graphql-transport-ws` protocol on the same endpoint.

## Security

No secrets are committed. Put credentials in `.env` / `.env.example`:

- `backend/.env.example` — MongoDB/Redis credentials, JWT secret, admin bootstrap
  login, CORS origins, `SITE_ADDRESS`, Firebase service account (optional; push
  only), Google/Facebook OAuth ids. There is **no** SMTP or payment-provider
  secret here: the Stripe **secret key** is saved at runtime through the admin
  `saveStripeConfiguration` mutation and stored in the DB configuration.
- `Admin Dashboard/.env.example` — `VITE_SERVER_URL`, `VITE_WS_SERVER_URL`,
  Cloudinary upload folders (menu images), Firebase (optional; browser push).
- `CustomerApp/.env.example` — `GRAPHQL_URL`, `WS_GRAPHQL_URL`, Stripe
  **publishable** key, Google OAuth, Amplitude. (No maps/location keys — the app
  has no maps dependency.)

`.env`, `google-services*.json`, and `google-service-account.json` must stay
git-ignored. Never put the Stripe secret key (`sk_*`) in env or in a client app —
only the publishable key (`pk_*`) belongs in `CustomerApp`.

## Current state

The product is branded **Forkly** end-to-end and is production-oriented:

1. **Backend** (`backend/`) — implemented: FastAPI + Strawberry GraphQL +
   Beanie/MongoDB + Redis, serving `/graphql` (HTTP + dual-protocol WebSocket)
   matching the frontend contract.
2. **Admin Dashboard** — React 18 + Vite 5 + `@apollo/client` 3.8 with Playwright
   E2E tests.
3. **CustomerApp** — Expo SDK 57 / React Native 0.86 / React 19 with Maestro E2E flows.
4. **Website** — Vite + React 18 B2B marketing site with 7 locales.
5. **Delivery removed** — `RiderApp/` and all rider/delivery code are gone; the
   model is self-pickup only.

Remaining work is tracked in OpenSpec (`openspec/changes/`) and summarized at the
end of `README_RU.md`.

## AI tooling (skills, MCP, rules, hooks)

### Skills (ready-made, installed via the `skills` CLI)

Installed into `.agents/skills/` (Cursor reads this directory), locked by
`skills-lock.json`:

- **obra/superpowers** (14 skills) — development methodology: brainstorming,
  writing-plans, executing-plans, test-driven-development, systematic-debugging,
  verification-before-completion, requesting/receiving-code-review,
  subagent-driven-development, dispatching-parallel-agents, using-git-worktrees, etc.
- **expo/skills** (9 framework skills) — expo-overview, expo-project-structure,
  expo-native-ui, expo-design-system, expo-data-fetching, expo-animation,
  expo-upgrade, expo-ui, expo-dev-client.

Project-specific skills live in `.cursor/skills/` (graphql-contract,
forkly-i18n, run-the-project).

Reinstall/update with:
```bash
npx skills add obra/superpowers --skill '*' -a cursor --copy -y
npx skills add expo/skills --skill expo-upgrade -a cursor --copy -y   # repeat --skill for each
```

### MCP servers (`.cursor/mcp.json`)

| Server    | Official source                              | Auth / prerequisite                                   |
|-----------|----------------------------------------------|-------------------------------------------------------|
| context7  | `@upstash/context7-mcp`                      | none                                                  |
| playwright| `@playwright/mcp`                            | none (downloads browsers on demand)                   |
| expo      | remote `https://mcp.expo.dev/mcp`            | OAuth (Expo account); local sim control needs SDK 54+ |
| firebase  | `firebase-tools mcp`                         | `firebase login` + a firebase project                 |
| mongodb   | `mongodb-mcp-server`                         | set `MDB_MCP_CONNECTION_STRING` (or use Atlas)        |

GitHub MCP is intentionally omitted (needs a personal access token); add it in
Cursor Settings → MCP if desired.

**Team onboarding (MCP):** `.cursor/mcp.json` is committed — teammates get the
same servers on clone, and `npx -y` auto-installs the packages. What is *not*
automatic (by design, for security): (1) each developer enables the servers in
Cursor Settings → MCP (one-time) and reloads the window; (2) credential-bearing
servers (`expo` OAuth, `firebase login`, `mongodb` connection string) are
per-developer. Keep secrets out of `.cursor/mcp.json` — use `${env:VAR}`
interpolation or a local `.env`. To verify a fresh checkout is wired up, run:

```bash
node scripts/setup-mcp.mjs
```

It resolves every `npx`-based server and prints what still needs manual setup.

### Rules (`.cursor/rules/`)

Framework rules were taken from the
[awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) library
(`react-native-expo`, `graphql-apollo-client`, `python-fastapi`,
`javascript-code-quality`, `security-devsecops`). Two project-specific rules are
authored here: `project-conventions.mdc` (facts that override generic guidance)
and `security-secrets.mdc` (secret-handling rules).

### Hooks (`.cursor/hooks.json`)

- `secret-guard.cjs` — blocks writing known hardcoded secret patterns.
- `git-guard.cjs` — blocks force-push to main/master and destructive `reset --hard`/`clean`.

### Agent harness (writer/reviewer loop)

The "one agent writes, another checks" pattern is wired from ready-made pieces —
see the commands in `.cursor/commands/`:

- `/ship <task>` — autonomous orchestrator: propose → implement (fresh
  implementer subagent per task + task review + fix loop) → verify (evidence) →
  runtime UI check (Playwright + Maestro) → review (`bugbot` + `security-review`)
  → finish (merge/PR) → archive. Stops for the human only at plan approval and
  integration.
- `/review` — dispatch the checker agents (`bugbot` + `security-review`) as a
  verification gate; reports PASS / CHANGES REQUIRED.
- `/ui-verify` — runtime UI verifier: change-impact sweep for blank screens and
  broken navigation (Playwright for the Admin web app, Maestro for the native
  CustomerApp); routes failures to the fix loop.

Role mapping (do not reimplement — invoke):

| Role | Tool |
|------|------|
| Writer | fresh `generalPurpose` subagent per task (`subagent-driven-development/implementer-prompt.md`) |
| Task checker | task reviewer subagent (`subagent-driven-development/task-reviewer-prompt.md`) |
| Final checker | `bugbot` + `security-review` subagents |
| Runtime UI checker | `/ui-verify` (Playwright web + Maestro native) |
| Policy enforcer | hooks `secret-guard.cjs` / `git-guard.cjs` (automatic) |
| Contract | OpenSpec specs + `/opsx-*` |
| Evidence | `verification-before-completion` |
| Integration | `finishing-a-development-branch` |

## Working rules for agents

- Preserve the GraphQL contract unless the specs say otherwise (and keep both
  sides in sync if you change it).
- Never commit secrets; use `.env` / `.env.example`.
- Keep commands/scripts cross-platform (the environment is Windows/PowerShell).
- Do not rewrite git history.
- Follow the installed `superpowers` methodology for planning/debugging/verifying.
- Use `/ship` for end-to-end autonomous work and `/review` as the merge/archive
  gate; the reviewer agents and policy hooks (`secret-guard`, `git-guard`) are the
  enforcement layer — do not bypass them.
