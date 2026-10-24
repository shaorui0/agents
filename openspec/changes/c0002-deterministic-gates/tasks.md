## 1. Gate 3
- [x] 1.1 `config/env_map.yaml` (example aliases, fail-closed default, hard blocks, verbs)
- [x] 1.2 `hooks/k8s_gate.py` + `hooks/k8s_gate.sh`
- [x] 1.3 `tests/test_gate.py`

## 2. Audit
- [x] 2.1 `hooks/audit.py`, `audit_pre.sh`, `audit_log.sh`
- [x] 2.2 `tests/test_audit.py`

## 3. Docs
- [x] 3.1 `.claude/settings.example.json`, METHOD.md corrections

## 4. Acceptance
- [x] 4.1 `make test` green
- [x] 4.2 `echo '{"tool_input":{"command":"kprod scale deploy x --replicas=1 -n y"}}' | bash hooks/k8s_gate.sh` exits 2 and prints the command
- [x] 4.3 `python3 tools/check_rules.py` OK, `openspec validate c0002-deterministic-gates`
- [x] 4.4 evidence.md, report, blog note, README Progress row
