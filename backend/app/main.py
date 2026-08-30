"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL

from app.config import settings
from app.db import close_db, get_database, init_db
from app.graphql.context import get_context
from app.graphql.schema import schema
from app.logging_config import configure_logging
from app.models import Configuration, Order
from app.services.payments import charge_stripe_card, to_cents

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_production_secrets()
    await init_db()
    if not await Configuration.find_one({}):
        await Configuration().insert()
    yield
    await close_db()


graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
    subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL],
)

app = FastAPI(title="Pickup API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_router, prefix="/graphql")


def _html(title: str) -> HTMLResponse:
    return HTMLResponse(
        f"<html><head><title>{title}</title></head><body>{title}</body></html>"
    )


@app.get("/stripe/success")
async def stripe_success() -> HTMLResponse:
    return _html("success")


@app.get("/stripe/failed")
async def stripe_failed() -> HTMLResponse:
    return _html("failed")


@app.get("/stripe/cancel")
async def stripe_cancel() -> HTMLResponse:
    return _html("cancel")


@app.post("/stripe/charge")
async def stripe_charge(request: Request, id: str) -> JSONResponse:
    config = await Configuration.find_one({})
    order = await Order.find_one(Order.order_id == id)
    if not order:
        return JSONResponse({"redirect": "stripe/failed"})
    if not config or not config.secret_key:
        return JSONResponse({"redirect": "stripe/failed"})

    body = await request.json()
    token = None
    if isinstance(body, dict):
        token = body.get("id") or body.get("token")
    if not token:
        return JSONResponse({"redirect": "stripe/failed"})

    try:
        charge_stripe_card(
            secret_key=config.secret_key,
            amount_cents=to_cents(order.order_amount),
            currency=config.currency or "usd",
            token=token,
            description=f"Order {order.order_id}",
        )
    except Exception:
        return JSONResponse({"redirect": "stripe/failed"})

    order.payment_status = "PAID"
    order.paid_amount = order.order_amount
    await order.save()
    return JSONResponse({"redirect": "stripe/success"})


@app.get("/")
async def root() -> dict:
    return {"status": "ok", "graphql": "/graphql"}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> JSONResponse:
    try:
        await get_database().command("ping")
    except Exception:
        return JSONResponse({"status": "not ready"}, status_code=503)
    return JSONResponse({"status": "ready"}, status_code=200)
