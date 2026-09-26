"""Request context and auth guards for GraphQL resolvers."""

from typing import Optional

from graphql import GraphQLError
from jose import JWTError
from starlette.requests import HTTPConnection
from strawberry.fastapi import BaseContext

from app.models import Restaurant
from app.services.auth import decode_token

_RESTAURANT_HEADER = "x-restaurant-id"


class Context(BaseContext):
    def __init__(self, request: Optional[HTTPConnection] = None):
        self.request = request
        self.user_id: Optional[str] = None
        self.role: Optional[str] = None
        self.restaurant_id: Optional[str] = None
        self.restaurant_slug: Optional[str] = None
        # Filled in by Strawberry from the `connection_init` payload on a
        # websocket connection (see strawberry/http/handlers.py). Subscriptions
        # open their own connection, so they cannot rely on request headers.
        self.connection_params: Optional[dict] = None


async def get_context(request: HTTPConnection) -> Context:
    ctx = Context(request=request)
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        try:
            payload = decode_token(auth[len("Bearer "):])
            ctx.user_id = payload.get("sub")
            ctx.role = payload.get("role")
            ctx.restaurant_id = payload.get("restaurant")
        except JWTError:
            pass
    # Client app builds send their restaurant slug; a token-bound restaurant
    # always wins over the header so a token can never be re-scoped by a caller.
    if not ctx.restaurant_id:
        await _apply_slug(ctx, request.headers.get(_RESTAURANT_HEADER))
    return ctx


async def _apply_slug(ctx: Context, slug: Optional[str]) -> None:
    """Resolve a restaurant slug onto the context when it is active."""
    slug = (slug or "").strip()
    if not slug:
        return
    restaurant = await Restaurant.find_one({"slug": slug, "is_active": True})
    if restaurant:
        ctx.restaurant_id = str(restaurant.id)
        ctx.restaurant_slug = restaurant.slug


async def resolve_restaurant(info) -> str:
    """Tenant id for a caller, resolving websocket credentials if needed.

    ``get_context`` runs when the connection is established, which for a
    websocket is *before* the ``connection_init`` frame arrives — so the
    connection params are not readable there. Strawberry stores them on the
    context we returned, and this helper reads them at resolver time, which is
    the first moment they are actually available.
    """
    ctx = info.context
    if not ctx:
        raise GraphQLError(
            "Restaurant context required",
            extensions={"code": "RESTAURANT_REQUIRED"},
        )
    if not ctx.restaurant_id:
        params = ctx.connection_params if isinstance(ctx.connection_params, dict) else {}
        if not ctx.user_id and not ctx.role:
            ws_auth = str(params.get("authorization", ""))
            if ws_auth.startswith("Bearer "):
                try:
                    payload = decode_token(ws_auth[len("Bearer "):])
                    ctx.user_id = payload.get("sub")
                    ctx.role = payload.get("role")
                    ctx.restaurant_id = payload.get("restaurant")
                except JWTError:
                    pass
        if not ctx.restaurant_id:
            await _apply_slug(
                ctx,
                params.get("restaurant") or params.get(_RESTAURANT_HEADER),
            )
    if not ctx.restaurant_id:
        raise GraphQLError(
            "Restaurant context required",
            extensions={"code": "RESTAURANT_REQUIRED"},
        )
    return ctx.restaurant_id


def require_user(info) -> str:
    ctx = info.context
    if not ctx or not ctx.user_id:
        raise GraphQLError("Authentication required", extensions={"code": "UNAUTHENTICATED"})
    return ctx.user_id


def require_admin(info) -> str:
    """Any dashboard user (director or staff)."""
    user_id = require_user(info)
    if info.context.role not in ("admin", "director", "staff"):
        raise GraphQLError("Admin access required", extensions={"code": "FORBIDDEN"})
    return user_id


def require_director(info) -> str:
    """Director-only: payments, catalog config, staff accounts."""
    user_id = require_user(info)
    # "admin" kept for backward-compatible JWTs from the env bootstrap
    if info.context.role not in ("admin", "director"):
        raise GraphQLError("Director access required", extensions={"code": "FORBIDDEN"})
    return user_id


def require_superadmin(info) -> str:
    """Platform owner only: tenant (restaurant) management."""
    user_id = require_user(info)
    if info.context.role != "superadmin":
        raise GraphQLError("Superadmin access required", extensions={"code": "FORBIDDEN"})
    return user_id


def require_restaurant(info) -> str:
    """Return the active restaurant id or fail when no tenant can be resolved."""
    ctx = info.context
    if not ctx or not ctx.restaurant_id:
        raise GraphQLError(
            "Restaurant context required",
            extensions={"code": "RESTAURANT_REQUIRED"},
        )
    return ctx.restaurant_id


def ensure_tenant_access(info, document) -> None:
    """Raise FORBIDDEN when a loaded document belongs to another restaurant."""
    restaurant_id = require_restaurant(info)
    owner = getattr(document, "restaurant", None)
    if owner is None or str(owner) != str(restaurant_id):
        raise GraphQLError(
            "Resource belongs to another restaurant",
            extensions={"code": "FORBIDDEN"},
        )
