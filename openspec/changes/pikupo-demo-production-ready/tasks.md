## 1. Codex harness readiness

- [x] 1.1 Confirm Codex is reachable (enable MCP `codex` in Cursor Settings → MCP + reload, or prove CLI: `node .cursor/mcp/codex-launcher.cjs exec -s read-only "reply with OK"`) and verify the skill path `.cursor/skills/codex-second-agent/SKILL.md` is followed for sandbox + verify-changes
- [x] 1.2 Create an isolated git worktree for writing work (per `using-git-worktrees`) and record its path in `.superpowers/sdd/pikupo-demo-production-ready/progress.md`

## 2. Brand visual kit (Codex image_gen)

- [ ] 2.1 With Codex, generate the Pikupo brand kit (app icon, adaptive icon foreground, splash mark, auth wordmark treatment, branded food placeholder, branded generic placeholder) and copy PNGs into `CustomerApp/assets/` + `CustomerApp/src/assets/images/` — verify files exist and are non-white
- [ ] 2.2 With Codex, generate demo category images (4) and food images (8) matching the seed catalog names; save under `backend/static/demo-media/` — verify file count and readable PNG headers
- [ ] 2.3 Refresh Admin brand marks (`Admin Dashboard/src/assets/img/brand/`, `public/favicon*`) and Website OG/favicon if they still read as generic/third-party — verify titles and favicons show Pikupo
- [x] 2.4 Remove or stop referencing Creative Tim `team-*.jpg` as Admin navbar/sidebar defaults; verify dashboard chrome after login shows no stock face photos

## 3. Wire imagery into product surfaces

- [x] 3.1 Update `PikupoImage` fallbacks (new placeholders, non-white background) and fix `MyOrders` wrong prop (`source` → `imgSource`); verify menu/cart/orders show placeholder or URL without white boxes
- [ ] 3.2 Wire `LogoName` / new logo assets into Login, Register, CreateAccount, ForgotPassword; replace external Google PNG with a local asset — verify auth screens and Google button load offline
- [x] 3.3 Parameterize demo media base URL in `seed_demo.py` (env, defaulting to current public apex) and set `img_menu`/`img_url` on all seeded categories/foods; verify GraphQL returns non-empty image fields after re-seed
- [ ] 3.4 Publish `demo-media` via Caddy (`Caddyfile.prod` route or existing static mount) and verify HTTPS 200 for each seeded URL from outside the container

## 4. CustomerApp production UX fixes

- [x] 4.1 Diff CustomerApp Sidebar/Drawer styles against https://github.com/enatega/food-delivery-singlevendor and fix label spacing (remove harmful negative margins / overflow); verify Russian + English drawer labels are readable on emulator
- [x] 4.2 Fix Google AuthSession: drop deprecated proxy, use `pikupo` scheme + platform client IDs, handle errors without opaque 400; disable button when IDs missing — verify disabled path and, if IDs provided, successful login
- [ ] 4.3 Backend: when `GOOGLE_CLIENT_ID` is set, verify Google ID tokens on `login(type: google)`; when unset, keep documented demo behavior — verify with a unit/integration test or scripted GraphQL call
- [x] 4.4 Fix Register phone/country/name validation and localize error strings across all CustomerApp locales; verify Belarusian-style and digit-length phones pass and non-Latin names are not rejected by Latin-only regex
- [ ] 4.5 Sweep remaining template-grade UI on primary paths (CreateAccount, Register, Menu, MenuItems, Cart, Checkout, MyOrders, Settings) for hardcoded English and broken empty states; verify no new lint issues via `node scripts/verify-changes.mjs`

## 5. Verification evidence

- [ ] 5.1 Run `node scripts/verify-changes.mjs` (and `--base` if on a branch) — must exit 0 for lintable modules; manually read backend/Website diffs
- [ ] 5.2 Run backend `python -m pytest -q` and `python -m compileall -q app tests` — all pass
- [ ] 5.3 Run Admin Playwright smoke (login → dashboard → orders → food list with images) — no console errors, images visible
- [ ] 5.4 Run CustomerApp Maestro (or emulator manual checklist): drawer, register, menu images, cart, place order COD — pass evidence captured
- [ ] 5.5 Independent Codex read-only review of the diff (brand leftovers, GraphQL contract, secrets) — blocking findings fixed or ruled

## 6. Deploy + APK

- [ ] 6.1 Reset/re-seed demo DB on the VPS (`/opt/pikupo`) with new media URLs; verify public site, admin, API health, and menu images over HTTPS
- [ ] 6.2 Rebuild Admin + Website static into `backend/static`; verify brand marks on live URLs
- [ ] 6.3 Rebuild release APK as Pikupo pointing at the live API; publish to `/downloads/pikupo-demo-v*.apk`; verify md5 and MIME; update `DEMO_RUNBOOK_RU.md` download URL
- [ ] 6.4 Final external curl + browser pass of site/admin/APK link; record credentials and URLs for the customer handoff
