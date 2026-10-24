## Why

R3 and R4 in `docs/REQUIREMENTS.md`. The method says "safety lives in deterministic code, not in the prompt", but the repository ships no code that can be run. Gate 3 (the PreToolUse hook) is the layer the model cannot route around, and it is the layer a reader has to be able to execute and break. This change generalizes the behaviour of a real production gate into a config-driven one with example aliases only, and adds the audit pair that records INTENT next to the outcome.

## What Changes

- `config/env_map.yaml`: example aliases (`kdev` dev, `kstage` staging, `kprod` prod), `default_tier: prod` (fail-closed), hard-block table, mutating-verb set. No real identifiers.
- `hooks/k8s_gate.sh` + `hooks/k8s_gate.py`: PreToolUse hook. stdin JSON, `exit 0` allow, `exit 2` block with reason and the command printed for a human. Tier policy, hard blocks in every tier, unknown alias treated as prod, `# INTENT:` reminder, `--dry-run` allowed, verify hints, compound-command and `bash -c` handling. `--classify` prints a JSON decision for the audit hooks.
- `hooks/audit_pre.sh`, `hooks/audit_log.sh`, `hooks/audit.py`: JSONL records under `records/audit/` (path via `AGENTS_AUDIT_DIR`), pre and post paired by `op_id`, `reasoning: null` when INTENT is missing.
- `.claude/settings.example.json`: how to register the three hooks (Gate 2 table included as an example).
- `tests/`: unittest suite, no cluster needed.

## Gates and rollback

This change adds the gates themselves. It performs no mutation. Rollback: remove the hook entries from `settings.json`; nothing else depends on them.

## Capabilities

### New Capabilities
- `gate3-k8s-gate`: deterministic tier enforcement for infra commands.
- `audit-trail`: paired pre/post audit records with INTENT.

### Modified Capabilities
(none)

## Impact

Docs: `docs/METHOD.md` corrected where the implementation now does more than described (`bash -c` is parsed one level).
