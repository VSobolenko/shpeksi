#!/usr/bin/env python3
"""Release gate for the CustomerApp APK: checks what was actually baked in.

The Android release bundle is compiled with Hermes, so the JS lives in
`assets/index.android.bundle`, while everything that comes from the environment
(GraphQL URL, restaurant slug) is injected by Expo into `assets/app.config`,
i.e. the native manifest - NOT into the JS. Grepping the JS bundle alone
therefore gives false negatives, which is how a build missing
`RESTAURANT_SLUG` once shipped: the API answers `RESTAURANT_REQUIRED` and the
app shows an empty catalog.

Usage:
    python3 scripts/inspect_apk.py CustomerApp/android/app/build/outputs/apk/release/app-release.apk

Exits non-zero when `RESTAURANT_SLUG` is missing, so it can gate a release.
"""
import sys
import zipfile

NEEDLES = [
    'x-restaurant-id',
    'pikupo-demo',
    'RESTAURANT_SLUG',
    'GRAPHQL_URL',
    'sslip',
    'localhost:8000',
    'disabled.apps.googleusercontent.com',
]

SKIP_SUFFIXES = (
    '.so', '.png', '.jpg', '.jpeg', '.webp', '.ttf', '.otf', '.woff', '.woff2',
    '.gif', '.mp4', '.zip',
)


def main(apk):
    raw = open(apk, 'rb').read()
    print('apk: %s' % apk)
    print('size: %d bytes' % len(raw))
    print()

    found = {}

    print('--- uncompressed entries ---')
    for needle in NEEDLES:
        hits = raw.count(needle.encode())
        if hits:
            found.setdefault(needle, []).append('(stored)')
        print('    %-38s %d' % (needle, hits))

    print()
    print('--- per-entry hits ---')
    with zipfile.ZipFile(apk) as archive:
        for info in archive.infolist():
            name = info.filename
            if name.lower().endswith(SKIP_SUFFIXES):
                continue
            if info.file_size > 30 * 1024 * 1024:
                continue
            try:
                data = archive.read(name)
            except Exception as exc:
                print('    %s: read error %s' % (name, exc))
                continue
            hits = {n: data.count(n.encode()) for n in NEEDLES}
            hits = {k: v for k, v in hits.items() if v}
            if hits:
                print('    %-42s %s' % (name, hits))
                for key in hits:
                    found.setdefault(key, []).append(name)

    print()
    if 'RESTAURANT_SLUG' in found and 'pikupo-demo' in found:
        print('VERDICT: OK - tenant slug is baked in; the app will send x-restaurant-id')
        return 0

    print('VERDICT: FAIL - RESTAURANT_SLUG is not baked into this APK.')
    print('  The backend answers RESTAURANT_REQUIRED and the catalog stays empty.')
    print('  Rebuild with RESTAURANT_SLUG=<slug> in CustomerApp/.env (or the build env).')
    return 1


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
