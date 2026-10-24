## ADDED Requirements

### Requirement: Data boundary is explicit
`docs/REQUIREMENTS.md` SHALL state which classes of data must never enter the repository (cluster aliases, environment maps, internal domains, customer names, ticket ids, audit logs) and name the mechanism that enforces it.

#### Scenario: Leak scan
- **WHEN** `python3 tools/check_rules.py` runs
- **THEN** files added after the base commit have zero leak-pattern hits, and legacy hits are reported without being modified

### Requirement: Requirements are numbered
Every requirement SHALL carry an id (R1..) that later changes cite.

#### Scenario: Traceability
- **WHEN** a change proposal is written
- **THEN** it cites at least one requirement id
