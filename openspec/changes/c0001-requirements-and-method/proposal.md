## Why

The repository publishes the structure of an SRE oncall triage skill (facets, skills, knowledge layout) but not the reasoning behind it, and nothing in it can be run or checked. A reader cannot tell which claims are enforced and which are advice. Before adding any code, write down the model (what is being protected and from what) and the requirements, so every later change can be traced to a named requirement.

## What Changes

- `docs/REQUIREMENTS.md`: requirements R1-R9, deliverables D1-D5, and the data-boundary constraints that govern what may ever enter this public repo.
- `docs/METHOD.md`: the model. Context as scarce RAM, four control primitives, the phase-lock state machine, the four gates, knowledge compounding, an executable step table, and a failure-mode table.
- `.claude/skills/agents-change-loop/SKILL.md`: the per-change loop (OpenSpec change, staged commits, evidence, HTML report, blog note).
- `tools/check_rules.py` + `make check`: leak scan (new files must have zero hits; legacy files are listed, never edited), required-file check, mermaid count, commit-subject format.
- `LICENSE` (MIT), `.gitignore` entry for `.leak_patterns.local`.

## Capabilities

### New Capabilities
- `requirements-doc`: requirements and data boundary are written down and checkable.
- `method-doc`: the method document has the required diagrams and tables.

### Modified Capabilities
(none)

## Impact

No behaviour change. Existing `knowledge/`, `facets/`, `skills/` are untouched. The leak scan over legacy files is read-only reporting.
