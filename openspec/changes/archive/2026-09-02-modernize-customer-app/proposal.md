## Why

The CustomerApp still runs on Expo SDK 50 (React Native 0.73, React 18.2), which no longer meets the 2026 store submission requirements: Google Play requires `targetSdkVersion 36` (Android 16) with mandatory edge-to-edge, the App Store requires Xcode 26 / iOS 26 SDK builds, and both stores require privacy manifests (`PrivacyInfo.xcprivacy`) for tracking and OAuth SDKs. The app is also still coupled to the original owner's Expo account (`ninjas_code`), hardcodes the EAS project id and `updates.url`, and carries dead location/delivery code — so it cannot be submitted or maintained as-is. This change brings it to production-ready state without altering the fixed GraphQL contract.

## What Changes

- **Upgrade Expo SDK 50 → 57** (`expo@>=57.0.17`, react-native 0.86, react 19.2, Node >= 22.13), New Architecture enabled (the default since SDK 52). **BREAKING** (native runtime, React 19 API changes).
- **Android store compliance**: `targetSdkVersion 36` via `expo-build-properties`; edge-to-edge enabled with no opt-out; remove the `"orientation": "portrait"` lock for adaptive orientation; no Google Play Billing (payments remain Stripe/PayPal/COD).
- **iOS store compliance**: EAS build on Xcode 26 / iOS 26 SDK; add `PrivacyInfo.xcprivacy` (required-reason APIs for Amplitude + Google OAuth); keep `expo-tracking-transparency` and its usage string.
- **Framework modernization**: `@apollo/client` latest 3.x while keeping `subscriptions-transport-ws` + the legacy `WebSocketLink` (no `graphql-transport-ws`); reanimated 4.x + `react-native-worklets`, gesture-handler, screens, safe-area-context at SDK 57 versions.
- **Cleanup & de-branding**: remove `expo-location` and `ACCESS_*_LOCATION` and empty Google Maps keys; remove dead/commented code and stray `console.log`; remove `owner`/`currentFullName`/`originalFullName` `ninjas_code`, the hardcoded `updates.url`, and `extra.eas.projectId` (move to env via `app.config.js`); make `googleServicesFile` conditional on file presence; remove the "delivery address" `NSLocationWhenInUseUsageDescription` and any legacy-brand/rider/courier remnants (except fixed GraphQL-contract fields); delete the stale `patches/@expo+cli+0.17.13.patch`.
- **Contract immutability (critical)**: `src/apollo/*.js` operations and snake_case field names MUST NOT change; verified by a snapshot taken before the work and an empty diff after.
- **Runtime verification (new)**: Maestro E2E flows (`.maestro/`) covering login → menu → categories → cart → profile/settings, an `e2e-test` profile in `eas.json`, and `.eas/workflows/e2e-tests.yml` (PR-triggered) per Expo docs, using `assertVisible` to catch white screens and dead navigation.
- **Verification gates**: `npx expo-doctor`, `npx expo export`, `npm run lint`, `npm test` all green; EAS Android target 36 / iOS Xcode 26; empty GraphQL-contract diff.

## Capabilities

### New Capabilities

- `customer-app-platform-compliance`: Expo SDK 57 + store submission compliance (Android targetSdk 36 / edge-to-edge / adaptive orientation; iOS Xcode 26 + privacy manifest + tracking transparency), framework upgrades (Apollo 3.x over legacy WebSocket, reanimated 4), and de-branding/cleanup (Expo-account decoupling, location/delivery removal, stale patch).
- `customer-app-runtime-verification`: Maestro E2E flows with `assertVisible` coverage of the key navigation path, the `e2e-test` EAS profile, and the `.eas/workflows/e2e-tests.yml` PR workflow, plus the automated verification gates (expo-doctor / export / lint / test).

### Modified Capabilities

- `pickup-order-flow`: add a requirement that the customer GraphQL contract (`src/apollo/*.js` operations and snake_case field names) remain unchanged, verified by an empty snapshot diff.

## Impact

- **Code**: `CustomerApp/` — `package.json` (deps), `app.json`/`app.config.js` (compliance + env decoupling), `src/apollo/index.js` (Apollo 3.x WebSocket link compatibility), React 19 migration across screens/components, and removal of location/delivery code and dead code.
- **New files**: `PrivacyInfo.xcprivacy`, `.maestro/*.yaml`, `.eas/workflows/e2e-tests.yml`, and a GraphQL-contract snapshot artifact used by the verification step.
- **Config**: `eas.json` (add `e2e-test` profile + Xcode 26 image), `.env.example` (owner/projectId/updates env vars).
- **Dependencies**: expo 50 → 57, react-native 0.73 → 0.86, react 18.2 → 19.2, `@apollo/client` latest 3.x, reanimated 3 → 4 (+ `react-native-worklets`), remove `expo-location` and the stale patch.
- **No impact**: the GraphQL operations/fields in `src/apollo/*.js` (contract preserved); the backend is unchanged.
