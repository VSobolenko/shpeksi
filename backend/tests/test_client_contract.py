"""The client apps' GraphQL documents must validate against the backend schema.

Both frontends keep their operations as template literals and talk to this
backend 1:1, so a document that the schema rejects is a silently broken button in
the product (the request fails with a validation error before it ever reaches a
resolver). Unit tests that call resolvers directly cannot catch that, so this
test validates the real documents instead.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
VALIDATOR = BACKEND_DIR / "scripts" / "validate_client_queries.py"

# Which documents the product actually ships.
CLIENT_FILES = [
    REPO_ROOT / "Admin Dashboard" / "src" / "apollo" / "server.js",
    REPO_ROOT / "CustomerApp" / "src" / "apollo" / "server.js",
]


def _load_validator():
    spec = importlib.util.spec_from_file_location("_client_query_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_validator()


def test_client_documents_validate_against_schema():
    problems = []
    checked = 0
    for path in CLIENT_FILES:
        assert path.exists(), f"missing client contract file: {path}"
        for name, body in validator.documents(path):
            if body is None:
                continue
            checked += 1
            try:
                document = validator.parse(body)
            except Exception as exc:  # noqa: BLE001
                problems.append(f"{path.name}:{name}: parse error: {exc}")
                continue
            for error in validator.validate(validator.GRAPHQL_SCHEMA, document):
                problems.append(f"{path.name}:{name}: {error.message}")

    assert checked > 0, "no GraphQL documents were found to validate"
    assert not problems, "client operations rejected by the schema:\n" + "\n".join(
        f"  - {p}" for p in problems
    )


@pytest.mark.parametrize("path", CLIENT_FILES)
def test_client_files_are_readable(path):
    """Guard the fixture itself: a renamed app directory would silently skip."""
    assert path.is_file(), f"expected a client contract file at {path}"
