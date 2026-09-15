## Purpose

The self-collect order lifecycle: placing an order, querying orders, advancing the pickup status queue, recording reviews, and delivering realtime order events to the store and the customer.

## ADDED Requirements

### Requirement: Place order without delivery
The backend SHALL implement `placeOrder` accepting items, contact details, coupon, and payment method, and SHALL NOT require or store a delivery address or delivery charge.

#### Scenario: Place a pickup order
- **WHEN** a customer calls `placeOrder` with items, contact name/phone, a payment method, and an optional coupon
- **THEN** the backend persists the order with a generated `order_id`, computes `order_amount`, and returns the order

#### Scenario: No delivery fields on order
- **WHEN** an order is created
- **THEN** the order contains no `delivery_address`, `delivery_charges`, or `rider` fields

### Requirement: Order queries
The backend SHALL implement `orders(offset)` and `order(id)` for customers and `allOrders(page,rows,search)` for admins, returning order details with snake_case fields.

#### Scenario: Customer lists own orders
- **WHEN** a customer queries `orders` with an offset
- **THEN** the backend returns only that customer's orders with items, `order_amount`, `order_status`, and `payment_status`

#### Scenario: Admin searches orders
- **WHEN** an admin queries `allOrders` with a search string
- **THEN** the backend returns matching orders with pagination metadata

### Requirement: Self-pickup order status lifecycle
The backend SHALL advance orders through the statuses `PENDING → ACCEPTED → READY → COMPLETED`, and SHALL allow `CANCELLED`.

#### Scenario: Store prepares a pickup order
- **WHEN** an admin calls `updateOrderStatus` moving an order from `PENDING` to `ACCEPTED` and later to `READY`
- **THEN** the backend persists each status change in order

#### Scenario: Cancel an order
- **WHEN** an admin cancels an order
- **THEN** the backend sets `order_status` to `CANCELLED`

### Requirement: Status queue timestamps
The backend SHALL maintain a `status_queue` object recording timestamps for each lifecycle stage (`pending`, `preparing`, `ready`, `completed`, `cancelled`).

#### Scenario: Record stage timestamps
- **WHEN** an order transitions through statuses
- **THEN** the backend records the timestamp of each stage in `status_queue`

### Requirement: Admin order status and payment mutations
The backend SHALL implement `updateOrderStatus`, `updatePaymentStatus`, and `updateStatus` for admins.

#### Scenario: Update payment status
- **WHEN** an admin calls `updatePaymentStatus` marking an order `PAID`
- **THEN** the backend sets `payment_status` to `PAID`

### Requirement: Realtime new-order subscription
The backend SHALL implement the `subscribePlaceOrder` subscription so the store is notified when a new order is placed.

#### Scenario: New order notifies the store
- **WHEN** a customer places an order while the admin is subscribed to `subscribePlaceOrder`
- **THEN** the backend pushes the new order event to the admin subscription in real time

### Requirement: Realtime order status subscription
The backend SHALL implement the `orderStatusChanged(userId)` subscription so a customer sees their order status change in real time.

#### Scenario: Customer sees status change
- **WHEN** the store changes an order status while that customer is subscribed to `orderStatusChanged`
- **THEN** the backend pushes the updated status to the customer's subscription in real time

### Requirement: Dual-protocol WebSocket subscriptions
The backend SHALL support both the legacy `subscriptions-transport-ws` protocol (`GQL_CONNECTION_INIT`/`GQL_START`/`GQL_STOP`) and the newer `graphql-transport-ws` protocol on the same `/graphql` WebSocket endpoint.

#### Scenario: Legacy Apollo v2 client subscribes
- **WHEN** a `subscriptions-transport-ws` client starts a subscription
- **THEN** the backend completes the handshake and delivers events over that connection

#### Scenario: Modern graphql-ws client subscribes
- **WHEN** a `graphql-transport-ws` client starts a subscription
- **THEN** the backend completes the handshake and delivers events over that connection

### Requirement: Order reviews
The backend SHALL implement `reviewOrder` for customers and `allReviews(offset)` for admins.

#### Scenario: Customer reviews an order
- **WHEN** a customer calls `reviewOrder` with a rating and description for a completed order
- **THEN** the backend attaches the review to the order

#### Scenario: Admin lists reviews
- **WHEN** an admin queries `allReviews`
- **THEN** the backend returns reviews with `rating`, `description`, `order`, and `is_active`

### Requirement: Redis-backed pub/sub for production
The backend SHALL use Redis pub/sub for realtime events when `REDIS_URL` is configured and SHALL fall back to an in-memory broker for single-instance development, so multiple backend instances deliver subscription events consistently.

#### Scenario: Multi-instance event delivery
- **WHEN** `REDIS_URL` is set and two backend instances run
- **THEN** a subscription event published by one instance is delivered to subscribers on the other instance
