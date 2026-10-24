## ADDED Requirements

### Requirement: No exemptions
`tools/check_rules.py` SHALL scan every text file in the repository and SHALL fail on any hit; it SHALL NOT exempt files by age or origin.

#### Scenario: Clean tree
- **WHEN** `python3 tools/check_rules.py --list-legacy` runs
- **THEN** it prints `legacy leak hits: 0` and the run ends with `check_rules: OK`

### Requirement: Single author identity
Every commit SHALL have the same author and committer email.

#### Scenario: Emails
- **WHEN** `git log --format=%ae%n%ce | sort -u` runs
- **THEN** exactly one address is printed

### Requirement: Backup exists
A local branch `pre-public-history` SHALL point at the pre-rewrite HEAD and SHALL NOT be pushed.

#### Scenario: Branch
- **WHEN** `git branch --list pre-public-history` runs
- **THEN** the branch is listed
