PY ?= python3

.PHONY: test check verify

test:   ## all tests
	$(PY) -m unittest discover -s tools -p 'test_*.py'
	$(PY) -W ignore -m unittest discover -s tests -t . -p 'test_*.py'

check:  ## leak scan, required files, doc shape, commit subjects
	$(PY) tools/check_rules.py

verify: ## the ok fixture must pass (0) and the bad fixture must fail (2)
	$(PY) tools/verify.py fixtures/report_ok.md
	@$(PY) tools/verify.py fixtures/report_bad.md; test $$? -eq 2
