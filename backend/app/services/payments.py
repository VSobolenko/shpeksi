"""Payment helpers (Stripe charge; PayPal is handled client-side)."""

from decimal import Decimal

import stripe


def charge_stripe_card(
    secret_key: str,
    amount_cents: int,
    currency: str,
    token: str,
    description: str,
):
    """Charge a card via a Stripe token (legacy Checkout flow)."""
    stripe.api_key = secret_key
    return stripe.Charge.create(
        amount=amount_cents,
        currency=currency.lower(),
        source=token,
        description=description,
    )


def to_cents(amount: float) -> int:
    return int(round(Decimal(str(amount)) * 100))
