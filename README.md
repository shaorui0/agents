# agents

An SRE oncall triage agent built as a Claude Code skill: an alert goes in, a structured investigation comes out, and every irreversible action stays behind a deterministic gate.

## Quickstart

No cluster, credentials or network needed.

```bash
git clone https://github.com/shaorui0/agents.git && cd agents

# 1. run the tests (Gate 3, audit trail, report verifier)
make test

# 2. see Gate 3 block a production mutation (exit 2, command printed for a human)
echo '{"tool_input":{"command":"kprod scale deploy x --replicas=1 -n y"}}' | bash hooks/k8s_gate.sh; echo "exit=$?"

# 3. check a triage report: ok fixture exits 0, bad fixture exits 2
python3 tools/verify.py fixtures/report_ok.md
python3 tools/verify.py fixtures/report_bad.md
make verify
```

Install the hooks in Claude Code: copy the `hooks` and `permissions` blocks from `.claude/settings.example.json` into your `settings.json`, set `$REPO` to this checkout, and replace the example aliases in `config/env_map.yaml` (`kdev` dev, `kstage` staging, `kprod` prod) with your own. An alias that is not in the map is treated as production. Audit records go to `records/audit/` (override with `AGENTS_AUDIT_DIR`).

## How I think about it

| Question | Answer |
|---|---|
| **What is the binding constraint?** | Context, not the model. Context is scarce RAM, not an infinite disk. The main agent keeps navigation, judgment and command generation; raw data fetching goes to a subagent that returns at most 500 tokens. |
| **What are the primitives?** | Four controls, not roles: Spec (declared end-state), Loop (observe, compare, act, verify), Hook (admission control), Fork (context isolation). See `docs/METHOD.md`. |
| **How does it avoid anchoring on the last deploy?** | Phase lock. In phase A the agent cannot read deploy history, so it cannot confabulate one. A to B needs a non-empty hypothesis with at least one verified. |
| **Where does safety live?** | In deterministic code. The model judges; a hook that returns `exit 2` owns every irreversible action. "It is fine if the model misbehaves." |
| **What stops a bad command?** | Four gates: user approval, `settings.json` allow/deny, the Gate 3 hook (fail-closed alias tiers, hard blocks, PROD plus mutating exits 2), mandatory post-change verification. |
| **How do I know a report is good?** | `tools/verify.py` returns an exit code: required sections, an evidence chain per conclusion, no over-assertion in the Slack reply, INTENT on every mutating command. |
| **Does it get better with use?** | Yes, through delta judgment: matches update an existing file, a new root-cause path creates a case, a new signal updates the routing table. AI-written notes stay `draft` until a human promotes them, and carry `derived_from`. |
| **What is enforced and what is advice?** | `docs/METHOD.md` marks every rule. Gate 3, the audit hooks and `verify.py` are code with tests; the rest is prompt contract. |

### Design stance

**Autonomy is bound to reversibility.** Idempotent expressibility is necessary, undo cost is sufficient. Actions fall into three classes: online undo in seconds, undo that needs an interruption, and no undo. Only the first class may be given to the agent as a command; the third is never given.

**Actuator output is a proposition, not a state change.** The agent outputs "what I think it is and what to do"; a human executes. Production stays read-only for the agent, which is what lets the investigation path be wide open.

**Context is fixed by layer, not slid by time.** Raw metric and log retrieval is pushed to subagents; the main loop receives structured summaries and keeps the judgment.

**Knowledge compounds with every investigation.** The delta is written back to `knowledge/`; the next investigation retrieves first, then acts.

## Repo layout

```
SKILL.md              entry: Layer 0 signal extraction -> route to a type skill
ARCHITECTURE.md       layering and state flow
facets/               abstract surfaces for external interfaces (alert intake, signal extraction, state store, traffic)
skills/               reusable sub-capabilities
  sre-oncall-init             create working dir, extract signals, route
  sre-oncall-quick-check      fast phase: stop the bleeding or locate first
  sre-oncall-query-safety     query safety rules (label filter / step floor / time ceiling)
  sre-oncall-output-format    output contract
  sre-oncall-acceptance-criteria  what counts as a finished investigation
  sre-oncall-compound-learning    write-back after an investigation
  workflow-oncall-spike       two-phase triage for latency spikes
knowledge/            method layer
  patterns/ debug-trees/ checklists/ mitigations/ cards/ references/
hooks/                k8s_gate.sh (Gate 3), audit_pre.sh, audit_log.sh
config/env_map.yaml   example alias -> tier map, hard blocks, verbs (fail-closed default)
tools/                verify.py (report gate), check_rules.py (leak scan, doc shape, commit subjects)
fixtures/             synthetic report_ok.md / report_bad.md
tests/                gate, audit and verifier tests
docs/                 METHOD.md (the model), REQUIREMENTS.md (requirements, data boundary)
openspec/changes/     one change per feature: proposal, specs, tasks, evidence
reports/ notes/blog/  per-change HTML report and blog notes
.claude/              skills/agents-change-loop, settings.example.json
```

## Not published

The full-fidelity incident write-ups (top-level `cases/`, `runbooks/`), runtime tools with audit logs, and investigation records (`records/`) are not published: they contain concrete production details and customer identifiers. `knowledge/cases/` and `knowledge/runbooks/` hold the earlier, already-public sanitized material; a leak scan over it found residual internal identifiers, listed in `openspec/changes/c0001-requirements-and-method/evidence.md` and deliberately left unedited by this work. This repository otherwise ships structure, method, gates and tests. See the data boundary in `docs/REQUIREMENTS.md`.

## Progress

| Change | Date | What | Takeaway | Links |
|---|---|---|---|---|
| c0001-requirements-and-method | 2026-10-24 | Model (METHOD), requirements and data boundary, change-loop skill, leak-scan tool | Label every safety claim enforced or advised; only an exit code is safety | [report](reports/0001-requirements-and-method.html) · [note](notes/blog/0001-requirements-and-method.md) |
| c0002-deterministic-gates | 2026-10-24 | Gate 3 (`k8s_gate`) with fail-closed tiers and hard blocks, audit pre/post pair, settings example, 37 tests | The gate is the one layer the model cannot negotiate with; fail-closed is a default, not a feature | [report](reports/0002-deterministic-gates.html) · [note](notes/blog/0002-deterministic-gates.md) |
| c0003-report-verify | 2026-10-24 | `tools/verify.py` exit-code gate (sections, evidence chain, no over-assertion, INTENT), ok/bad fixtures, README reorganized | A report is only an eval run if "good" is an exit code; reuse the gate's classifier so the two cannot drift | [report](reports/0003-report-verify.html) · [note](notes/blog/0003-report-verify.md) |

## License

MIT, see `LICENSE`. Copyright (c) 2026 Rui Shao.
