## 1. Phase 0 — Inventory & scaffolding

- [x] 1.1 Audit the GraphQL contract: enumerate every operation and snake_case field in `Admin Dashboard/src/apollo/server.js`, `CustomerApp/src/apollo/*.js`, and `RiderApp/src/apollo/*.js` into a checklist, and verify it matches the documented GraphQL contract
- [x] 1.2 Record the current run state of each module (npm install/build/expo start) and verify the exact demo URL references in `CustomerApp/environment.js`, `RiderApp/environment.js`, and `Admin Dashboard/.env.*`
- [x] 1.3 Scaffold `backend/` (pyproject.toml/requirements.txt, `.env.example`, README, `app/` and `tests/` packages) and verify `python -m pip install -r requirements.txt` succeeds

## 2. Phase 1 — Backend core

- [x] 2.1 Implement `app/config.py` (pydantic-settings) and `app/db.py` (Beanie/Motor init) and verify the app connects to a local MongoDB and initializes documents
- [x] 2.2 Define Beanie models for Category, Food, Variation, Addon, Option, Coupon, User, Address, Order, OrderItem, Review, Configuration with snake_case fields and verify model import/validation passes
- [x] 2.3 Implement JWT auth (`python-jose`) + bcrypt (`passlib[bcrypt]`) utilities and a role guard, and verify token sign/verify and role checks pass unit tests
- [x] 2.4 Implement the menu catalog queries and admin catalog mutations (foods, categories, foodByCategory, foodByIds, addons, options, coupons, allCategories/allAddons/allOptions, and create/edit/delete mutations) and verify a GraphQL smoke test returns the expected fields
- [x] 2.5 Implement auth/user operations (`adminLogin`, `login` with `type`, `createUser`, `profile`, `updateUser`, `updateNotificationStatus`, addresses, `changePassword`, `forgotPassword`) and verify login returns a JWT and profile
- [x] 2.6 Implement the `configuration` singleton query and `saveOrderConfiguration`/`saveEmailConfiguration`/`savePaypalConfiguration`/`saveStripeConfiguration`/`saveCurrencyConfiguration` mutations and verify a saved config is returned by `configuration`
- [x] 2.7 Implement dashboard analytics queries (`orderCount`, `getDashboardTotal`, `getDashboardSales`, `getDashboardOrders`, `getDashboardData`) and status enum queries (`getOrderStatuses`, `getPaymentStatuses`) and verify they return the pickup status set
- [x] 2.8 Stand up the dual-protocol WebSocket prototype (legacy `subscriptions-transport-ws` + `graphql-transport-ws`) on `/graphql` and verify a subscription event reaches both a legacy Apollo v2 client and a `graphql-ws` client

## 3. Phase 2 — Orders, realtime, payments, notifications

- [x] 3.1 Implement `placeOrder` (items + contact + coupon + payment method, no delivery fields) with generated `order_id` and `order_amount`, and verify the created order has no `delivery_address`/`delivery_charges`/`rider`
- [x] 3.2 Implement `orders(offset)`, `order(id)`, and `allOrders(page,rows,search)` and verify customer scoping and admin pagination/search
- [x] 3.3 Implement `updateOrderStatus`, `updatePaymentStatus`, `updateStatus`, and the `status_queue` timestamps (`pending`/`preparing`/`ready`/`completed`/`cancelled`) and verify status transitions persist
- [x] 3.4 Implement `subscribePlaceOrder` and `orderStatusChanged(userId)` subscriptions wired to the pub/sub and verify realtime delivery to admin and customer
- [x] 3.5 Implement Stripe REST endpoints (`POST /stripe/charge?id=<order_id>`, `GET /stripe/cancel`, success/failed redirects) and verify a charge marks the order `PAID` and redirects correctly
- [x] 3.6 Implement PayPal configuration storage and verify `configuration` returns `client_id`/`client_secret`/`sandbox`
- [x] 3.7 Implement FCM push (`pushToken`, `uploadToken`, `sendNotificationUser`, status-change push honoring `is_order_notification`) and verify a status change dispatches a push
- [x] 3.8 Implement SMTP email (order confirmation, `forgotPassword`/`resetPassword`) honoring `enable_email`, and verify an order triggers a confirmation email

## 4. Phase 3 — Remove delivery & connect client to store

- [x] 4.1 Delete the entire `RiderApp/` module (code, package files, `google-services.json`, `google-service-account.json`, `patches/`, `.expo/`, `reset-cache/`) and verify it no longer exists on disk
- [x] 4.2 Remove rider/delivery operations from `Admin Dashboard/src/apollo/server.js` (`riders`, `availableRiders`, `createRider`, `editRider`, `deleteRider`, `toggleAvailablity`, `assignRider`, `saveDeliveryConfiguration`) and verify the admin app compiles without them
- [x] 4.3 Remove rider/delivery operations from `CustomerApp/src/apollo/*.js` (`rider(id)`, `subscriptionRiderLocation`) and verify the customer app compiles without them
- [x] 4.4 Strip delivery UI from Admin (`src/views/Riders.jsx`, `src/components/Rider/`, Riders route/menu, Assign Rider in order views, `Configuration/Delivery/`) and verify the admin has no riders route or assign-rider UI
- [x] 4.5 Strip delivery UI from CustomerApp (`OrderDetail/TrackingRider`, `PICKED`/`DELIVERED` status rendering, `delivery_charges`/`deliveryFee` in cart, delivery address in checkout → contact-only) and verify checkout collects name/phone only
- [x] 4.6 Replace status sets with pickup statuses (`PENDING`, `ACCEPTED`, `READY`, `COMPLETED`, `CANCELLED`) across order/status components and verify no `PICKED`/`DELIVERED` strings remain in the apps
- [x] 4.7 Remove delivery/courier/chat/tracking translation strings from `CustomerApp/src/translations/*.js` (en, ar, de, fr, km, zh) and verify no delivery/courier keys remain
- [x] 4.8 Align the backend schema with the delivery removal (drop Rider model, `delivery_charges`/`delivery_address`/`rider` from Order, courier subscriptions) and verify the schema validates

## 5. Phase 4 — Cleanup

- [x] 5.1 Move Admin Firebase config/VAPID from `Admin Dashboard/src/index.js` to `.env`/`.env.example` and verify the admin builds with env-provided values
- [x] 5.2 Move CustomerApp Stripe/Google/Amplitude keys from `environment.js` and Google Maps key from `app.json` to env/config and verify no hardcoded keys remain
- [x] 5.3 Repoint both apps from the third-party demo GraphQL endpoint to the self-hosted backend URL and verify the configured URLs resolve to the local backend
- [x] 5.4 Remove cached/generated dirs and dead code (`.expo/`, `reset-cache/`, `.DS_Store`, commented blocks, stray `console.log`, the `"npm": "^6.14.9"` dependency) and verify `git status` no longer shows those artifacts
- [x] 5.5 Remove now-unused native dependencies (`react-native-maps`, `react-native-maps-directions`, `react-native-gifted-chat`, `react-native-timeline-flatlist`, `deprecated-react-native-prop-types` if unused, `react-native-material-textfield`) and verify install/lint still passes
- [x] 5.6 Normalize i18n to a single solution (`i18n-js`) after RiderApp removal and verify translation imports resolve

## 6. Phase 5 — Modernize legacy stack

- [x] 6.1 Migrate Admin Dashboard to React 18 + Vite (from CRA 2.1.8) and verify `npm run build` succeeds
- [x] 6.2 Migrate Admin to `@apollo/client` 3.x (remove `apollo-boost`/`react-apollo`/`apollo-client` 2.x) and verify queries/mutations/subscriptions still work
- [x] 6.3 Upgrade Admin deps: chart.js 4 + react-chartjs-2 4, firebase modular (9+/10), react-router-dom v6 (`Switch`→`Routes`), sass (dart-sass), dayjs; remove `compile-sass/minify-sass/map-sass` scripts and verify `npm run build` passes
- [x] 6.4 Migrate CustomerApp to `@apollo/client` 3.x (single package) with `WebSocketLink` over `subscriptions-transport-ws` and verify subscriptions work against the backend
- [x] 6.5 Upgrade CustomerApp to Expo SDK 50+ via the official upgrade path and verify `npx expo start` boots without errors
- [x] 6.6 Replace `react-native-material-textfield` with a maintained input and verify text inputs still render and accept input

## 7. Phase 6 — End-to-end verification & docs

- [x] 7.1 Run the full pickup scenario (customer places order → admin sees it in real time → accept → ready → complete → customer sees status changes) and verify it completes without errors
- [x] 7.2 Run lint/build across all remaining modules and verify `npm run build` (Admin) and `npx expo start` (CustomerApp) pass
- [x] 7.3 Add backend `.env.example` and Admin `.env.example` and verify placeholders are present with no real secrets
- [x] 7.4 Rewrite README for the pickup product (backend + Admin + CustomerApp run instructions, Node 18/20 LTS, no delivery/rider content, remove rider screenshots/demo links) and verify the documented commands work
- [x] 7.5 Run `openspec validate --strict` for this change and verify the change validates with no missing deltas

## 8. Phase 7 — Production hardening & release

- [x] 8.1 Brand the backend as Pikupo: DB → `pikupo`, order prefix → `PKP`, package `pikupo-backend`, API title → "Pikupo API", and update `.env.example`; verify `placeOrder` returns an `PKP-…` id and data lands in the `pikupo` database
- [x] 8.2 Brand the frontends as "Pikupo" (CustomerApp `app.json` name/slug/scheme/bundleId, `PikupoImage`, login/sidebar/footer text, translations, `package.json` names; Admin `index.html` title, login/footer/sidebar, `i18n.js`) and update root policy/docs files to match; verify no legacy brand remains
- [x] 8.3 Add secrets fail-fast (startup refuses to run when `ENV=production` and `JWT_SECRET`/`ADMIN_PASSWORD` are unset or `change-me`) and verify a prod startup with placeholder secrets exits with a clear error
- [x] 8.4 Add `GET /health` (liveness) and `GET /ready` (readiness with MongoDB ping) and verify `/health` returns ok and `/ready` returns 503 when MongoDB is unreachable
- [x] 8.5 Wire Redis pub/sub (Redis when `REDIS_URL` set, in-memory fallback) and verify subscriptions work in-memory and, with Redis available, across two instances
- [x] 8.6 Add a non-root backend `Dockerfile` and `docker-compose.yml` (app + MongoDB + Redis) with healthchecks and verify `docker compose up` exposes `/graphql` and `/health`
- [x] 8.7 Add/extend the pytest suite (auth, catalog, orders, payments config, notifications no-op) and keep the pickup E2E smoke test; verify `pytest` passes
- [x] 8.8 Add a CI workflow (lint + test + build) for backend and Admin Dashboard and verify the config is present and runnable
- [x] 8.9 Final verification: `npm run build` (Admin), `npx expo export`/`expo start` (CustomerApp), and `openspec validate --strict` all pass (closes 7.2 and 7.5)

## 9. Phase 8 — Production operations & security hardening

- [x] 9.1 Enable MongoDB and Redis authentication (root user via `MONGO_INITDB_ROOT_USERNAME`/`MONGO_INITDB_ROOT_PASSWORD`, Redis `requirepass`) and wire the app to connect with credentials from env; verify compose boots with auth on and the app fails fast in production when a store credential is missing/placeholder
- [x] 9.2 Add a TLS-terminating reverse proxy (Caddy) in front of the app serving `/graphql` and `/health` over HTTPS, with the app bound to an internal address; verify HTTPS serves the GraphQL endpoint
- [x] 9.3 Make CORS environment-driven in the compose file (no hardcoded localhost origins in production) and verify non-listed origins are rejected in production
- [x] 9.4 Add a MongoDB backup strategy (documented `mongodump`/`mongorestore` procedure plus a scheduled job) and verify a backup restores order/configuration data
- [x] 9.5 Add structured JSON logging (log level from env, no secrets in logs) and confirm `/health` + `/ready` feed the monitoring/alerting probes
- [x] 9.6 Document a production deploy runbook (release build, env provisioning, cutover, rollback) and, optionally, a CD workflow; verify a release can be built and deployed from clean state
