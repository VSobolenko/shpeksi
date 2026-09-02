## ADDED Requirements

### Requirement: Customer GraphQL contract immutability
The CustomerApp SHALL preserve its GraphQL contract exactly: the operations and snake_case field names in `src/apollo/*.js` SHALL NOT change as part of this modernization.

#### Scenario: Snapshot diff is empty
- **WHEN** a snapshot of `src/apollo/*.js` is taken before the change and diffed against the files after the change
- **THEN** the diff of GraphQL operation names and snake_case field names is empty

#### Scenario: Contract matches specs
- **WHEN** the `src/apollo/*.js` files are diffed against the GraphQL contract documented in the specs
- **THEN** there are no operation or field differences
