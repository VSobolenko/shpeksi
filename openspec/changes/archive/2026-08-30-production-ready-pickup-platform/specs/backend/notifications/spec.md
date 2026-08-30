## Purpose

Push and email notifications for order events and account actions, using Firebase Cloud Messaging for devices and SMTP for email.

## ADDED Requirements

### Requirement: Device token registration
The backend SHALL store device notification tokens via `pushToken` (customer) and `uploadToken` (admin), persisting the token on the relevant user/configuration.

#### Scenario: Customer registers push token
- **WHEN** a customer calls `pushToken` with a device token
- **THEN** the backend stores the token so future notifications reach the device

### Requirement: Admin sends notification to a user
The backend SHALL implement `sendNotificationUser` so an admin can send a push notification to a specific customer.

#### Scenario: Admin notifies a customer
- **WHEN** an admin calls `sendNotificationUser` for a customer id with a title and body
- **THEN** the backend dispatches an FCM push to the customer's registered token

### Requirement: Order status push notifications
The backend SHALL send a push notification to the customer when their order status changes.

#### Scenario: Status change triggers push
- **WHEN** the store updates an order's status
- **THEN** the backend sends a push notification to that customer's device describing the new status

### Requirement: Notification preferences
The backend SHALL honor the user's `is_order_notification` and `is_offer_notification` flags and SHALL allow the customer to update them via `updateNotificationStatus`.

#### Scenario: Orders muted by preference
- **WHEN** a customer has disabled order notifications
- **THEN** the backend does not send order-status pushes to that customer

### Requirement: Email notifications
The backend SHALL send email via SMTP for order confirmation and password reset using the configuration's email credentials, subject to the `enable_email` flag.

#### Scenario: Order confirmation email
- **WHEN** an order is placed and email is enabled
- **THEN** the backend sends a confirmation email to the customer

#### Scenario: Password reset email
- **WHEN** a customer calls `forgotPassword` or `resetPassword` and email is enabled
- **THEN** the backend sends a password reset email to the customer

### Requirement: Graceful degradation when unconfigured
The backend SHALL no-op with a log warning when FCM or SMTP credentials are absent, rather than crashing or sending with placeholder credentials.

#### Scenario: Missing FCM credentials
- **WHEN** a notification is triggered but no Firebase service account is configured
- **THEN** the backend logs a warning and skips the push without failing the request

#### Scenario: Missing SMTP credentials
- **WHEN** an email would be sent but SMTP is not configured or `enable_email` is false
- **THEN** the backend skips sending without failing the request

### Requirement: Admin Dashboard runs without Firebase configuration
The Admin Dashboard SHALL boot and remain fully usable when no Firebase credentials are provided, skipping only push-token registration and the foreground push handler.

#### Scenario: Admin loads without Firebase
- **WHEN** an admin opens the dashboard without a configured `VITE_FIREBASE_API_KEY`
- **THEN** the dashboard still loads and functions, but no push token is registered and no foreground push handler is attached
