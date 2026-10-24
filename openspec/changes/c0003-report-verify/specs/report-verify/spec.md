## ADDED Requirements

### Requirement: Required sections
`verify.py` SHALL exit 2 when any of Investigation Plan, Extracted Signals, Investigation Log, Conclusions, Slack Response, Operation Commands or Links is missing.

#### Scenario: Missing section
- **WHEN** a report has no Links section
- **THEN** exit code is 2 and the output names the section

### Requirement: Evidence chain
Each conclusion SHALL cite at least one `[E<n>]`, and each cited id SHALL be defined in the Investigation Log. A defined evidence item without a timestamp or without a query/command SHALL warn.

#### Scenario: Dangling reference
- **WHEN** a conclusion cites `[E9]` and the log defines only E1..E4
- **THEN** exit code is 2

### Requirement: No over-assertion in the Slack reply
The Slack Response SHALL NOT contain assertion words (definitely, certainly, clearly, "all customers", "root cause is" without hedge, and similar).

#### Scenario: Assertive reply
- **WHEN** the reply says "definitely"
- **THEN** exit code is 2

### Requirement: Mutating commands carry INTENT
Every mutating command in Operation Commands SHALL be preceded by `# INTENT:`, using the Gate 3 classifier to decide what is mutating.

#### Scenario: Missing INTENT
- **WHEN** the section contains `kprod scale deploy x` with no INTENT line
- **THEN** exit code is 2

### Requirement: Fixtures pin behaviour
`fixtures/report_ok.md` SHALL exit 0 and `fixtures/report_bad.md` SHALL exit 2.

#### Scenario: Make target
- **WHEN** `make verify` runs
- **THEN** it exits 0 only if ok gives 0 and bad gives 2
