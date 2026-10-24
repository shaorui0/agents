# Requirements

## 1. One line

Make the SRE oncall triage skill a public, checkable example of harness engineering: a model of what is protected and from what, plus gates and verifiers that actually run, plus evidence that they do. Oncall triage is the carrier; the thing being demonstrated is controlling a non-deterministic agent on a real system.

## 2. Requirements

| # | Requirement | Why |
|---|---|---|
| R1 | Write the model down: context as scarce RAM, four control primitives (Spec / Loop / Hook / Fork), phase lock, four gates, knowledge compounding. Each rule says whether it is enforced or advised. | Claims that are not marked are indistinguishable from advice |
| R2 | The investigation path is autonomous and read-only; every irreversible action is a proposition handed to a human. | Autonomy is bound to reversibility |
| R3 | Gate 3 is runnable code: alias to tier, hard-block table, mutating-verb detection, `# INTENT:` reminder, fail-closed on unknown aliases, PROD + mutating exits 2 and prints the command. | Safety cannot rest on "the model will comply" |
| R4 | Mutations and their stated reasons are audited, with pre and post records that pair. | Post-mortems need intent next to outcome |
| R5 | A triage report is checkable by exit code: required sections, evidence per conclusion, no over-assertion in the reply, mutating commands carry INTENT. | Every real oncall is an eval run |
| R6 | Gates and verifier have tests that run without any cluster, credentials or network. | Anyone can clone and run |
| R7 | Every change is an OpenSpec change with staged commits, an evidence file with raw command output, an HTML report and a blog note. | Process is part of the deliverable |
| R8 | The repository has zero leak-pattern hits in every file and every commit it publishes; earlier snapshots that contained internal identifiers were replaced by a rebuilt, generalized history (c0004). | A public repo about data boundaries must not contain the data |
| R9 | Public by default: the repo never contains internal identifiers. | See data boundary |

## 3. Deliverables

| ID | Deliverable | Acceptance | Reqs |
|---|---|---|---|
| D1 | `docs/METHOD.md`, `docs/REQUIREMENTS.md` | Two or more mermaid diagrams, step table, failure-mode table; `make check` OK | R1 |
| D2 | `hooks/k8s_gate.sh` + `config/env_map.yaml` + `hooks/audit_pre.sh` + `hooks/audit_log.sh` | `make test` green; PROD scale exits 2 and prints the command | R2 R3 R4 R6 |
| D3 | `tools/verify.py` + `fixtures/report_ok.md` + `fixtures/report_bad.md` | ok fixture exits 0, bad fixture exits 2 | R5 R6 |
| D4 | `.claude/skills/agents-change-loop/SKILL.md`, README Progress table | One row per change | R7 |
| D5 | Leak scan | Every file: 0 hits, no exemptions | R8 R9 |

## 4. Data boundary

These classes of data must never enter this repository, in code, config, fixtures, tests, docs, commit messages or reports:

- real cluster aliases and the table that maps them to environments (config ships only the examples `kdev`, `kstage`, `kprod`);
- internal domains, webhook URLs, workspace names;
- customer or company names, ticket ids, internal repository paths;
- audit logs and investigation records (`records/audit/*.jsonl` is gitignored; fixtures are synthetic);
- credentials, account numbers, local home paths.

Enforcement: `.leak_patterns.local` (gitignored, so the repo never contains the words it guards against) is read by `tools/check_rules.py` together with generic patterns. Every file must have zero hits; there is no exemption by age or origin. History that predated the scan was rebuilt in c0004: identifiers were replaced class-for-class (same original, same replacement, meaning unchanged) and the old history is kept only in a local, never-pushed backup branch.

Reference implementations used while writing the gates were studied for behaviour only; no identifier, table or message text was copied.

## 5. Non-goals

- No live cluster integration, no real alert ingestion.
- No claim that a verb deny-list is complete; it is one layer of four.
- No automatic promotion of knowledge from draft to stable.
