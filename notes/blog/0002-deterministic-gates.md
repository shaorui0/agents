# 0002 deterministic-gates

- Core idea: the gate is the one layer the model cannot negotiate with. Everything else (skill text, phase lock) is a request; `exit 2` is a fact. Hallucination stops being a safety risk once every irreversible action passes it.
- Fail-closed is a default, not a feature. An alias that is not in the table is production. The cost is one false block; the alternative is one unreviewed prod change.
- Counter-intuitive: the old substring deny-list missed `kubectl -n y scale` (flag before verb) and fired on arguments that merely contained a verb word. Finding the verb by position after skipping flag values was both stricter and quieter.
- Pitfall: `set image`, `replace`, `edit`, `annotate`, `rollout undo` were not in the original verb list and passed on prod. A deny-list is fail-open by construction; widen it and put audit behind it.
- Pitfall: PostToolUse sees the command but not the pre record. Pairing by command string breaks on repeated commands; pair by fingerprint plus a one-shot inflight marker. There is a test for two identical commands in a row.
- INTENT is a forcing function for the agent, not a security control. Missing INTENT only warns and records `reasoning: null`; the blocking is done by tier policy.
- Hard blocks should beat `--dry-run`. A dry-run flag is something the agent controls.
