---
name: run-the-project
description: Run, build, and lint each module of the Forkly monorepo. Use when the user asks how to start or build the app, or needs the correct commands per module.
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
