# pickup-order-flow Specification

## Purpose
The self-collect (pickup) product flow across the CustomerApp and Admin Dashboard, in which the customer orders and picks up food directly from the store with no courier or delivery involved.

## Requirements

### Requirement: No rider or delivery surface
The product SHALL contain no rider, courier, delivery, or rider-tracking functionality anywhere in the code, UI, or backend.

#### Scenario: Rider app removed
- **WHEN** the change is complete
- **THEN** the `RiderApp/` module no longer exists in the repository

#### Scenario: No rider GraphQL operations
- **WHEN** the Admin and Customer apps load
- **THEN** no `rider`, `riders`, `availableRiders`, `assignRider`, or rider-location queries, mutations, or subscriptions are referenced

### Requirement: Contact-only checkout
The CustomerApp SHALL collect only the customer's contact details (name and phone) at checkout and SHALL NOT require a delivery address.

#### Scenario: Checkout without address
- **WHEN** a customer completes checkout
- **THEN** the order is placed with contact name/phone only, with no delivery address captured

### Requirement: No delivery charges
The product SHALL NOT charge or display any delivery fee or `delivery_charges` in the cart, checkout, or order.

#### Scenario: Cart totals without delivery fee
- **WHEN** a customer views the cart and checkout totals
- **THEN** the totals reflect item cost and discounts only, with no delivery fee line item

### Requirement: Pickup order statuses in the client
The CustomerApp SHALL present order status using the pickup set (`PENDING`, `ACCEPTED`, `READY`, `COMPLETED`, `CANCELLED`) and SHALL NOT show `PICKED` or `DELIVERED`.

#### Scenario: Status display
- **WHEN** a customer views an order
- **THEN** the app renders only pickup statuses and never courier statuses such as `PICKED` or `DELIVERED`

### Requirement: Realtime store-to-customer status flow
The store SHALL see new orders in real time in the Admin Dashboard and SHALL be able to advance an order through the pickup statuses; the customer SHALL see these changes in real time.

#### Scenario: End-to-end pickup flow
- **WHEN** a customer places an order, then the store accepts, marks it ready, and completes it
- **THEN** the Admin Dashboard receives the new order and each status update, and the customer sees the status changes in real time

### Requirement: No rider management in the admin
The Admin Dashboard SHALL have no riders management view, no "Riders" menu item, and no "Assign Rider" control on orders.

#### Scenario: Admin UI without riders
- **WHEN** an admin navigates the dashboard
- **THEN** there is no Riders route or menu entry and no assign-rider UI in order details

### Requirement: No rider tracking in the client
The CustomerApp SHALL have no rider tracking map component and no courier chat tied to delivery.

#### Scenario: Order detail without tracking
- **WHEN** a customer opens an order detail screen
- **THEN** there is no rider-tracking map and no courier chat

### Requirement: Clean localization
The CustomerApp translations (`en`, `ar`, `de`, `fr`, `km`, `zh`) SHALL contain no strings about delivery, couriers, or tracking.

#### Scenario: Translation audit
- **WHEN** the change is complete
- **THEN** no delivery-, courier-, or tracking-related keys or strings remain in any translation file

### Requirement: Neutral product naming
The product SHALL NOT use the "Enatega" name (any casing) in production artifacts; the database, order prefix, backend package, API title, and app branding SHALL use the neutral name "Pickup".

#### Scenario: No Enatega in product artifacts
- **WHEN** the change is complete
- **THEN** no file under `backend/`, `Admin Dashboard/`, or `CustomerApp/` references "Enatega"; the database is named `pickup`, the order prefix is `ORD`, and the apps display "Pickup"

#### Scenario: Neutral order identifiers
- **WHEN** an order is placed
- **THEN** its `order_id` begins with `ORD-` and never with `ENATEGA-`

#### Scenario: Root policy files preserved
- **WHEN** the change is complete
- **THEN** the root-level files (`LICENSE`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CONTRIBUTING.md`, `AGENTS.md`, `AGENT_PROMPT.md`, `README.md`) remain present and are not renamed or deleted

### Requirement: Configurable backend endpoint
The frontends SHALL resolve the backend GraphQL URL from environment/config and SHALL NOT contain a hardcoded demo URL.

#### Scenario: No hardcoded demo endpoint
- **WHEN** the apps load
- **THEN** they read the GraphQL endpoint from config/env, not a hardcoded third-party `*.railway.app` URL

### Requirement: Automated verification
The change SHALL include an automated backend test suite and an end-to-end pickup-flow smoke test that can run in CI.

#### Scenario: Pickup flow covered by automated tests
- **WHEN** the test suite runs
- **THEN** it exercises the pickup lifecycle (place → accept → ready → complete → customer sees status) and passes

#### Scenario: Smoke test targets any endpoint
- **WHEN** the pickup smoke test is run
- **THEN** it accepts the backend URL (HTTP and WebSocket) as parameters and drives both requests and subscriptions against that endpoint (e.g. the Caddy proxy), rather than a hardcoded `localhost:8000`
