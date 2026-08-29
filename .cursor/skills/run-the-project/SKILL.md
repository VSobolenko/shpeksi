---
name: run-the-project
description: Run, build, and lint each module of the Enatega monorepo. Use when the user asks how to start or build the app, or needs the correct commands per module.
disable-model-invocation: true
---

# Run the project

Node 14–16 is currently documented (legacy); Node 18/20 LTS is the modernization target.

## Admin Dashboard

```bash
cd "Admin Dashboard"
npm install
npm start          # dev server (react-scripts/CRA)
npm run build      # production build
npm run lint:fix   # eslint --fix
npm run format     # prettier
```

## CustomerApp

```bash
cd CustomerApp
npm install
npm start          # expo start
npm run android    # expo start --android
npm run ios        # expo start --ios
```

## RiderApp (deprecated, slated for removal)

```bash
cd RiderApp
npm install
npm start
```

Env vars: Admin reads `REACT_APP_*` from `.env.*` (see `.env.example`); CustomerApp reads `environment.js`.
