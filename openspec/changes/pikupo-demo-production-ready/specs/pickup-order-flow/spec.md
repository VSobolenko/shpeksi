## ADDED Requirements

### Requirement: Demo pickup catalog presents food photos
A freshly seeded demo environment used for customer demos SHALL expose category and food images over the same GraphQL fields the CustomerApp already reads (`img_menu`, `img_url`), so the pickup browse → cart → order path shows real photographs end-to-end.

#### Scenario: Browse menu with photos
- **WHEN** a demo customer opens the menu after a clean demo seed
- **THEN** category cards and food rows display images from the seed, not empty white placeholders

#### Scenario: Order history with photos
- **WHEN** a demo customer views an order created from seeded foods
- **THEN** order line thumbnails resolve to the seeded food images
