# backend/graphql-api Specification

## Purpose
A self-hosted GraphQL API that exposes the menu catalog, configuration, user, and authentication surface for the Admin Dashboard and CustomerApp, implementing the existing frontend GraphQL contract 1:1 over HTTP and WebSocket.

## Requirements

### Requirement: GraphQL endpoint availability
The backend SHALL serve a GraphQL endpoint at the path `/graphql` over both HTTP and WebSocket, using the field, operation, and type names fixed by the existing frontends.

#### Scenario: HTTP GraphQL query
- **WHEN** a client sends an HTTP POST to `/graphql` with a valid GraphQL operation
- **THEN** the backend returns the requested fields for that operation

#### Scenario: WebSocket GraphQL subscription
- **WHEN** a client opens a WebSocket connection to `/graphql` and starts a subscription
- **THEN** the backend delivers subscription events over that connection

### Requirement: JWT authentication
The backend SHALL authenticate requests via a JWT in the `Authorization: Bearer <token>` header and SHALL reject unauthenticated access to protected operations.

#### Scenario: Authenticated request
- **WHEN** a client sends a request with a valid, unexpired JWT
- **THEN** the backend allows access to role-permitted operations

#### Scenario: Missing or invalid token
- **WHEN** a client sends a protected request without a valid JWT
- **THEN** the backend returns an authentication error and does not execute the operation

### Requirement: Role-based authorization
The backend SHALL distinguish admin and customer roles and SHALL reject an operation when the caller's role is not permitted to invoke it.

#### Scenario: Admin-only mutation from a customer
- **WHEN** a customer token invokes an admin mutation such as `updateOrderStatus`
- **THEN** the backend returns an authorization error

#### Scenario: Customer mutation from an admin
- **WHEN** an admin token invokes a customer mutation such as `placeOrder`
- **THEN** the backend returns an authorization error

### Requirement: Menu catalog queries
The backend SHALL implement the catalog queries `categories`, `foods`, `foodByCategory`, `foodByIds`, `addons`, `options`, `coupons`, `allCategories(page)`, `allAddons(page)`, and `allOptions(page)`, returning snake_case fields for the menu entities.

#### Scenario: List categories
- **WHEN** a client queries `categories`
- **THEN** the backend returns categories with `_id`, `title`, `description`, and `img_menu`

#### Scenario: List food by category
- **WHEN** a client queries `foodByCategory` for a category id
- **THEN** the backend returns foods with `title`, `description`, `img_url`, `stock`, `tag`, `variations`, and their nested `addons`

### Requirement: Admin catalog management
The backend SHALL implement the admin catalog mutations `createFood`, `editFood`, `deleteFood`, `createCategory`, `editCategory`, `deleteCategory`, `createOptions`, `editOption`, `deleteOption`, `createAddons`, `editAddon`, `deleteAddon`, `createCoupon`, `editCoupon`, and `deleteCoupon`.

#### Scenario: Create and edit a food
- **WHEN** an admin creates a food with `createFood` and later updates it with `editFood`
- **THEN** the backend persists both changes and returns the updated entity

#### Scenario: Delete a coupon
- **WHEN** an admin calls `deleteCoupon` with a coupon id
- **THEN** the backend removes the coupon and it no longer appears in `coupons`

### Requirement: User and profile management
The backend SHALL implement `createUser`, `login`, `profile`, `updateUser`, `updateNotificationStatus`, `createAddress`, `editAddress`, `deleteAddress`, `selectAddress`, `changePassword`, and `forgotPassword`, and SHALL support `login` with a `type` for standard, Facebook, and Apple sign-in.

#### Scenario: Customer login
- **WHEN** a customer calls `login` with valid email/password credentials
- **THEN** the backend returns a JWT and the customer profile

#### Scenario: Social login
- **WHEN** a customer calls `login` with `type` Facebook or Apple and a valid OAuth token
- **THEN** the backend validates the token and returns a JWT and profile

#### Scenario: Address lifecycle
- **WHEN** a customer creates, edits, selects, and deletes addresses
- **THEN** the backend reflects each change on the user's `addresses` list, including the `selected` flag

### Requirement: Password handling
The backend SHALL store passwords as bcrypt hashes and SHALL issue JWTs with an `exp` expiry claim.

#### Scenario: Password never stored in plaintext
- **WHEN** a user creates an account or resets a password
- **THEN** the stored password is a bcrypt hash, never the plaintext value

### Requirement: Configuration singleton
The backend SHALL expose a single configuration document via the `configuration` query and SHALL update it through `saveOrderConfiguration`, `saveEmailConfiguration`, `savePaypalConfiguration`, `saveStripeConfiguration`, and `saveCurrencyConfiguration`.

#### Scenario: Read configuration
- **WHEN** a client queries `configuration`
- **THEN** the backend returns the singleton config including `currency`, `currency_symbol`, `publishable_key`, and `client_id`

#### Scenario: Save Stripe configuration
- **WHEN** an admin calls `saveStripeConfiguration` with keys
- **THEN** the backend persists the keys and they are returned by later `configuration` queries

### Requirement: Dashboard analytics queries
The backend SHALL implement `orderCount`, `getDashboardTotal(starting_date,ending_date)`, `getDashboardSales`, `getDashboardOrders`, and `getDashboardData` returning aggregated metrics for the admin dashboard.

#### Scenario: Order count
- **WHEN** an admin queries `orderCount`
- **THEN** the backend returns the total number of orders

#### Scenario: Date-filtered totals
- **WHEN** an admin queries `getDashboardTotal` with a date range
- **THEN** the backend returns totals computed only within that range

### Requirement: Status enum queries
The backend SHALL implement `getOrderStatuses` and `getPaymentStatuses` returning the allowed status enums.

#### Scenario: Read order statuses
- **WHEN** an admin queries `getOrderStatuses`
- **THEN** the backend returns the pickup status set (`PENDING`, `ACCEPTED`, `READY`, `COMPLETED`, `CANCELLED`)

### Requirement: Production configuration and secrets
The backend SHALL read all secrets and environment-specific values from environment variables and SHALL NOT ship insecure default credentials. In production it SHALL fail fast when required secrets are missing or still placeholder values.

#### Scenario: Missing JWT secret in production
- **WHEN** the backend starts with `ENV=production` and `JWT_SECRET` unset or `change-me`
- **THEN** startup fails with a clear error

#### Scenario: Placeholder admin password in production
- **WHEN** the backend starts with `ENV=production` and `ADMIN_PASSWORD` unset or `change-me`
- **THEN** startup fails with a clear error

#### Scenario: Configurable database name
- **WHEN** `MONGODB_DB_NAME` is set
- **THEN** the backend connects to that database (default `pickup`)

### Requirement: Health and readiness endpoints
The backend SHALL expose a liveness endpoint `GET /health` and a readiness endpoint `GET /ready` that reports dependency status.

#### Scenario: Liveness probe
- **WHEN** a client requests `GET /health`
- **THEN** the backend returns `200` with `{"status": "ok"}`

#### Scenario: Readiness probe
- **WHEN** a client requests `GET /ready`
- **THEN** the backend returns `200` if MongoDB is reachable, otherwise `503`

### Requirement: Safe error handling
The backend SHALL return structured errors that do not leak secrets, connection strings, or stack traces.

#### Scenario: Errors hide internals
- **WHEN** a resolver raises an unexpected exception
- **THEN** the client receives a generic error with no secret values or stack trace

### Requirement: Containerized deployment
The backend SHALL ship a non-root `Dockerfile` and a `docker-compose` definition that starts the app with MongoDB and Redis, including healthchecks.

#### Scenario: Backend runs in a container
- **WHEN** the image is built and run
- **THEN** the API is reachable at `/graphql` and `/health` returns ok

### Requirement: Authenticated data stores
The backend SHALL connect to MongoDB and Redis using credentials supplied from environment, and the production deployment SHALL enable authentication on both services. In production the backend SHALL refuse to start when a data-store credential is missing or still a placeholder value.

#### Scenario: MongoDB and Redis require authentication
- **WHEN** the stack starts in production
- **THEN** MongoDB and Redis require credentials and the app connects using credentials from environment

#### Scenario: Missing store credentials in production
- **WHEN** the backend starts with `ENV=production` and a MongoDB or Redis credential is unset or placeholder
- **THEN** startup fails with a clear error

### Requirement: TLS termination
The backend SHALL be deployed behind a TLS-terminating reverse proxy that serves `/graphql` and `/health` over HTTPS, while the application itself listens only on an internal address and is not directly exposed.

#### Scenario: HTTPS endpoint
- **WHEN** a client connects over HTTPS to the reverse proxy
- **THEN** the proxy terminates TLS and forwards to the backend, and `/graphql` and `/health` are reachable over HTTPS

### Requirement: Environment-driven CORS
The backend SHALL derive its allowed CORS origins from the `CORS_ORIGINS` environment variable and SHALL NOT hardcode localhost origins in production deployment files.

#### Scenario: CORS from environment
- **WHEN** `CORS_ORIGINS` lists the production origins
- **THEN** the backend allows those origins and rejects others

### Requirement: Database backups
The deployment SHALL include a documented MongoDB backup strategy and a restore procedure so order and configuration data can be recovered.

#### Scenario: Backup and restore
- **WHEN** a backup is taken and the database is restored from it
- **THEN** the order and configuration data is recovered

### Requirement: Structured logging
The backend SHALL emit structured (JSON) logs with the log level controlled by environment, and SHALL NOT write secrets, tokens, or connection strings to logs.

#### Scenario: Structured, redacted logs
- **WHEN** the backend processes a request
- **THEN** logs are structured and contain no secret values or connection strings
