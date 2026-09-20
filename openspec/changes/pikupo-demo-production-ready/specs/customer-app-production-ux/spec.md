## Purpose

Defines production-ready CustomerApp UX for demos and handoff: navigation chrome, authentication, registration, and image wiring must work without template-grade breakage.

## ADDED Requirements

### Requirement: Drawer labels remain readable
The left navigation drawer SHALL align icon and label on one row without clipping, overlapping the icon, or overflowing the drawer width for the shipped locales (`en`, `ar`, `de`, `fr`, `km`, `ru`, `zh`).

#### Scenario: Long locale label
- **WHEN** the device language is Russian (or another shipped locale with long menu labels) and the user opens the drawer
- **THEN** each drawer item label is fully readable (wraps or truncates with ellipsis on a second line as designed) and does not overlap its icon

#### Scenario: Layout matches intended spacing
- **WHEN** the drawer is compared against the intended layout after the Pikupo fork
- **THEN** label horizontal spacing does not rely on large negative margins that push text under icons

### Requirement: Google sign-in either works or is honestly disabled
Google sign-in SHALL either complete a successful session for a configured demo build, or be clearly disabled/hidden with no dead tap that surfaces an opaque HTTP 400. When Google credentials are configured, the app SHALL obtain an ID/access token via Expo AuthSession and the backend SHALL accept a Google login of type `google` without returning a client 400 for a valid token exchange.

#### Scenario: Configured Google sign-in succeeds
- **WHEN** valid Google OAuth client IDs are present in the CustomerApp env and the user completes the Google account picker on Create Account
- **THEN** the app obtains a token, calls `login` with `type: "google"`, and lands the user in an authenticated session

#### Scenario: Unconfigured Google sign-in does not look broken
- **WHEN** Google client IDs are missing or incomplete in the build env
- **THEN** the Google button is disabled or absent with a clear affordance, and tapping it does not show an unexplained HTTP 400

### Requirement: Phone registration accepts realistic numbers
Registration SHALL accept international phone numbers used in the demo markets, apply a visible country prefix consistently with the submitted value, and SHALL NOT reject valid non-Latin names that otherwise meet length rules for the demo.

#### Scenario: Register with Belarusian-style phone
- **WHEN** a user registers with a phone of 9–15 digits after the country code handling used by the form
- **THEN** validation accepts the number and `createUser` succeeds (assuming unique email)

#### Scenario: Validation messages are localized
- **WHEN** registration validation fails
- **THEN** error strings come from the active locale files, not hardcoded English-only literals

### Requirement: Order and cart images use the shared image component contract
Every CustomerApp surface that shows a food or order thumbnail SHALL pass the image source through the shared image component's documented prop (`imgSource` or equivalent) so thumbnails render; surfaces SHALL NOT pass a wrong prop name that silently yields a blank or broken image.

#### Scenario: Past orders list shows thumbs
- **WHEN** a customer opens My Orders with completed orders that have food `img_url` values
- **THEN** each row shows a thumbnail image (seeded URL or branded placeholder)

#### Scenario: Cart line shows food image
- **WHEN** a customer adds a seeded food to the cart and opens Cart
- **THEN** the line item shows that food's image or the branded placeholder
