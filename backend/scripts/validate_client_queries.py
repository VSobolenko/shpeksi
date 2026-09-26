"""Validate every GraphQL document an app sends against the live backend schema.

The frontends keep their operations as template literals in `src/apollo/server.js`.
A typo there is invisible to unit tests and only shows up as a runtime error in
the browser, so this parses each document and validates it against the real
schema built from the backend code.

Usage:
    python scripts/validate_client_queries.py "../Admin Dashboard/src/apollo/server.js"
    python scripts/validate_client_queries.py "../CustomerApp/src/apollo/server.js"
"""

import argparse
import re
import sys
from pathlib import Path

from graphql import parse, validate

# The frontends import nothing from the backend, so the schema is the only
# shared contract between them.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.graphql.schema import schema  # noqa: E402

# `app.graphql.schema.schema` is a Strawberry wrapper; graphql-core's validator
# needs the underlying GraphQLSchema it builds.
GRAPHQL_SCHEMA = getattr(schema, "_schema", schema)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

EXPORT_RE = re.compile(r"export const (\w+)\s*=\s*`(.*?)`", re.DOTALL)
# `gql` fragments are composed at runtime, so documents that interpolate other
# constants cannot be validated in isolation.
INTERPOLATION_RE = re.compile(r"\$\{")


def documents(path: Path):
    source = path.read_text(encoding="utf-8")
    for name, body in EXPORT_RE.findall(source):
        if INTERPOLATION_RE.search(body):
            yield name, None
            continue
        yield name, body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    total = 0
    skipped = 0
    problems: list[str] = []

    for file_arg in args.files:
        path = Path(file_arg)
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        try:
            label = path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            label = path.as_posix()
        print(f"=== {label} ===")
        checked_here = 0
        for name, body in documents(path):
            if body is None:
                skipped += 1
                continue
            total += 1
            checked_here += 1
            try:
                document = parse(body)
            except Exception as exc:  # noqa: BLE001
                problems.append(f"{label}:{name}: parse error: {exc}")
                continue
            errors = validate(GRAPHQL_SCHEMA, document)
            for error in errors:
                problems.append(f"{label}:{name}: {error.message}")
        print(f"  checked {checked_here} document(s)")

    print()
    print(f"documents checked: {total}, skipped (composed at runtime): {skipped}")
    if problems:
        print(f"{len(problems)} PROBLEM(S):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("ALL CLIENT DOCUMENTS VALIDATE AGAINST THE SCHEMA")
    return 0


if __name__ == "__main__":
    sys.exit(main())
