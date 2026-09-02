## Context

The backend is already running via docker-compose (`mongo`, `redis`, `app`, `caddy`, `backup` all healthy) and serving `/graphql` on `:8000`. The Admin Dashboard is Vite + React 18 + `@apollo/client` 3. The CustomerApp is Expo SDK 57 / React Native 0.86.3 with package `com.pickup.vendor`. An AVD `Medium_Phone` exists, and Maestro 2.9.0 and Playwright are installed. Existing specs (`pickup-order-flow`, `customer-app-runtime-verification`, `backend/*`) define the target behavior. See `proposal.md` for motivation.

## Goals / Non-Goals

**Goals:**

- Run a complete, evidence-backed verification of all three modules and the cross-cutting flows.
- Fix every defect found, preserving the GraphQL contract and the pickup-only model.
- Produce a scenario → PASS/FAIL → evidence → what-was-fixed matrix.

**Non-Goals:**

- Feature development, dependency upgrades, or architecture changes beyond what a fix requires.
- Changing the GraphQL contract or the pickup-only model.
- Committing, merging, or pushing (integration is a separate checkpoint).

## Decisions

- **Environment reuse**: reuse the running docker-compose backend; reseed demo data (categories, foods with addons, coupons, test customer) via `backend/scripts/` when needed.
- **Backend evidence**: `python -m pytest -q` + `python -m compileall -q app tests` + `backend/scripts/e2e_pickup_smoke.py`.
- **Admin evidence**: Playwright screenshots per route (build + preview, then drive).
- **Customer evidence**: Maestro flows against a release APK on `Medium_Phone`; base network is `http://10.0.2.2:8000/graphql`.
- **Fix-loop**: each finding is dispatched to an implementer subagent + task review; the controller does not fix directly.
- **Contract safety**: any GraphQL fix keeps frontend operations/field names 1:1 (snake_case).

## Risks / Trade-offs

- [Emulator/Android build time and flakiness] → build the release APK once and reuse it across Maestro runs; validate selectors via `maestro hierarchy` rather than trusting stale selectors.
- [Java version mismatch (PATH resolves Java 24, JAVA_HOME is JDK 17)] → export `JAVA_HOME=C:\Program Files\Java\jdk-17` for Gradle builds.
- [Apollo Client v3 `useLazyQuery` + `onCompleted`/`onError` warnings (v2→v3 legacy)] → convert to derived state from `data`/`error` if they produce a red LogBox or behavior bugs; otherwise record as a ruling.
- [Stripe/PayPal require real sandbox keys] → verify the test-mode flow; if no sandbox keys exist, verify the COD path and record the payment limitation as a ruling.
- [Secret scan false positives on demo config] → remove/replace any tracked secret, honoring the `secret-guard` hook.

## Migration Plan

None — verification plus targeted fixes. No data migration; reseed demo data as needed.
