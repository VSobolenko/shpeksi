## 1. Phase 0 — Contract snapshot & isolation

- [ ] 1.1 Snapshot the GraphQL contract: copy `CustomerApp/src/apollo/server.js` to `openspec/changes/modernize-customer-app/contract-snapshot/server.js.before` and verify the file matches the live source byte-for-byte
- [ ] 1.2 Create an isolated feature branch/worktree (never on `main`) and verify `git status` shows the workspace on the new branch

## 2. Phase 1 — Expo SDK 57 upgrade

- [ ] 2.1 Upgrade Expo to SDK 57: run `npx expo install expo@latest` then `npx expo install --fix` in `CustomerApp/` and verify `npx expo-doctor` reports no invalid dependency versions
- [ ] 2.2 Pin the baseline in `package.json` (`"expo": ">=57.0.17"`) and remove now-implicit entries (`@babel/core`, `babel-preset-expo`, and `expo-constants` if unused) and verify `npm install` succeeds cleanly
- [ ] 2.3 Add `react-native-worklets` and bump reanimated 4, gesture-handler, screens, safe-area-context to SDK 57 versions and verify `npx expo-doctor` stays clean
- [ ] 2.4 Ensure New Architecture is the default (no `newArchEnabled` flag, no opt-out) and verify the config has no New Architecture opt-out

## 3. Phase 2 — Store/platform compliance

- [ ] 3.1 Add the `expo-build-properties` plugin with `android.targetSdkVersion: 36` and edge-to-edge enabled (no opt-out) and verify the resulting Android prebuild targets API 36
- [ ] 3.2 Remove `"orientation": "portrait"` and the `ACCESS_FINE_LOCATION`/`ACCESS_COARSE_LOCATION` permissions and empty Google Maps keys and verify `npx expo prebuild --no-install` (or config inspect) shows no portrait lock, no location permissions, no empty maps key
- [ ] 3.3 Set the iOS EAS build to the Xcode 26 / iOS 26 SDK image and verify `eas.json` references the correct image
- [ ] 3.4 Add `PrivacyInfo.xcprivacy` declaring required-reason APIs for Amplitude and Google OAuth and keep `expo-tracking-transparency` with its usage string; verify the manifest is present and the plugin remains enabled
- [ ] 3.5 Remove the "delivery address" `NSLocationWhenInUseUsageDescription` and verify the iOS config has no delivery location usage string

## 4. Phase 3 — De-branding & cleanup

- [ ] 4.1 Remove `owner`/`currentFullName`/`originalFullName` (`ninjas_code`), the hardcoded `updates.url`, and `extra.eas.projectId`; source them from env in `app.config.js` and document them in `.env.example`; verify `grep` finds no `ninjas_code` or hardcoded ids/URLs in source
- [ ] 4.2 Make `googleServicesFile` conditional on file existence (`fs.existsSync`) and verify the config omits it when no `google-services*.json` is present and no key file is committed
- [ ] 4.3 Remove `expo-location` from dependencies and verify `npm install`/lint pass without it
- [ ] 4.4 Remove dead code, commented-out blocks, and stray `console.log` across `CustomerApp/src/` and verify `npm run lint` (after wiring in Phase 5) reports zero and no stray `console.log` remains
- [ ] 4.5 Delete the stale `patches/@expo+cli+0.17.13.patch` and verify the `patches/` directory no longer contains it

## 5. Phase 4 — Code migration

- [ ] 5.1 Migrate React 19 breaking changes (remove `forwardRef`, `Context.Provider` → `<Context>`, provider-valued `useContext`) and verify the app compiles/renders with `npx expo export`
- [ ] 5.2 Bump `@apollo/client` to the latest 3.x while keeping `subscriptions-transport-ws` + `WebSocketLink` (no `graphql-transport-ws`); verify the subscription link import resolves and `graphql-transport-ws` is absent from dependencies
- [ ] 5.3 Verify `src/apollo/server.js` operations are untouched by diffing against the Phase 0 snapshot and confirm the diff is empty

## 6. Phase 5 — Runtime verification (Maestro + EAS)

- [ ] 6.1 Add `.maestro/` YAML flows (launchApp → assertVisible → tapOn → takeScreenshot) covering login → menu → categories → cart → profile/settings and verify the flows reference the correct app id and assert visible elements on each screen
- [ ] 6.2 Add an `e2e-test` profile to `eas.json` (iOS `simulator: true` Release; Android `buildType: apk`) and verify `eas config`/`eas build:configure` resolves the profile
- [ ] 6.3 Add `.eas/workflows/e2e-tests.yml` (build job → `type: maestro` job, PR trigger) per Expo docs and verify the workflow YAML is valid
- [ ] 6.4 Add a `lint` script + StandardJS `.eslintrc.json` (repo conventions) and a minimal jest test asserting the `src/apollo/server.js` operations, and verify `npm run lint` and `npm test` both pass with zero errors

## 7. Phase 6 — End-to-end verification

- [ ] 7.1 Run the full gate suite (`npx expo-doctor`, `npx expo export`, `npm run lint`, `npm test`) and verify all exit zero
- [ ] 7.2 Verify Android EAS build targets API 36 and iOS EAS build uses Xcode 26 / iOS 26 SDK (via build logs or the produced artifacts)
- [ ] 7.3 Run the Maestro flows (locally and/or via the EAS workflow) and verify they pass, including that `assertVisible` failures would be caught
- [ ] 7.4 Diff `src/apollo/*.js` against the snapshot and against the documented contract and verify the diff of operations/fields is empty
- [ ] 7.5 Run `openspec validate --strict modernize-customer-app` and verify the change validates with no errors
