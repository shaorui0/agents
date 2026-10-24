# c0001 evidence

## 3.1a make test
```
$ make test
python3 -m unittest discover -s tools -p 'test_*.py'
....
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
[exit=0]
```

## 3.1b make check (legacy hits listed, not modified)
```
$ python3 tools/check_rules.py --list-legacy
legacy leak hits (reported, not modified): 36 lines in 11 files
  LEGACY SKILL.md:19
  LEGACY SKILL.md:69
  LEGACY SKILL.md:130
  LEGACY knowledge/agent-routing-table.md:24
  LEGACY knowledge/cards/card-admission-webhook-failure-fast-triage.md:39
  LEGACY knowledge/cases/case-debezium-schema-change-snapshot-sign-null.md:9
  LEGACY knowledge/cases/case-debezium-schema-change-snapshot-sign-null.md:82
  LEGACY knowledge/cases/case-spark-job-pending-not-running.md:48
  LEGACY knowledge/cases/case-spark-job-pending-not-running.md:50
  LEGACY knowledge/cases/case-spark-job-pending-not-running.md:86
  LEGACY knowledge/cases/case-spark-job-pending-not-running.md:95
  LEGACY knowledge/cases/case-spark-job-pending-not-running.md:107
  LEGACY knowledge/cases/case-spark-job-pending-not-running.md:114
  LEGACY knowledge/cases/case-spark-job-pending-not-running.md:125
  LEGACY knowledge/cases/case-spark-job-pending-not-running.md:132
  LEGACY knowledge/cases/case-starrocks-fe-crashloop-bdb-ip-binding.md:9
  LEGACY knowledge/runbooks/runbook-debezium-cdc-connector-troubleshooting.md:9
  LEGACY knowledge/runbooks/runbook-jenkins-selenium-dns-failures.md:27
  LEGACY knowledge/runbooks/runbook-jenkins-selenium-dns-failures.md:28
  LEGACY knowledge/runbooks/runbook-jenkins-selenium-dns-failures.md:29
  LEGACY knowledge/runbooks/runbook-jenkins-selenium-dns-failures.md:45
  LEGACY knowledge/runbooks/runbook-jenkins-selenium-dns-failures.md:49
  LEGACY knowledge/runbooks/runbook-jenkins-selenium-dns-failures.md:54
  LEGACY knowledge/runbooks/runbook-jenkins-selenium-dns-failures.md:61
  LEGACY knowledge/runbooks/runbook-jenkins-selenium-dns-failures.md:62
  LEGACY knowledge/runbooks/runbook-jenkins-selenium-dns-failures.md:64
  LEGACY knowledge/runbooks/runbook-site-outage-access-troubleshooting.md:28
  LEGACY knowledge/runbooks/runbook-site-outage-access-troubleshooting.md:29
  LEGACY skills/sre-oncall-init/phase_lock.md:12
  LEGACY skills/sre-oncall-output-format/SKILL.md:10
  LEGACY skills/sre-oncall-output-format/SKILL.md:16
  LEGACY skills/sre-oncall-output-format/SKILL.md:19
  LEGACY skills/sre-oncall-output-format/SKILL.md:24
  LEGACY skills/sre-oncall-output-format/SKILL.md:50
  LEGACY skills/sre-oncall-output-format/SKILL.md:168
  LEGACY skills/sre-oncall-output-format/SKILL.md:211
check_rules: OK
[exit=0]
```

## 3.1c mermaid blocks in METHOD.md
```
$ grep -c '^```mermaid' docs/METHOD.md
2
[exit=0]
```

## 3.2 openspec validate
```
$ openspec validate c0001-requirements-and-method
Change 'c0001-requirements-and-method' is valid
[exit=0]
```

## commit subjects since base
```
$ git log --no-merges --format=%s 9268df3..HEAD
c0001-requirements-and-method [4/5 impl]: check_rules (leak scan, doc shape, legacy-untouched, commit subjects), make test/check
c0001-requirements-and-method [3/5 docs]: METHOD (two diagrams, step and failure tables), REQUIREMENTS with data boundary, change-loop skill, MIT license
c0001-requirements-and-method [2/5 spec+tasks]: contracts for requirements and method docs, acceptance tasks
c0001-requirements-and-method [1/5 proposal]: why the model and requirements come before any code
[exit=0]
```
