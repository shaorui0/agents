## ADDED Requirements

### Requirement: Pre and post records pair
`audit_pre.sh` SHALL write a `phase=pre` record with `op_id`, command and INTENT before a mutating infra command runs; `audit_log.sh` SHALL write a `phase=post` record carrying the same `op_id`.

#### Scenario: Pair
- **WHEN** pre then post run for the same command
- **THEN** both records share one `op_id`

### Requirement: Missing intent is visible
When no INTENT line is present the pre record SHALL have `reasoning: null`.

#### Scenario: Null reasoning
- **WHEN** pre runs for a mutating command without INTENT
- **THEN** the record's `reasoning` is null

### Requirement: Audit path is configurable and ignored by git
The audit directory SHALL come from `AGENTS_AUDIT_DIR` and default to `records/audit/`; `*.jsonl` there SHALL be gitignored.

#### Scenario: Custom dir
- **WHEN** `AGENTS_AUDIT_DIR` is set
- **THEN** records are written there
