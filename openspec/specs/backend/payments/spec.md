# backend/payments Specification

## Purpose
Payment handling for self-collect orders across Cash on Delivery, Stripe card charges, and PayPal, plus the payment status lifecycle.

## Requirements

### Requirement: Supported payment methods
The backend SHALL support the payment methods `COD`, `STRIPE`, and `PAYPAL` and SHALL record the chosen method and payment status on each order.

#### Scenario: Order records payment method
- **WHEN** a customer places an order with a payment method
- **THEN** the backend stores `payment_method` and sets `payment_status` appropriately (`PENDING` for COD, or `PENDING` until confirmed for online)

### Requirement: Payment status lifecycle
The backend SHALL track `payment_status` with values `PENDING` and `PAID`.

#### Scenario: Mark order paid
- **WHEN** payment is confirmed
- **THEN** the backend sets `payment_status` to `PAID`

### Requirement: Stripe charge endpoint
The backend SHALL expose `POST /stripe/charge?id=<order_id>` that accepts a Stripe token and charges the order amount using the configured Stripe secret key.

#### Scenario: Successful Stripe charge
- **WHEN** the frontend posts a valid Stripe token for an order
- **THEN** the backend charges the card, marks the order `PAID`, and redirects to the success page

#### Scenario: Failed Stripe charge
- **WHEN** the Stripe charge is declined
- **THEN** the backend redirects to the failed page and leaves the order `PENDING`

### Requirement: Stripe cancel endpoint
The backend SHALL expose `GET /stripe/cancel` returning an HTML page whose title is `cancel`.

#### Scenario: Cancel redirect
- **WHEN** the user cancels Stripe checkout and lands on `/stripe/cancel`
- **THEN** the backend returns HTML with `<title>cancel</title>`

### Requirement: Stripe result redirects
The backend SHALL return HTML result pages with `success` and `failed` titles for the corresponding Stripe outcomes.

#### Scenario: Success and failure pages
- **WHEN** a Stripe charge succeeds or fails
- **THEN** the backend redirects to pages titled `success` or `failed` respectively

### Requirement: PayPal configuration
The backend SHALL store and return the PayPal `client_id`, `client_secret`, and `sandbox` flag via the configuration, and SHALL NOT process PayPal server-side (the frontend handles it client-side).

#### Scenario: Read PayPal configuration
- **WHEN** a client queries `configuration`
- **THEN** the backend returns `client_id`, `client_secret`, and `sandbox` for PayPal

### Requirement: Production payment configuration
The backend SHALL load Stripe and PayPal credentials from configuration/environment and SHALL NOT contain committed test or placeholder keys; the PayPal `sandbox` flag SHALL govern live vs sandbox mode.

#### Scenario: No committed payment secrets
- **WHEN** the change is complete
- **THEN** no Stripe secret key, PayPal client secret, or other payment credential appears in source or committed config, only env/`.env.example` placeholders

#### Scenario: Sandbox toggle
- **WHEN** `sandbox` is `true`
- **THEN** PayPal runs in sandbox mode; when `false`, it runs live
