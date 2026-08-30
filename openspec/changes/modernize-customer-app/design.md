## Context

The CustomerApp is an Expo SDK 50 app (React Native 0.73, React 18.2) that already went through the earlier pickup/de-branding pass: `@apollo/client` 3.x is in place with `subscriptions-transport-ws` + `WebSocketLink`, secrets were moved to `environment.js`/`app.config.js`, and the pickup-only flow is established. The `src/apollo/server.js` file holds the fixed GraphQL operations; `src/apollo/index.js` holds the client wiring (no operations). No `ios/`/`android/` directories exist (Continuous Native Generation), so native projects are regenerated at build time. Local environment is Node v24.11.1 (satisfies the >= 22.13 requirement).

See proposal.md for motivation. The authoritative upgrade playbook is the `expo-upgrade` skill.

## Goals / Non-Goals

**Goals:**
- Land SDK 57 with a clean `expo-doctor`, a passing `expo export`, and passing lint/tests.
- Reach Android targetSdk 36 + edge-to-edge and an iOS 26 / Xcode 26 build with a privacy manifest.
- Keep the GraphQL contract byte-identical (verified by snapshot diff).
- Ship runnable Maestro flows wired into EAS.

**Non-Goals:**
- Changing any GraphQL operation or snake_case field name.
- Adding Google Play Billing or changing the payment methods (Stripe/PayPal/COD stay).
- Migrating the CustomerApp off `subscriptions-transport-ws` (explicitly out of scope).
- Touching the backend or the Admin Dashboard.

## Decisions

### 1. Upgrade straight to SDK 57 (skip 56), pin `expo@>=57.0.17`
Per the `expo-upgrade` skill, upgrade directly from SDK 55-or-earlier to 57 (never land on `expo@57.0.8` or below due to a Hermes V1 + worklets/reanimated memory regression). Use:

```bash
npx expo install expo@latest
npx expo install --fix
```

then `npx expo-doctor` and iterate until clean. Pin `"expo": ">=57.0.17"` in `package.json`.
- Alternative rejected: hand-editing every version string — error-prone across ~40 packages.

### 2. New Architecture: accept the default, remove the field
New Architecture is on by default from SDK 52; do not add `newArchEnabled` and do not opt out. The upgrade skill confirms Expo Go is New-Architecture-only from SDK 53.

### 3. React 19 migration
SDK 57 brings React 19.2. Apply the `expo-upgrade` React 19 reference changes: replace `forwardRef` with plain props/ref-as-prop, migrate `Context.Provider` → `<Context>`, and `useContext` usages where a provider value is now rendered. Scope to files that actually use these patterns; the app is largely hooks + React Navigation 6.

### 4. Reanimated 4 + worklets
Add `react-native-worklets` (required for reanimated 4 from SDK 54) and bump reanimated/gesture-handler/screens/safe-area-context to SDK 57 versions via `npx expo install`. Keep the babel preset minimal; remove `babel-preset-expo`/`@babel/core` from explicit `package.json` entries (now implicit in SDK 57).

### 5. Apollo 3.x with legacy WebSocket (do not migrate protocol)
Keep `subscriptions-transport-ws` and `@apollo/client/link/ws` (`WebSocketLink`) exactly as-is; do not add `graphql-transport-ws`. Bump `@apollo/client` to the latest 3.x. Verify `@apollo/client/link/ws` still resolves in the latest 3.x; if a 3.x minor dropped it, pin to the last 3.x that still ships `link/ws`.
- Alternative rejected: moving to `graphql-transport-ws` — violates the contract constraint.

### 6. Android compliance via `expo-build-properties`
Add the `expo-build-properties` plugin with `android.targetSdkVersion: 36` and `android.edgeToEdgeEnabled: true`; ensure no `edgeToEdgeEnabled: false` opt-out. Remove `"orientation": "portrait"` and the `ACCESS_FINE_LOCATION`/`ACCESS_COARSE_LOCATION` permissions and empty `googleMaps`/`googleMapsApiKey` keys.

### 7. iOS compliance via EAS + privacy manifest
Set the iOS EAS build image to the Xcode 26 line (`image: latest` / the 26 SDK image). Add `PrivacyInfo.xcprivacy` (required-reason APIs for Amplitude and Google OAuth) and keep `expo-tracking-transparency` with its usage string. Remove the "delivery address" `NSLocationWhenInUseUsageDescription`.

### 8. Account decoupling via `app.config.js` env
`app.config.js` already loads `.env`. Extend it to source `owner`/`slug`-scoped values and EAS ids from env instead of hardcoding:
- Remove `owner`, `currentFullName`, `originalFullName` (`ninjas_code`).
- `updates.url` set only when `EXPO_UPDATES_URL` is present.
- `extra.eas.projectId` set from `EAS_PROJECT_ID` when present.
- `googleServicesFile` set only when the file exists (`fs.existsSync`), never committed.
- Document the new vars in `CustomerApp/.env.example`.

### 9. Contract snapshot strategy
Before touching code, snapshot `src/apollo/server.js` (the operation-bearing file) verbatim into the change folder. After the work, diff the operations/fields; the diff must be empty. `src/apollo/index.js` (client wiring only, no operations) is allowed to change for Apollo 3.x compatibility, but its exported operation strings (none) are covered by the `server.js` snapshot. Add a small jest test that asserts the exported operations still parse as expected, which doubles as the `npm test` smoke test (there are currently zero tests, and bare jest fails on "no tests found").

### 10. Lint wiring
There is no CustomerApp `.eslintrc` and no `lint` script today (only `lint:fix`). Add a `lint` script and a StandardJS-based `.eslintrc.json` mirroring the repo conventions (no semicolons, single quotes, 2-space indent, `react/prop-types: 0`) so `npm run lint` reports zero.

### 11. Maestro + EAS E2E
Add `.maestro/` YAML flows (one per screen sequence) using `launchApp` (with the app id), `assertVisible`, `tapOn`, and `takeScreenshot`. Add an `e2e-test` profile to `eas.json` (`ios: { simulator: true, distribution: internal, ... }, android: { buildType: "apk" }`). Add `.eas/workflows/e2e-tests.yml` with a `build` job followed by a `maestro` (`type: maestro`) job triggered on PRs, per the Expo docs. Flows must assert visible elements (not merely "no crash") so white screens and dead navigation fail.

## Risks / Trade-offs

- **SDK 50 → 57 is a large jump** (React 19, reanimated 4, package renames like expo-av→expo-audio). → Mitigation: rely on `expo install --fix` + `expo-doctor` + `expo export` as a fast feedback loop; consult the `expo-upgrade` reference files for React 19 / New Architecture / React Compiler.
- **`@apollo/client/link/ws` may be dropped in a later 3.x.** → Mitigation: verify the import early; pin to the last 3.x that ships `link/ws` if needed (no protocol change).
- **Reanimated 4 / worklets runtime issues on the new Hermes.** → Mitigation: install `react-native-worklets`, use SDK 57's correct babel setup, and avoid Worklets Bundle Mode (unsupported/experimental per the skill).
- **Native config is regenerated by CNG**, so plugin/`expo-build-properties` settings only take effect at build time. → Mitigation: validate via `npx expo prebuild --no-install` diff and a real EAS build before declaring success.
- **Maestro needs a runnable device/simulator locally or EAS.** → Mitigation: the EAS workflow is the source of truth; run locally when an emulator/simulator is available.
- **`npm test` currently has no tests.** → Mitigation: add the contract smoke test so the gate is meaningful and green.

## Migration Plan

1. Snapshot the GraphQL contract (`src/apollo/server.js`) into the change folder.
2. Create an isolated feature branch/worktree (never on `main`).
3. Upgrade deps (`expo install expo@latest` + `--fix`) and fix `expo-doctor` findings.
4. Apply config changes (`app.json`/`app.config.js`/`eas.json`, privacy manifest, `.env.example`).
5. Migrate code (React 19, Apollo 3.x wiring, reanimated 4, remove location/dead code, de-brand).
6. Add Maestro flows, EAS e2e profile, workflow, lint config, and the contract test.
7. Verify: `expo-doctor`, `expo export`, `npm run lint`, `npm test`, EAS Android (target 36) + iOS (Xcode 26), Maestro flows green, contract diff empty.
8. Rollback: revert the branch; the snapshot diff proves the contract was preserved or pinpoints any drift.

## Open Questions

None — all decisions that could change the specs or task breakdown are resolved above.
