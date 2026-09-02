## Purpose

Defines the platform and store-submission requirements the CustomerApp must satisfy to be production-ready for the 2026 app stores, including the Expo SDK 57 baseline, Android and iOS compliance, framework compatibility, and the removal of account coupling and dead delivery/location code.

## ADDED Requirements

### Requirement: Expo SDK 57 baseline
The CustomerApp SHALL run on Expo SDK 57 (`expo@>=57.0.17`) with React Native 0.86 and React 19.2, and SHALL build and run under Node.js >= 22.13. The New Architecture SHALL be enabled (the SDK default).

#### Scenario: Expo SDK 57 resolved
- **WHEN** `npx expo-doctor` runs in `CustomerApp/`
- **THEN** it reports the SDK 57 toolchain with no invalid dependency versions

#### Scenario: App exports on the upgraded stack
- **WHEN** `npx expo export` runs
- **THEN** the bundle exports successfully with no errors on the SDK 57 / React 19 stack

### Requirement: Android 16 target and edge-to-edge
The CustomerApp SHALL target Android 16 (`targetSdkVersion` 36) via `expo-build-properties`, and SHALL render edge-to-edge with no opt-out flag.

#### Scenario: Android build targets API 36
- **WHEN** an Android EAS build completes
- **THEN** the produced APK targets `targetSdkVersion` 36 and edge-to-edge is enabled without an opt-out

### Requirement: Adaptive orientation
The CustomerApp SHALL NOT lock orientation to portrait; it SHALL support adaptive orientation on both platforms.

#### Scenario: No portrait lock
- **WHEN** the app configuration is inspected
- **THEN** there is no `"orientation": "portrait"` restriction in the Expo config

### Requirement: No Google Play Billing
The CustomerApp SHALL NOT include Google Play Billing; payments SHALL remain Stripe, PayPal, and cash-on-delivery only.

#### Scenario: No billing SDK
- **WHEN** the Android dependency set is inspected
- **THEN** no Google Play Billing SDK or billing permission is present

### Requirement: iOS 26 SDK build
The CustomerApp SHALL be built on Xcode 26 / the iOS 26 SDK through EAS for App Store submission.

#### Scenario: iOS build image
- **WHEN** an iOS EAS build runs
- **THEN** it uses the Xcode 26 / iOS 26 SDK build environment

### Requirement: Privacy manifest
The CustomerApp SHALL ship a `PrivacyInfo.xcprivacy` declaring required-reason API usage for the Amplitude analytics and Google OAuth SDKs.

#### Scenario: Privacy manifest present
- **WHEN** the app is submitted for review
- **THEN** `PrivacyInfo.xcprivacy` declares required-reason API categories for Amplitude and Google OAuth

### Requirement: Tracking transparency
The CustomerApp SHALL keep `expo-tracking-transparency` and its usage string so tracking consent is requested before any tracking.

#### Scenario: Tracking consent string
- **WHEN** the app requests tracking permission
- **THEN** the configured usage string is shown and the plugin remains enabled

### Requirement: Apollo 3.x over legacy WebSocket
The CustomerApp SHALL use the latest `@apollo/client` 3.x while keeping `subscriptions-transport-ws` and the legacy `WebSocketLink` protocol, and SHALL NOT introduce `graphql-transport-ws`.

#### Scenario: Legacy subscription protocol preserved
- **WHEN** the app opens a GraphQL subscription
- **THEN** it connects over `subscriptions-transport-ws` via `WebSocketLink`, and `graphql-transport-ws` is absent from dependencies

### Requirement: Reanimated 4 and native UI libraries
The CustomerApp SHALL run reanimated 4.x with `react-native-worklets`, plus gesture-handler, screens, and safe-area-context at their SDK 57 versions.

#### Scenario: Reanimated 4 with worklets
- **WHEN** an animation runs on the upgraded stack
- **THEN** reanimated 4 worklets execute with `react-native-worklets` installed

### Requirement: No location capability
The CustomerApp SHALL remove `expo-location`, the `ACCESS_FINE_LOCATION`/`ACCESS_COARSE_LOCATION` permissions, and empty Google Maps API keys.

#### Scenario: Location removed
- **WHEN** the dependency set and config are inspected
- **THEN** `expo-location` and `ACCESS_*_LOCATION` are absent and no empty Google Maps keys remain

### Requirement: Dead code and log cleanup
The CustomerApp SHALL remove dead code, commented-out blocks, and stray `console.log` statements.

#### Scenario: No debug residue
- **WHEN** lint runs over `CustomerApp/`
- **THEN** no stray `console.log` or commented-out code blocks remain in source

### Requirement: Expo account decoupling
The CustomerApp SHALL NOT hardcode the `owner`, `currentFullName`, or `originalFullName` (`ninjas_code`), the `updates.url`, or `extra.eas.projectId`; these SHALL be sourced from environment via `app.config.js`.

#### Scenario: No account coupling in source
- **WHEN** the Expo config is inspected
- **THEN** no `ninjas_code` value, hardcoded `updates.url`, or hardcoded `extra.eas.projectId` appears, and each is read from env

### Requirement: Conditional Google services file
The CustomerApp SHALL reference `googleServicesFile` only when the file exists on disk, and SHALL NOT commit any Google services key file.

#### Scenario: Google services file optional
- **WHEN** the app config is evaluated without a `google-services*.json` present
- **THEN** `googleServicesFile` is omitted, and no Google services key is committed

### Requirement: No delivery or vendor remnants
The CustomerApp SHALL remove the "delivery address" `NSLocationWhenInUseUsageDescription` and any Enatega/rider/courier remnants, EXCEPT the fixed snake_case field names of the GraphQL contract.

#### Scenario: No delivery usage string
- **WHEN** the iOS configuration is inspected
- **THEN** there is no "delivery address" location usage description

#### Scenario: No vendor branding remnants
- **WHEN** the source is searched
- **THEN** no Enatega/rider/courier string remains outside the fixed GraphQL contract fields

### Requirement: Stale patch removal
The CustomerApp SHALL delete the outdated `patches/@expo+cli+0.17.13.patch`.

#### Scenario: Patch removed
- **WHEN** the `patches/` directory is inspected
- **THEN** `@expo+cli+0.17.13.patch` no longer exists
