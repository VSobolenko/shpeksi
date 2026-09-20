## Why

The live Pikupo demo was shown to a customer and failed the visual/UX bar: leftover Enatega/stock imagery (or empty white placeholders), a broken CustomerApp drawer layout, non-working Google sign-in (HTTP 400), broken phone registration, and overall template-grade UI. Text rebrand to Pikupo is done; assets, catalog imagery, and CustomerApp production polish are not. Codex is now available as a second agent (including `image_gen`) and must be used as a peer for asset generation and independent review.

## What Changes

- Establish a single Pikupo visual system (palette, logo treatment, food photography style) and regenerate brand + product imagery across CustomerApp, Admin Dashboard, Website, and demo seed data — using Codex `image_gen` for new raster assets where needed.
- Replace Enatega/Argon/stock leftovers and white default placeholders with Pikupo-branded assets; wire unused `LogoName` SVG into auth screens; stop loading Google button art from an external CDN.
- Seed the demo catalog with real `img_url` / `img_menu` values (local static files served by Caddy, or committed assets) so menu, cart, and orders never show empty white boxes.
- Fix CustomerApp production bugs: left drawer text layout (diff vs upstream Enatega), Google OAuth 400 path, phone/country registration, broken order thumbnails (`source` vs `imgSource`), placeholder styling.
- Verify Google auth against Expo + Google Cloud console docs and backend `GOOGLE_CLIENT_ID` verification (or an explicit, documented demo-mode path if keys are not yet provisioned).
- Runtime-verify (Maestro + Playwright + local Docker), then redeploy the demo stand and rebuild/publish the APK under the Pikupo name.

## Capabilities

### New Capabilities

- `pikupo-brand-visuals`: Brand visual identity and asset rules for logos, placeholders, marketing/OG art, and demo food/category imagery across all four modules.
- `customer-app-production-ux`: Production-ready CustomerApp UX acceptance criteria for drawer layout, auth (email + Google), registration (phone/name), image rendering, and catalog/cart/order thumbnails.

### Modified Capabilities

- `pickup-order-flow`: Demo seed / catalog presentation MUST include images so the pickup journey shows real food photos end-to-end (no behavioral change to order states).

## Impact

- `CustomerApp/` — assets, `PikupoImage`, Sidebar/Drawer styles, CreateAccount Google flow, Register validation, MyOrders thumbnails, Maestro flows.
- `Admin Dashboard/` — brand logos/favicons; remove unused Argon stock photos from UI surfaces that customers see.
- `Website/` — OG/favicon refresh if needed; optional hero visual.
- `backend/scripts/seed_demo.py` (+ optional static image hosting) — catalog images on seed.
- `DEMO_RUNBOOK_RU.md` — APK name, asset/deploy notes.
- Tooling: Codex MCP/CLI as peer for image generation and independent review; `scripts/verify-changes.mjs` as the objective gate.
- Upstream reference for layout diff: https://github.com/enatega/food-delivery-singlevendor
- No GraphQL contract renames; no rider/delivery restoration; Stripe secret key remains admin-DB-only.
