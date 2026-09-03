## Purpose

The public marketing website for the Pickup ordering platform, positioned business-to-business: it sells the white-label self-pickup ordering platform to restaurants, cafés, and merchants who want to launch their own branded ordering app, across seven languages.

## ADDED Requirements

### Requirement: Business-to-business marketing site
The product SHALL include a public marketing website that advertises the Pickup white-label ordering platform to restaurants and merchants, positioning it as a way to launch their own branded self-pickup ordering app.

#### Scenario: Merchant reaches the home page
- **WHEN** a restaurant owner or merchant opens the site root
- **THEN** the site renders a hero section with the Pickup platform name, a merchant-focused value proposition ("launch your own pickup ordering app"), and a call-to-action to request a demo or get started

### Requirement: Merchant-focused landing sections
The site SHALL present a coherent merchant-focused content set: hero, "how it works" for the merchant (set up menu → receive orders → hand over at pickup), platform features, a "for your customers" section, about, FAQ for restaurant owners, contact, and a get-started/demo CTA.

#### Scenario: Merchant sections are reachable
- **WHEN** a visitor navigates the site
- **THEN** every merchant-focused section (hero, how it works, platform features, for-your-customers, about, FAQ, contact, get-started) is present and reachable via the navigation

### Requirement: White-label positioning
The site SHALL describe the platform as a white-label solution — the merchant's own brand, logo, and colors — and SHALL NOT present the site as a consumer food-ordering app or a single restaurant's menu.

#### Scenario: No consumer or single-restaurant framing
- **WHEN** the site content is reviewed
- **THEN** the copy sells the platform to merchants (branded app, menu/order management, no delivery overhead), with no consumer "order your food" messaging and no single restaurant's menu showcase

### Requirement: Pickup-only branding
The site SHALL describe the product as a pickup-only service and SHALL NOT mention delivery, riders, couriers, or the "Enatega" name (any casing) in any content or asset.

#### Scenario: No delivery or legacy branding
- **WHEN** the site content and assets are reviewed
- **THEN** no delivery-, rider-, courier-, or "Enatega"-related text or imagery is present

### Requirement: Multilingual content
The site SHALL support seven languages — `en`, `ar`, `de`, `fr`, `km`, `ru`, `zh` — and every user-facing string SHALL be available in all seven languages.

#### Scenario: Language completeness
- **WHEN** the site is switched to any supported language
- **THEN** every user-facing string renders in that language with no missing or untranslated keys

#### Scenario: Language switcher
- **WHEN** a visitor selects a language from the language switcher
- **THEN** the entire site content re-renders in the selected language

### Requirement: Locale-aware default language
The site SHALL select the initial display language from the visitor's browser/system locale when it is one of the supported languages, falling back to English otherwise; the visitor's explicit choice SHALL be remembered across visits.

#### Scenario: Initial language follows the visitor's locale
- **WHEN** a visitor whose browser language is Russian opens the site for the first time
- **THEN** the site renders in Russian without any manual selection

#### Scenario: Fallback to English
- **WHEN** a visitor's browser language is not among the supported languages
- **THEN** the site renders in English

#### Scenario: Choice is remembered
- **WHEN** a visitor selects a language and later returns to the site
- **THEN** the site renders in the previously selected language

### Requirement: Right-to-left rendering for Arabic
The site SHALL render Arabic (`ar`) content right-to-left, including layout direction.

#### Scenario: Arabic layout direction
- **WHEN** the site language is set to Arabic
- **THEN** text and layout flow right-to-left

### Requirement: Merchant call-to-action targets
The site SHALL provide clearly labeled calls-to-action to request a demo and to open the merchant panel, using configurable target URLs.

#### Scenario: Demo and merchant-panel links
- **WHEN** a visitor clicks the demo or merchant-panel CTA
- **THEN** it navigates to the configured demo/contact and merchant-panel targets

### Requirement: Static production build
The site SHALL build to a static, deployable artifact via a single command and SHALL run locally via a dev server.

#### Scenario: Production build succeeds
- **WHEN** the production build command is run
- **THEN** a static `dist/` artifact is produced with no build errors and can be served by any static host

#### Scenario: Local development
- **WHEN** the dev server command is run
- **THEN** the site is served locally for development with hot reload

### Requirement: Responsive layout
The site SHALL render correctly across mobile and desktop viewports.

#### Scenario: Mobile and desktop rendering
- **WHEN** the site is viewed on a mobile viewport and on a desktop viewport
- **THEN** the layout adapts with no broken or overflowing content
