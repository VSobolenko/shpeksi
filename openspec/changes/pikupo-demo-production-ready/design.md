## Context

See `proposal.md` for motivation. Text/product rename to Pikupo is already on the server (`/opt/pikupo`, DB `pikupo`, order prefix `PKP`). Visual assets and CustomerApp UX were not part of that cutover. Seed scripts create catalog rows without `img_url`/`img_menu`, so the live stand shows white/empty placeholders. Drawer styles include a large negative horizontal margin; Google OAuth uses Expo AuthSession with `useProxy: true` and no backend ID-token verification; Register uses digit-only phone regex plus timezone→country mapping that can emit hyphenated codes.

Codex is registered in `.cursor/mcp.json` via `.cursor/mcp/codex-launcher.cjs`. In the current Cursor session the `codex` MCP namespace is **not** loaded (only `cursor`, browsers, Playwright, Unity). The binary resolves via the launcher (`openai.chatgpt-…/bin/.../codex.exe`). Implementation MUST use Codex MCP when available, otherwise the CLI fallback `node .cursor/mcp/codex-launcher.cjs exec …`, per `.cursor/skills/codex-second-agent/SKILL.md`. Codex has **no shell network egress** and no web search; image_gen works. Objective gate after any Codex write: `node scripts/verify-changes.mjs` + human diff read. Writing work goes in a git worktree.

Upstream layout reference: https://github.com/enatega/food-delivery-singlevendor (CustomerApp Sidebar/Drawer).

## Goals / Non-Goals

**Goals:**
- One visual system + regenerated assets, wired into all four modules and demo seed.
- CustomerApp drawer, Google auth path, registration, and image props fixed to production-demo quality.
- Evidence via verify-changes, pytest, Admin Playwright, CustomerApp Maestro, then redeploy + APK rebuild.

**Non-Goals:**
- Buying/configuring a production Google Cloud project for the merchant (we document required client IDs; if absent, Google is honestly disabled).
- Full App Store / Play Store listing art beyond what the demo APK and site need.
- Restyling every Admin Argon SCSS page into a new design system.
- Domain cutover to `pikupo.com` (separate pending step unless DNS is already live).

## Decisions

### 1. Codex as peer for images + independent review
- **Choice:** Generate food/category/placeholder/logo rasters with Codex `image_gen`; use Codex read-only for brand leftover audits and post-change review. Controller owns verification.
- **Why:** Model diversity + built-in image_gen without `OPENAI_API_KEY`. Subagents share our blind spots.
- **Alternatives:** Manual stock downloads (license risk, off-brand); GenerateImage Cursor tool (no long agent loop / weaker for batch brand kits).

### 2. Host demo food images as static files under Caddy
- **Choice:** Commit or generate PNGs under `backend/static/demo-media/` (or `Website/public/demo-media/`), serve over HTTPS on the apex/API host, store absolute HTTPS URLs in seed `img_url`/`img_menu`.
- **Why:** No Cloudinary dependency for demos; survives DB reset; works offline on the VPS.
- **Alternatives:** Cloudinary upload during seed (needs secrets); base64 in Mongo (bloated).

### 3. Google auth: Expo AuthSession without deprecated proxy + optional backend verify
- **Choice:** Remove `useProxy: true`; use scheme `pikupo` + platform client IDs; verify ID token against `GOOGLE_CLIENT_ID` on the backend when set; if client IDs missing, disable the button.
- **Why:** Proxy/auth URL mismatches are a common source of 400s; backend currently trusts email from userinfo with no verification.
- **Alternatives:** Keep proxy (fragile on modern Expo); require Firebase Auth (heavier than needed for demo).

### 4. Drawer: diff vs Enatega, then fix styles — not a rewrite
- **Choice:** Diff `CustomerApp/src/components/Sidebar` (+ Drawer Profile) against upstream Enatega; remove the negative margin / flex bugs; keep React Navigation drawer.
- **Why:** User reports a regression after fork; upstream is the intended baseline.
- **Alternatives:** Full custom drawer rewrite (out of scope).

### 5. Placeholders: branded asset + non-white background
- **Choice:** New `food_placeholder` / `imagePlaceholder` from Codex; PikupoImage fallback background uses brand surface color, not pure white.
- **Why:** Spec forbids white empty boxes.

### 6. Worktree isolation for Codex writers
- **Choice:** `using-git-worktrees` for any Codex `workspace-write` session; merge only after verify-changes.
- **Why:** Skill mandate; prevents clobbering the controller tree.

## Risks / Trade-offs

- [Codex MCP not enabled in this Cursor session] → Use CLI fallback; ask human to enable `codex` in Settings → MCP + reload so `/ship` can call MCP tools directly.
- [Google OAuth still fails without real client IDs] → Honest disable path + runbook section listing exact console steps; do not fake "working Google" without credentials.
- [image_gen slow/costly (~52s per image)] → Batch prompts (one kit: logo, placeholder, N foods, N categories); reuse across Admin/Website where possible.
- [Seed HTTPS URLs tied to sslip.io or pikupo.com] → Parameterize base media URL via env in seed script so domain cutover does not require regenerating binaries.
- [Secret-guard does not see Codex writes] → Always scan Codex diffs before staging.

## Migration Plan

1. Generate asset kit → commit under agreed paths.
2. Wire UI + seed; reset local and server demo DBs; re-seed.
3. Fix CustomerApp UX bugs; Maestro + Playwright evidence.
4. Rebuild Admin/Website static; publish; rebuild APK as `pikupo-demo-v1.0.23.apk` (or next version); update runbook download URL.
5. Rollback: previous APK kept beside new file; Mongo rescue dump pattern already documented in `DEMO_RUNBOOK_RU.md`.

## Open Questions

Resolved 2026-09-20 (human answers):

- **Domain / DNS:** none purchased yet; demo stays on `sslip.io` / server IP until the human later buys `pikupo.com`. Media base URL and APK target the current public apex.
- **Google OAuth client IDs:** not provisioned yet. Do **not** use a shared Gmail password as a substitute — OAuth needs Cloud Console client IDs. During apply: implement honest disable + correct AuthSession wiring; when the human is available, walk them through creating OAuth clients (or they paste client IDs). Never store account passwords in the repo or agent files.
