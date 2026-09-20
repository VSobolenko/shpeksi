---
name: run-the-project
description: Run, build, and lint each module of the Pikupo monorepo. Use when the user asks how to start or build the app, or needs the correct commands per module.
disable-model-invocation: true
---

# Run the project

Targets: **Node.js 18/20 LTS** and **Python 3.11+** (plus MongoDB, optionally Redis).

## Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in MongoDB/Redis/secret values
uvicorn app.main:app --reload --port 8000
# tests: python -m pytest -q
```

## Admin Dashboard

```bash
cd "Admin Dashboard"
npm install
npm run dev        # Vite dev server
npm run build      # production build
npm run lint:fix   # eslint --fix
npm run format     # prettier
npm run test:e2e   # Playwright
```

## CustomerApp

```bash
cd CustomerApp
npm install
npm start          # expo start
npm run android    # expo start --android
npm run ios        # expo start --ios
```

## Website

```bash
cd Website
npm install
npm run dev        # Vite dev server
npm run build      # static build into dist/
```

Env: the backend reads `backend/.env` (see `.env.example`); Admin reads `VITE_*`
from `.env.*`; CustomerApp reads `.env`; Website reads `VITE_*`. The frontends
point at the self-hosted backend (`http://localhost:8000/graphql`) by default.

## Verify changed files (fast gate)

```bash
node scripts/verify-changes.mjs              # uncommitted changes
node scripts/verify-changes.mjs --base main  # branch changes
node scripts/verify-changes.mjs --build      # also run module builds (slow)
```

Lints **only the files that changed**, so pre-existing debt cannot produce a false
failure. Exits non-zero on a violation, and also when a check could not run
(BLOCKED) — a skipped check is never reported as a pass.

Coverage is uneven by design: `CustomerApp` and `Admin Dashboard` are checked with
eslint (`standard`); `backend` has no linter (only `compileall`) and `Website` has
no eslint config at all, so both are reported **UNVERIFIED** and their diffs must
be read by hand. `Admin Dashboard` reports BLOCKED until `npm install` has been run
there.

Use this before accepting any code an external agent produced.
