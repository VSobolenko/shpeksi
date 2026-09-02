## Purpose

Defines the runtime end-to-end verification of the CustomerApp using Maestro, covering the key navigation path with visibility assertions that catch white screens and dead navigation, wired into an EAS build profile and a PR-triggered workflow.

## ADDED Requirements

### Requirement: Maestro flow coverage
The CustomerApp SHALL include Maestro YAML flows under `.maestro/` that drive the key navigation path: launch app, login, menu, categories, cart, and profile/settings.

#### Scenario: Flows exist
- **WHEN** the `.maestro/` directory is inspected
- **THEN** YAML flows exist that exercise login → menu → categories → cart → profile/settings, each using `launchApp`

### Requirement: Visibility assertions catch failures
The Maestro flows SHALL assert element visibility (`assertVisible`) at each screen so a white screen or broken navigation fails the flow, rather than merely passing when the app does not crash.

#### Scenario: White screen is caught
- **WHEN** a screen renders blank or navigation to it fails
- **THEN** the flow fails on `assertVisible` for that screen's expected element

#### Scenario: Screenshots captured
- **WHEN** a flow runs
- **THEN** it captures `takeScreenshot` evidence at key steps

### Requirement: E2E build profile
`eas.json` SHALL define an `e2e-test` profile with an iOS simulator Release build and an Android `apk` build type.

#### Scenario: Profile configurable
- **WHEN** the EAS e2e-test profile is selected
- **THEN** it builds an iOS simulator Release app and an Android APK

### Requirement: EAS workflow for E2E
The repo SHALL include `.eas/workflows/e2e-tests.yml` with a build job and a Maestro job (`type: maestro`) triggered on pull requests.

#### Scenario: PR-triggered E2E
- **WHEN** a pull request opens
- **THEN** the workflow builds the app and runs the Maestro flows via the `maestro` job type

### Requirement: Automated verification gates
The CustomerApp SHALL pass `npx expo-doctor`, `npx expo export`, `npm run lint`, and `npm test` with a clean (zero-error) result before the change is considered done.

#### Scenario: Gates green
- **WHEN** the verification commands run
- **THEN** expo-doctor, expo export, lint, and test all exit successfully with no errors
