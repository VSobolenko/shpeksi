---
name: "/ui-verify"
id: "ui-verify"
category: "Review"
description: "Runtime UI verifier — change-impact sweep for blank screens / broken navigation (web: Playwright, native: Maestro)"
---

# /ui-verify — runtime UI verifier

Catches what static review cannot. `bugbot`/`security-review` read code and
diffs; `npm run build`/`pytest` prove the code *compiles* and the logic *passes*.
None of them prove the UI *renders*. A blank screen or dead navigation with no
exception passes every static gate. This role closes that gap: it launches the
app and drives a real runtime over everything the change could have touched,
then routes failures back for rework.

- **Web** (Admin Dashboard) → **Playwright** (real browser).
- **Native** (CustomerApp — React Native + Expo) → **Maestro** (YAML flows on
  emulator/simulator; no native code changes; Expo/EAS support it officially).

This is the "second agent that checks the running app". It does NOT fix code —
it finds runtime defects and hands them to the `/ship` fix loop.

## Core principle: change-impact scope, never a fixed list

A fixed smoke list misses the regression next door. Derive the verification
surface from the change, and err toward **over**-covering: anything the change
touched, and anything that depends on what it touched.

### 1. Read the diff
`git diff --name-only` (uncommitted) or `git diff <base>...HEAD --name-only`
(branch). List every changed file.

### 2. Classify blast radius
Map changed files to what could break, using the repo's structure:

- **Shared / global** (Sidebar, Navbar, Footer, routes, `apollo/server`, i18n,
  theme/SCSS, `index.jsx`, router setup — or, in RN: shared components, screens,
  `components/index.js`, navigation stacks, `apollo/*`, translations) →
  **sweep every main screen/route**, because a shared change can blank every one.
- **Local** (a view or a component) → cover: the screen(s) that render it, its
  direct neighbors, and any screen that imports the changed module (follow the
  import graph outward). A change to a shared `<Card>` affects every list that
  uses it.

When unsure whether something is affected, **include it**. Over-checking is the
safe default; this role's whole point is that a false "all good" is worse than a
slower check.

### 3. Build the checklist
Emit one item per screen/flow to exercise: entry point, and the concrete
assertion ("renders the food list", "nav to Settings works"). Cover: every
screen in the blast radius, plus the key flows crossing changed code (login →
list → detail → action). Applies to both web and native targets.

## Steps

### 0. Determine the target(s)
- **Admin Dashboard** (React + Vite, web) → Playwright drives it directly.
- **CustomerApp** (React Native + Expo) → native screens are driven by
  **Maestro**. An Expo **web** export, if present, is an *additional* Playwright
  surface, not a substitute for native.
- If the change touches **both** (e.g. the GraphQL contract), run both.

### 1. Determine impact surface
Run the diff → blast-radius → checklist above. Write the checklist down (it is
the record of what was and was not covered).

### 2. Bring up the target (+ backend)
- **Web:** start the dev server / preview (`npm run dev` or build+preview).
- **Native:** build or install the app on an emulator/simulator (Expo Go or an
  EAS-built binary) — see the Maestro recipe below.
- Data-dependent screens need the backend running (and reachable) — a blank
  screen may be a backend/DNS issue, not UI. Note the backend state so failures
  are not misattributed.

### 3. Verify the driver is available
- **Playwright:** check the MCP catalog for the Playwright tools (navigate /
  snapshot / click / screenshot / console). If the Playwright MCP server is not
  connected, fall back to the Playwright CLI (`npx playwright`).
- **Maestro:** check that the Maestro CLI is installed (`maestro --version`); if
  not, install it (`curl -fsSL https://get.maestro.mobile.dev | bash`). Verify a
  device is available (`maestro hierarchy` or `maestro test` against a booted
  emulator). If Maestro cannot run locally, use **EAS Workflows** (the `maestro`
  job type) to run the same flows in Expo's CI — same YAML, no local device.

### 4. Drive each checklist item

**Web (Playwright)** — for every screen/flow:
1. **Navigate** to it (route or click the nav entry — click the real UI, don't
   short-circuit with URLs when testing navigation itself).
2. **Assert it renders** — the key content is present, not a blank shell.
3. **Assert navigation works** — menu/history/back transitions actually land.
4. **Check console** for errors (unhandled rejections, failed imports, 404s).
5. **Capture evidence** — a screenshot per screen (success and failure).

**Native (Maestro)** — for every screen/flow, a YAML flow that:
1. **Launches** the app (clear state), then navigates via real taps/swipes.
2. **Asserts content** with `assertVisible` on the key element (a screen with a
   perpetual spinner or empty shell must FAIL, not just "no crash").
3. **Asserts navigation** — tap a tab/link, `assertVisible` on the destination.
4. **Captures evidence** — `takeScreenshot` on success and failure (Maestro
   screenshots land in the run output; EAS records them).

Record PASS / FAIL per item, with the evidence path.

### 5. Report and route
- **PASS** — every item green; state the coverage ("N screens, M flows").
- **FAIL** — for each failure: screen, symptom (blank / dead nav / console
  error / failed assertion), and the evidence. Hand the list to the `/ship` fix
  loop (resume the implementer, then scoped re-review, then re-run `/ui-verify`
  on the affected surface — not the whole app).

## Checks per screen (the assertion set)
- **Renders:** key element present (not blank / not stuck on a spinner).
- **Navigation:** menu/tabs/links/back reach the right screen.
- **Data:** when a screen lists data, the list (or its empty state) appears — a
  perpetual loader is a failure.
- **Errors:** web — console clean; native — no crash/redbox during the visit.

## Mobile (native) — Maestro recipe (ready-made)

This is the standard 2026 setup, straight from Expo/EAS docs. Use it; don't
reinvent it. Flows live **outside** the app (no native deps, no build changes).

1. **Flows** — `.maestro/` at the project root, one YAML per journey. Minimal
   shape:

   ```yaml
   appId: com.forkly.app        # your app id
   ---
   - launchApp:
       clearState: true
   - assertVisible: "Menu"
   - tapOn: "Categories"
   - assertVisible: "Categories"   # destination actually rendered
   - takeScreenshot: categories
   ```

2. **Build profile** — add an `e2e-test` profile to `CustomerApp/eas.json`:
   - iOS: `"simulator": true`, `"buildConfiguration": "Release"`
   - Android: `"buildType": "apk"`

3. **Local run** — boot an emulator/simulator, install the build, then
   `maestro test .maestro/`.

4. **CI (EAS Workflows)** — `.eas/workflows/e2e-tests.yml` with a `build` job
   (`profile: e2e-test`) followed by a `maestro` job referencing the `build_id`
   and `flow_path`. Trigger on pull requests. See:
   - https://docs.expo.dev/tutorial/cicd/e2e-tests/
   - https://docs.expo.dev/eas/workflows/examples/e2e-tests

## Limitations (state these, don't hide them)
- **Web vs native are different drivers.** Playwright does not drive native RN
  screens; Maestro does not drive a browser. Cover each surface with its own
  driver; an Expo web export is *extra* coverage, never a native substitute.
- **Environment-dependent.** Auth, data, and network shape results. A failure on
  a backend-down screen is an environment failure, not a UI regression — report
  it distinctly.
- **Drivers must be available.** Playwright MCP offline → fall back to CLI;
  Maestro CLI missing → install it or fall back to EAS Workflows. Never skip the
  sweep because a driver is missing.

## Output

```
## UI verification

**Target:** Admin Dashboard (web) / CustomerApp (native)
**Driver:** Playwright / Maestro
**Impact surface:** <shared change → full sweep | local change → N screens>
**Backend state:** <up / down>

### Coverage
- [PASS] Categories — renders list (evidence: ...)
- [PASS] Orders — nav from menu (evidence: ...)
- [FAIL] Addons — blank screen, console: chunk load error (evidence: ...)

### Verdict
PASS / FAIL (N failures → routed to fix loop)
```
