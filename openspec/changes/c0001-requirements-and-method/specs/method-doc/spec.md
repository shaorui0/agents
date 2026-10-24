## ADDED Requirements

### Requirement: Model diagrams
`docs/METHOD.md` SHALL contain at least two mermaid diagrams: the phase-lock state machine and the four-gate flow.

#### Scenario: Count
- **WHEN** `python3 tools/check_rules.py` runs
- **THEN** it counts at least two mermaid blocks in `docs/METHOD.md`

### Requirement: Executable method and failure modes
`docs/METHOD.md` SHALL contain a step table with input, action, criterion and artifact per step, and a failure-mode table that says what each mechanism defends against.

#### Scenario: Review
- **WHEN** a reviewer reads the step table
- **THEN** each step names an artifact that can be checked
