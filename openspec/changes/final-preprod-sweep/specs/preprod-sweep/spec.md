## Purpose

Defines the acceptance criteria for the final pre-release verification sweep of the entire Pickup system (backend, Admin Dashboard, and CustomerApp) and the mandatory fix-loop applied to every finding.

## ADDED Requirements

### Requirement: Full backend verification

The backend SHALL pass its automated test suite, byte-compile cleanly, and pass the pickup-flow end-to-end smoke test against the live GraphQL endpoint over both HTTP and WebSocket.

#### Scenario: Tests and byte-compile pass

- **WHEN** `python -m pytest -q` and `python -m compileall -q app tests` run from `backend/`
- **THEN** both commands exit successfully with no errors

#### Scenario: Pickup smoke test passes

- **WHEN** the pickup smoke test runs against the running backend
- **THEN** the full lifecycle (admin login, catalog create, place order, ACCEPTED → READY → COMPLETED transitions, and realtime subscriptions) passes

### Requirement: Admin dashboard runtime verification

The Admin Dashboard SHALL render every route without a blank screen or dead navigation, verified with browser automation and screenshot evidence.

#### Scenario: Every admin route verified

- **WHEN** an admin navigates login, dashboard, orders, catalog (categories/foods/addons/options), coupons, customers, configuration, notifications, and profile
- **THEN** each screen renders real data or a correct empty/error state, and every control leads to its intended destination

### Requirement: Customer app runtime verification

The CustomerApp SHALL pass Maestro flows covering the full customer journey, with visibility assertions at every screen.

#### Scenario: Full journey flows pass

- **WHEN** the Maestro flows run against a release build on the emulator
- **THEN** launch → menu → search/filter → item detail → cart → checkout → payment → orders → review → auth → profile → addresses → settings → help all render with no white screen or dead navigation

### Requirement: Cross-cutting consistency

Placing an order, registering a customer, and admin catalog/coupon changes SHALL propagate correctly between the CustomerApp and Admin Dashboard in real time.

#### Scenario: Order lifecycle

- **WHEN** a customer places an order and the admin advances its status
- **THEN** the order appears in the dashboard and the customer sees each status change in real time

#### Scenario: Registration propagation

- **WHEN** a customer registers
- **THEN** the customer appears in the admin customer list

#### Scenario: Catalog and coupon propagation

- **WHEN** the admin creates or edits a food item or coupon
- **THEN** the change is reflected in the customer menu or checkout coupon validation

### Requirement: Branding, localization, and secrets hygiene

The system SHALL use "Pickup" branding, the `ORD` order prefix, and the `pickup` database; SHALL contain no "Enatega" or delivery/rider artifacts; SHALL keep all six CustomerApp translations complete; and SHALL contain no committed secrets.

#### Scenario: Branding audit

- **WHEN** the codebase and runtime UI are searched
- **THEN** no "Enatega", rider, courier, or delivery artifacts remain; orders use the `ORD-` prefix; and the database is named `pickup`

#### Scenario: Localization completeness

- **WHEN** each of the six translations is checked against the source keys
- **THEN** no translation key is missing in `en`, `ar`, `de`, `fr`, `km`, or `zh`

#### Scenario: No committed secrets

- **WHEN** a secret scan runs
- **THEN** no API keys or credentials remain hardcoded in tracked files

### Requirement: Fix-loop for findings

Every finding SHALL be fixed in the owning module and re-verified before the sweep is considered complete.

#### Scenario: Finding is fixed and re-verified

- **WHEN** a bug, broken layout, dead button, contract drift, or other defect is found
- **THEN** it is fixed in the owning module and the affected verification re-runs green
