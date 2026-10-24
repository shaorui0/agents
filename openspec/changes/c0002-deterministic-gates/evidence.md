# c0002 evidence

## 4.1 make test
```
$ make test
python3 -m unittest discover -s tools -p 'test_*.py'
....
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
python3 -W ignore -m unittest discover -s tests -t . -p 'test_*.py'
.....................................
----------------------------------------------------------------------
Ran 37 tests in 4.836s

OK
[exit=0]
```

## 4.1b gate tests, verbose
```
$ python3 -W ignore -m unittest tests.test_gate -v
test_classify_reports_null_reasoning (tests.test_gate.CompoundAndNonInfra.test_classify_reports_null_reasoning) ... ok
test_compound_strictest_segment_wins (tests.test_gate.CompoundAndNonInfra.test_compound_strictest_segment_wins) ... ok
test_custom_config_changes_tiers (tests.test_gate.CompoundAndNonInfra.test_custom_config_changes_tiers) ... ok
test_env_prefix_and_wrapper (tests.test_gate.CompoundAndNonInfra.test_env_prefix_and_wrapper) ... ok
test_non_bash_tool_ignored (tests.test_gate.CompoundAndNonInfra.test_non_bash_tool_ignored) ... ok
test_non_infra_commands_pass (tests.test_gate.CompoundAndNonInfra.test_non_infra_commands_pass) ... ok
test_shell_indirection_one_level (tests.test_gate.CompoundAndNonInfra.test_shell_indirection_one_level) ... ok
test_bare_kubectl_mutating_blocked (tests.test_gate.FailClosed.test_bare_kubectl_mutating_blocked) ... ok
test_garbage_stdin_exits_2 (tests.test_gate.FailClosed.test_garbage_stdin_exits_2) ... ok
test_missing_config_exits_2 (tests.test_gate.FailClosed.test_missing_config_exits_2) ... ok
test_unbalanced_quotes_on_infra_command_fail_closed (tests.test_gate.FailClosed.test_unbalanced_quotes_on_infra_command_fail_closed) ... ok
test_unknown_alias_mutating_treated_as_prod (tests.test_gate.FailClosed.test_unknown_alias_mutating_treated_as_prod) ... ok
test_unknown_alias_read_passes (tests.test_gate.FailClosed.test_unknown_alias_read_passes) ... ok
test_hard_block_beats_dry_run (tests.test_gate.HardBlocks.test_hard_block_beats_dry_run) ... ok
test_hard_blocks_on_every_tier (tests.test_gate.HardBlocks.test_hard_blocks_on_every_tier) ... ok
test_iam_and_terminate_and_prod_context (tests.test_gate.HardBlocks.test_iam_and_terminate_and_prod_context) ... ok
test_dev_delete_non_hardblock_warns (tests.test_gate.NonProdPolicy.test_dev_delete_non_hardblock_warns) ... ok
test_dev_dry_run_passes_quietly (tests.test_gate.NonProdPolicy.test_dev_dry_run_passes_quietly) ... ok
test_dev_mutating_passes_with_intent_reminder_when_missing (tests.test_gate.NonProdPolicy.test_dev_mutating_passes_with_intent_reminder_when_missing) ... ok
test_dev_mutating_with_intent_has_no_reminder (tests.test_gate.NonProdPolicy.test_dev_mutating_with_intent_has_no_reminder) ... ok
test_dev_read_passes (tests.test_gate.NonProdPolicy.test_dev_read_passes) ... ok
test_staging_scale_passes_with_warning_delete_blocks (tests.test_gate.NonProdPolicy.test_staging_scale_passes_with_warning_delete_blocks) ... ok
test_aws_mutating_blocked_read_passes (tests.test_gate.ProdPolicy.test_aws_mutating_blocked_read_passes) ... ok
test_helm_bare_is_unclassified_so_prod (tests.test_gate.ProdPolicy.test_helm_bare_is_unclassified_so_prod) ... ok
test_intent_line_preserved_in_printed_command (tests.test_gate.ProdPolicy.test_intent_line_preserved_in_printed_command) ... ok
test_prod_dry_run_passes (tests.test_gate.ProdPolicy.test_prod_dry_run_passes) ... ok
test_prod_flags_before_verb_still_blocked (tests.test_gate.ProdPolicy.test_prod_flags_before_verb_still_blocked) ... ok
test_prod_mutating_blocks_and_prints_command (tests.test_gate.ProdPolicy.test_prod_mutating_blocks_and_prints_command) ... ok
test_prod_read_passes (tests.test_gate.ProdPolicy.test_prod_read_passes) ... ok
test_prod_rollout_restart_and_unlisted_looking_verbs (tests.test_gate.ProdPolicy.test_prod_rollout_restart_and_unlisted_looking_verbs) ... ok

----------------------------------------------------------------------
Ran 30 tests in 4.330s

OK
[exit=0]
```

## 4.2 PROD + mutating: exit 2, command printed
```
$ echo '{"tool_input":{"command":"kprod scale deploy x --replicas=1 -n y"}}' | bash hooks/k8s_gate.sh
[k8s-gate] BLOCKED: mutating op on PROD (kprod) not allowed via agent.
[k8s-gate] Policy: read-only. Generate the command for a human to run.
[k8s-gate] Command for a human to run:
[k8s-gate] -> kprod scale deploy x --replicas=1 -n y
[k8s-gate] INTENT MISSING: add '# INTENT: <what you saw, what you conclude, expected effect>' before this command; audit will record reasoning: null.
[exit=2]
```

## 4.2b unknown alias + mutating: treated as PROD
```
$ echo '{"tool_input":{"command":"kmystery scale deploy x --replicas=1"}}' | bash hooks/k8s_gate.sh
[k8s-gate] BLOCKED: unclassified alias (kmystery), treated as PROD: mutating op not allowed via agent.
[k8s-gate] Policy: read-only. Generate the command for a human to run.
[k8s-gate] Add the alias to config/env_map.yaml if it should be less restricted.
[k8s-gate] Command for a human to run:
[k8s-gate] -> kmystery scale deploy x --replicas=1
[k8s-gate] INTENT MISSING: add '# INTENT: <what you saw, what you conclude, expected effect>' before this command; audit will record reasoning: null.
[exit=2]
```

## 4.2c hard block on dev
```
$ echo '{"tool_input":{"command":"kdev delete ns foo"}}' | bash hooks/k8s_gate.sh
[k8s-gate] BLOCKED (hard-block: delete-namespace): not allowed via agent on any tier (kdev). Run it manually.
[k8s-gate] Command for a human to run:
[k8s-gate] -> kdev delete ns foo
[exit=2]
```

## 4.2d DEV read-only passes
```
$ echo '{"tool_input":{"command":"kdev get pods -n x"}}' | bash hooks/k8s_gate.sh
[exit=0]
```

## 4.2e dev mutating without INTENT: reminder, still allowed
```
$ echo '{"tool_input":{"command":"kdev scale deploy x --replicas=2"}}' | bash hooks/k8s_gate.sh
[k8s-gate] INTENT MISSING: add '# INTENT: <what you saw, what you conclude, expected effect>' before this command; audit will record reasoning: null.
[k8s-gate] VERIFY after: kubectl rollout status <resource> && kubectl get <resource>
[exit=0]
```

## 4.2f prod dry-run passes
```
$ echo '{"tool_input":{"command":"kprod apply -f x.yaml --dry-run=server"}}' | bash hooks/k8s_gate.sh
[k8s-gate] PROD (kprod): --dry-run detected, plan only.
[exit=0]
```

## 4.2g audit pair in a temp dir
```
$ D=$(mktemp -d); P="{\"session_id\":\"demo\",\"tool_input\":{\"command\":\"# INTENT: demo scale in dev
kdev scale deploy x --replicas=2\"},\"tool_response\":{\"stdout\":\"scaled\"}}"; echo "$P" | AGENTS_AUDIT_DIR=$D bash hooks/audit_pre.sh; echo "$P" | AGENTS_AUDIT_DIR=$D bash hooks/audit_log.sh; cat $D/*.jsonl
[audit] Gate 4: verify the change now (rollout status / get / helm status). If verification fails or is ambiguous, stop and report.
{"timestamp": "2026-10-23T16:27:05Z", "phase": "pre", "op_id": "f698ae74b281", "session_id": "demo", "cwd": "unknown", "command": "# INTENT: demo scale in dev\nkdev scale deploy x --replicas=2", "fingerprint": "cb3fcce30d94", "reasoning": "demo scale in dev", "decision": {"action": "allow", "tier": "dev", "mutating": true, "hard_block": null, "unknown_alias": false}}
{"timestamp": "2026-10-23T16:27:05Z", "phase": "post", "op_id": "f698ae74b281", "session_id": "demo", "cwd": "unknown", "command": "# INTENT: demo scale in dev\nkdev scale deploy x --replicas=2", "fingerprint": "cb3fcce30d94", "stdout": "scaled", "stderr": "", "verify_required": true}
[exit=0]
```

## 4.3 check_rules + openspec validate
```
$ python3 tools/check_rules.py; openspec validate c0002-deterministic-gates
legacy leak hits (reported, not modified): 36 lines in 11 files
check_rules: OK
Change 'c0002-deterministic-gates' is valid
[exit=0]
```
