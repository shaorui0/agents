## Why

R5 in `docs/REQUIREMENTS.md`: every real oncall is an eval run. "Evidence-backed" and "no over-assertion" are prompt advice until something returns a non-zero exit code on a report that violates them. Without that, nothing tells you whether the skill is decaying, and Slack replies can say "definitely" with no evidence chain behind them.

## What Changes

- `tools/verify.py`: structure gate for a triage `report.md`. Required sections, every conclusion cites evidence ids that exist in the investigation log, evidence carries a timestamp and a query or command, the Slack reply has no over-assertion words, and every mutating command in the operation section has a `# INTENT:` line (decided by the Gate 3 classifier, so the two cannot drift apart). Exit 0 PASS, 1 WARN, 2 FAIL; `--json`.
- `fixtures/report_ok.md`, `fixtures/report_bad.md`: synthetic reports (no real systems).
- `tests/test_verify.py`.
- README reorganized: one-liner, Quickstart, How I think, layout, Progress, License. All original facts kept.

## Gates and rollback

Read-only tool; nothing mutates. Rollback: delete `tools/verify.py`.

## Capabilities

### New Capabilities
- `report-verify`: exit-code gate on a triage report.

### Modified Capabilities
(none)

## Impact

`make verify` runs both fixtures and expects 0 and 2.
