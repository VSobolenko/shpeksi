## 1. Environment bring-up and baseline

- [ ] 1.1 Confirm the backend stack is healthy (`docker ps` + `/health`) and reseed demo data (categories, foods with addons, coupons, test customer) via `backend/scripts/`; verify `/graphql` responds
- [ ] 1.2 Start the Admin Dashboard (`npm run dev` or build + preview) and verify the login screen loads in Playwright
- [ ] 1.3 Build the CustomerApp release APK for `Medium_Phone` (`npx expo run:android --variant release` with `JAVA_HOME` = JDK 17) and verify it installs and launches to the menu

## 2. Backend verification

- [ ] 2.1 Run `python -m pytest -q` and `python -m compileall -q app tests` from `backend/`; verify zero errors
- [ ] 2.2 Run `e2e_pickup_smoke.py` against `localhost:8000`; verify all checks PASS including WebSocket subscriptions

## 3. Admin Dashboard sweep (Playwright)

- [ ] 3.1 Login with valid and invalid password; verify error on invalid and redirect on valid
- [ ] 3.2 Dashboard renders stats and charts with real data; verify no blank screen or error
- [ ] 3.3 Orders: list renders, detail opens, status changes ACCEPTED → READY → COMPLETED; verify status updates
- [ ] 3.4 Catalog CRUD: categories, foods (with variations/addons), options, addons — create/edit/delete; verify lists reflect changes
- [ ] 3.5 Coupons CRUD: create/edit/delete; verify list reflects changes
- [ ] 3.6 Customers: list and detail; verify customer data renders
- [ ] 3.7 Configuration: business settings (Stripe/PayPal/SMTP/currency) render and save; verify persistence
- [ ] 3.8 Notifications and admin profile render and controls work; verify no dead routes

## 4. CustomerApp sweep (Maestro)

- [ ] 4.1 Splash → menu (categories/featured) renders with real data
- [ ] 4.2 Search and the filter modal work
- [ ] 4.3 Category → item detail with options/addons and quantity
- [ ] 4.4 Cart add/remove/quantity change and empty state
- [ ] 4.5 Checkout: contact details, coupon (valid and invalid), payment selection, place order
- [ ] 4.6 Payment Stripe/PayPal test-mode flow (or record a ruling if no sandbox keys)
- [ ] 4.7 My Orders: list, detail, reorder, status
- [ ] 4.8 Rate & Review after an order
- [ ] 4.9 Auth: register, login, forgot password, logout, and the "Create Account" gate
- [ ] 4.10 Profile edit and change password
- [ ] 4.11 Addresses create/edit/delete
- [ ] 4.12 Settings: language switch across all six languages, notifications
- [ ] 4.13 Help screen renders and navigates correctly

## 5. Cross-cutting scenarios

- [ ] 5.1 Order lifecycle: customer places order → appears in dashboard → admin changes status → customer sees the update in real time
- [ ] 5.2 Customer registration → appears in the admin customer list
- [ ] 5.3 Admin creates/edits a food item → reflects in the customer menu
- [ ] 5.4 Admin creates a coupon → customer applies it at checkout

## 6. Branding, localization, and secrets audit

- [ ] 6.1 Search for legacy-brand/rider/delivery/courier artifacts; verify the `FRK` order prefix and the `forkly` database; fix any leftovers
- [ ] 6.2 Verify all six translations (`en`/`ar`/`de`/`fr`/`km`/`zh`) have complete keys; fix gaps
- [ ] 6.3 Run a secret scan; remove or replace any tracked secrets

## 7. Final evidence and report

- [ ] 7.1 Re-run full verification (`pytest`, admin build, `npx expo export`)
- [ ] 7.2 Produce the scenario → PASS/FAIL → evidence → what-was-fixed matrix report
