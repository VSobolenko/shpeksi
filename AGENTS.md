# AGENTS.md — Project context for AI agents

> Single source of truth for how this repository is structured, built, and the
> conventions it follows. Read this before making changes. The full refactor
> roadmap lives in `AGENT_PROMPT.md`.

## Overview

**Enatega Single Vendor** — a white-label food-ordering / food-delivery solution.
The repo contains the **frontends only**; the backend/API is proprietary and is
**not** in this repo (a replacement is planned, see Roadmap).

Three frontend modules (a monorepo):

- `Admin Dashboard/` — restaurant/merchant web panel (React).
- `CustomerApp/` — customer mobile app (React Native + Expo).
- `RiderApp/` — courier mobile app (React Native + Expo). **Slated for removal.**

All modules talk to a GraphQL server over **HTTP + WebSocket** (subscriptions).

## Repository layout

```
Admin Dashboard/     React admin panel (react-scripts / CRA)
CustomerApp/         React Native customer app (Expo SDK 47)
RiderApp/            React Native courier app (Expo SDK 47)
assets/              README screenshots and logos
contributingGuides/  contributor guide
backend/             (does NOT exist yet — planned Python backend)
AGENT_PROMPT.md      roadmap/spec: write backend, remove delivery, modernize
```

## Tech stack

| Module          | Stack |
|-----------------|-------|
| Admin Dashboard | React 16.8 (legacy), react-scripts 2.1.8 (CRA), reactstrap, Apollo Client v2 (`apollo-client` + `apollo-link` + `react-apollo`), `subscriptions-transport-ws`, Firebase 7, chart.js 2, i18next |
| CustomerApp     | React Native 0.70.5, Expo SDK 47, React Navigation 6, Apollo Client v2, `subscriptions-transport-ws` 0.11, i18n-js, react-native-maps |
| RiderApp        | React Native 0.70.8, Expo SDK 47, React Navigation 5, Apollo Client v2, i18next |

Frontends are plain JavaScript (ES modules) — **no TypeScript**.

## How to run

Prereqs: Node.js. The repo currently documents Node 14–16 (legacy); the
modernization target is Node 18/20 LTS.

```bash
# Admin Dashboard
cd "Admin Dashboard" && npm install && npm start      # CRA dev server

# CustomerApp
cd CustomerApp && npm install && npm start            # expo start

# RiderApp (deprecated)
cd RiderApp && npm install && npm start
```

Env: Admin reads `REACT_APP_*` from `.env.*` (see `.env.example`); CustomerApp
reads `environment.js`. The apps currently point at the hosted demo GraphQL
(`https://enatega-singlevendor.up.railway.app/graphql`).

## Code conventions

- **Style**: StandardJS (no semicolons, single quotes, 2-space indent) +
  `plugin:react/recommended`, with `space-before-function-paren: never` and
  `react/prop-types: 0`. Prettier uses `prettier-config-standard`.
- Legacy files are inconsistent (some double quotes / semicolons). Match the
  *intended* StandardJS style, not the accidental inconsistencies.
- Screens live in `src/screens/<Screen>/`, reusable UI in
  `src/components/<Group>/<Component>/`. Colocate a `styles.js` (`StyleSheet.create`)
  in RN, or SCSS under `src/assets/scss/` in Admin.
- i18n: CustomerApp uses `i18n-js` with keys in `src/translations/*.js`
  (en, ar, de, fr, km, zh). Every user-facing string must be added to **all** files.

## GraphQL contract (important)

- Operations are template-literal strings exported from `src/apollo/server.js`
  (Admin) and `src/apollo/*.js` (Customer/Rider).
- Field/operation names are **fixed by the frontend** — a backend must implement
  them 1:1. Do not invent or rename fields.
- Auth: JWT via `Authorization: Bearer <token>` header.
- Subscriptions use the **legacy `subscriptions-transport-ws`** protocol
  (`apollo-link-ws`), NOT `graphql-transport-ws`. Critical compatibility point.

## Security (critical)

Secrets are currently hardcoded in several places. Do NOT commit new secrets:

- `CustomerApp/environment.js` — Stripe / Google OAuth / Amplitude keys.
- `Admin Dashboard/src/index.js` — Firebase config + VAPID key.
- `CustomerApp/app.json`, `RiderApp/app.json` — Google Maps API key.

Put credentials in `.env` / `.env.example`. `.env`, `google-services*.json`, and
`google-service-account.json` must stay git-ignored.

## Current state & roadmap

Legacy codebase mid-refactor. The full plan is in `AGENT_PROMPT.md`:

1. Write a Python backend (`backend/`): FastAPI + Strawberry GraphQL + Beanie
   (MongoDB) + Redis, serving `/graphql` (HTTP + WS) matching the frontend contract.
2. Remove delivery: delete `RiderApp/`, strip rider/delivery UI and fields from
   `CustomerApp` and `Admin Dashboard`.
3. Cleanup: remove secrets, dead code, unused dependencies.
4. Modernize: React 18 + Vite (Admin), `@apollo/client` 3.x, Expo SDK 50+
   (CustomerApp), update README.

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
enatega-i18n, run-the-project).

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
and `security-secrets.mdc` (exact locations of hardcoded secrets).

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

- Preserve the GraphQL contract unless the roadmap says otherwise (and keep both
  sides in sync if you change it).
- Never commit secrets; use `.env` / `.env.example`.
- Keep commands/scripts cross-platform (the environment is Windows/PowerShell).
- Do not rewrite git history.
- Follow the installed `superpowers` methodology for planning/debugging/verifying.
- Use `/ship` for end-to-end autonomous work and `/review` as the merge/archive
  gate; the reviewer agents and policy hooks (`secret-guard`, `git-guard`) are the
  enforcement layer — do not bypass them.
