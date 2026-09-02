## Purpose

The public marketing and landing website for the Pickup food-ordering platform, which introduces the brand, explains the pickup-only ordering flow, and directs visitors to the customer app and merchant panel across six languages.

## ADDED Requirements

### Requirement: Public landing site
The product SHALL include a public marketing/landing website that introduces the Pickup brand and its self-pickup food-ordering model.

#### Scenario: Visitor reaches the home page
- **WHEN** a visitor opens the site root
- **THEN** the site renders a hero section with the Pickup brand name, a value proposition, and a call-to-action

### Requirement: Standard landing-page sections
The site SHALL present a coherent marketing content set: hero, "how it works" (order → store prepares → pickup), feature highlights, a menu showcase, about, FAQ, contact, and download/CTA links.

#### Scenario: Sections are reachable
- **WHEN** a visitor navigates the site
- **THEN** every standard section (hero, how it works, features, menu showcase, about, FAQ, contact, downloads) is present and reachable via the navigation

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

### Requirement: Links to the apps
The site SHALL provide clearly labeled calls-to-action linking to the CustomerApp and Admin Dashboard, using configurable target URLs.

#### Scenario: App and merchant links
- **WHEN** a visitor clicks a download or merchant CTA
- **THEN** it navigates to the configured CustomerApp or Admin Dashboard target

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
