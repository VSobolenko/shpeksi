"""Request context and auth guards for GraphQL resolvers."""

from typing import Optional

from graphql import GraphQLError
from jose import JWTError
from starlette.requests import HTTPConnection
from strawberry.fastapi import BaseContext

from app.services.auth import decode_token


class Context(BaseContext):
    def __init__(self, request: Optional[HTTPConnection] = None):
        self.request = request
        self.user_id: Optional[str] = None
        self.role: Optional[str] = None


async def get_context(request: HTTPConnection) -> Context:
    ctx = Context(request=request)
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        try:
            payload = decode_token(auth[len("Bearer "):])
            ctx.user_id = payload.get("sub")
            ctx.role = payload.get("role")
        except JWTError:
            pass
    return ctx


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
