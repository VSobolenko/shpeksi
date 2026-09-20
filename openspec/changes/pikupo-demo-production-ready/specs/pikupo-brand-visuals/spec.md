## Purpose

Defines how Pikupo looks across CustomerApp, Admin Dashboard, Website, and demo catalog data: brand marks, placeholders, and food imagery must read as one product, not as leftover Enatega/Argon stock.

## ADDED Requirements

### Requirement: Consistent Pikupo brand marks
Every customer-facing surface SHALL display a Pikupo brand mark (wordmark and/or bag icon) that matches the product name "Pikupo" and SHALL NOT display third-party white-label marks, Argon theme logos, or external CDN brand art for primary branding.

#### Scenario: Auth and shell branding
- **WHEN** a user opens CustomerApp auth screens, the Admin Dashboard shell, or the marketing Website header/footer
- **THEN** the visible logo/wordmark is Pikupo and no Enatega, Ninjas Code product mark, or Argon React logo is shown as the product brand

#### Scenario: Favicons and share cards
- **WHEN** a browser loads the Admin Dashboard or Website
- **THEN** favicon and Open Graph images show Pikupo branding (name and/or mark), not a generic or third-party mark

### Requirement: No white empty placeholders for missing media
When a food, category, or order thumbnail has no remote URL, the UI SHALL show a Pikupo-branded placeholder graphic. It SHALL NOT render a blank white rectangle as the primary visual.

#### Scenario: Missing food image in the menu
- **WHEN** a menu item has an empty or null `img_url`
- **THEN** the CustomerApp shows a branded placeholder image, not a solid white box

#### Scenario: Missing category image
- **WHEN** a category has an empty or null `img_menu`
- **THEN** the category card or header shows a branded placeholder, not a solid white box

### Requirement: Demo catalog includes real food imagery
The demo seed used for customer demos SHALL populate category and food image fields with resolvable HTTPS URLs (or equivalent app-reachable URIs) so a freshly seeded stand shows photographed food, not only placeholders.

#### Scenario: Fresh demo seed has images
- **WHEN** the demo catalog seed completes on a clean database
- **THEN** every seeded category has a non-empty `img_menu` and every seeded food has a non-empty `img_url` that the CustomerApp and Admin Dashboard can load

#### Scenario: Cart and orders show thumbs
- **WHEN** a demo customer views the cart or an active/past order that contains seeded foods
- **THEN** line-item thumbnails resolve to the seeded food images (or the branded placeholder only if the network fetch fails)

### Requirement: No third-party stock photos in customer-visible chrome
Admin Dashboard chrome that a merchant sees during a demo (sidebar avatar fallbacks, navbar avatar, login brand) SHALL NOT use Creative Tim / Argon stock team photos or unrelated framework marketing images as the default look.

#### Scenario: Admin chrome without stock faces
- **WHEN** an admin opens the dashboard after login
- **THEN** default avatars or brand areas do not show stock "team-*.jpg" Creative Tim photographs
