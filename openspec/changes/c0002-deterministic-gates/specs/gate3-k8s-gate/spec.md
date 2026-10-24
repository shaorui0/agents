## ADDED Requirements

### Requirement: Production mutation is blocked
The gate SHALL exit 2 for any mutating command on a prod-tier alias and SHALL print the command so a human can run it.

#### Scenario: Scale on prod
- **WHEN** stdin carries `kprod scale deploy x --replicas=1 -n y`
- **THEN** the exit code is 2 and stderr contains the command

### Requirement: Unknown aliases fail closed
An infra command whose alias is not in `config/env_map.yaml` SHALL be treated as prod. A missing or unreadable config SHALL exit 2.

#### Scenario: Unknown alias
- **WHEN** stdin carries `kmystery scale deploy x`
- **THEN** the exit code is 2 and stderr says the alias is unclassified

### Requirement: Hard blocks apply to every tier
Deleting a namespace, a persistent volume, using `--all` or all-namespaces with delete, IAM mutations, instance termination and an explicit prod `--context` SHALL exit 2 on every tier, including dev.

#### Scenario: Dev namespace delete
- **WHEN** stdin carries `kdev delete ns foo`
- **THEN** the exit code is 2

### Requirement: Reads, dry-runs and dev work pass
Read-only commands, `--dry-run` commands and non-delete mutations on dev SHALL exit 0.

#### Scenario: Dry-run on prod
- **WHEN** stdin carries `kprod apply -f x.yaml --dry-run=server`
- **THEN** the exit code is 0

### Requirement: Mutations carry an INTENT
A mutating command without a `# INTENT:` line SHALL produce an `INTENT MISSING` reminder on stderr and a decision with `reasoning: null`.

#### Scenario: Missing INTENT
- **WHEN** stdin carries `kdev scale deploy x --replicas=2`
- **THEN** the exit code is 0 and stderr contains `INTENT MISSING`
