# c0003 evidence

## 3.1a make test
```
$ make test
python3 -m unittest discover -s tools -p 'test_*.py'
....
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
python3 -W ignore -m unittest discover -s tests -t . -p 'test_*.py'
................................................
----------------------------------------------------------------------
Ran 48 tests in 5.412s

OK
[exit=0]
```

## 3.1b verify tests verbose
```
$ python3 -m unittest tests.test_verify -v
test_bad_report_exits_2_with_every_defect_named (tests.test_verify.Fixtures.test_bad_report_exits_2_with_every_defect_named) ... ok
test_json_output (tests.test_verify.Fixtures.test_json_output) ... ok
test_ok_report_exits_0 (tests.test_verify.Fixtures.test_ok_report_exits_0) ... ok
test_unreadable_file_exits_2 (tests.test_verify.Fixtures.test_unreadable_file_exits_2) ... ok
test_dangling_reference_is_fail (tests.test_verify.Mutations.test_dangling_reference_is_fail) ... ok
test_hedged_root_cause_is_allowed (tests.test_verify.Mutations.test_hedged_root_cause_is_allowed) ... ok
test_missing_intent_on_mutating_is_fail (tests.test_verify.Mutations.test_missing_intent_on_mutating_is_fail) ... ok
test_missing_links_section_is_fail (tests.test_verify.Mutations.test_missing_links_section_is_fail) ... ok
test_missing_timestamp_is_warn_exit_1 (tests.test_verify.Mutations.test_missing_timestamp_is_warn_exit_1) ... ok
test_unhedged_slack_is_fail (tests.test_verify.Mutations.test_unhedged_slack_is_fail) ... ok
test_unknown_alias_does_not_change_intent_check (tests.test_verify.Mutations.test_unknown_alias_does_not_change_intent_check) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.324s

OK
[exit=0]
```

## 3.1c ok fixture (expect exit 0)
```
$ python3 tools/verify.py fixtures/report_ok.md
PASS
[exit=0]
```

## 3.1d bad fixture (expect exit 2)
```
$ python3 tools/verify.py fixtures/report_bad.md
FAIL [S1] missing required section: extracted signals
FAIL [S1] missing required section: links
WARN [E3] E1: no timestamp (use YYYY-MM-DDTHH:MMZ)
WARN [E3] E1: no query or command in backticks
WARN [E3] E2: no timestamp (use YYYY-MM-DDTHH:MMZ)
FAIL [E1] conclusion without evidence reference: "The root cause is the last deploy."
FAIL [E2] E9 cited but not defined in Investigation Log
FAIL [A1] over-assertion in Slack Response: 'definitely'
FAIL [A1] over-assertion in Slack Response: 'clearly'
FAIL [A1] over-assertion in Slack Response: scope 'all users/customers'
FAIL [A1] over-assertion in Slack Response: 'root cause is' without hedge
WARN [A2] Slack Response has no hedging language (consistent with / evidence suggests / unknown)
FAIL [O1] mutating command without '# INTENT:': kprod scale deploy/checkout-api --replicas=1 -n shop
WARN [O2] mutating commands present but section does not say they await approval
FAIL (do not send)
[exit=2]
```

## 3.1e make verify
```
$ make verify
python3 tools/verify.py fixtures/report_ok.md
PASS
FAIL [S1] missing required section: extracted signals
FAIL [S1] missing required section: links
WARN [E3] E1: no timestamp (use YYYY-MM-DDTHH:MMZ)
WARN [E3] E1: no query or command in backticks
WARN [E3] E2: no timestamp (use YYYY-MM-DDTHH:MMZ)
FAIL [E1] conclusion without evidence reference: "The root cause is the last deploy."
FAIL [E2] E9 cited but not defined in Investigation Log
FAIL [A1] over-assertion in Slack Response: 'definitely'
FAIL [A1] over-assertion in Slack Response: 'clearly'
FAIL [A1] over-assertion in Slack Response: scope 'all users/customers'
FAIL [A1] over-assertion in Slack Response: 'root cause is' without hedge
WARN [A2] Slack Response has no hedging language (consistent with / evidence suggests / unknown)
FAIL [O1] mutating command without '# INTENT:': kprod scale deploy/checkout-api --replicas=1 -n shop
WARN [O2] mutating commands present but section does not say they await approval
FAIL (do not send)
[exit=0]
```

## 3.2 check_rules + openspec validate
```
$ python3 tools/check_rules.py; openspec validate c0003-report-verify
legacy leak hits (reported, not modified): 36 lines in 11 files
check_rules: OK
Change 'c0003-report-verify' is valid
[exit=0]
```

## README Quickstart step 2 (copied from README)
```
$ echo '{"tool_input":{"command":"kprod scale deploy x --replicas=1 -n y"}}' | bash hooks/k8s_gate.sh
[k8s-gate] BLOCKED: mutating op on PROD (kprod) not allowed via agent.
[k8s-gate] Policy: read-only. Generate the command for a human to run.
[k8s-gate] Command for a human to run:
[k8s-gate] -> kprod scale deploy x --replicas=1 -n y
[k8s-gate] INTENT MISSING: add '# INTENT: <what you saw, what you conclude, expected effect>' before this command; audit will record reasoning: null.
[exit=2]
```
