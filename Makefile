PY ?= python3

.PHONY: test check

test:   ## all tests
	$(PY) -m unittest discover -s tools -p 'test_*.py'

check:  ## leak scan, required files, doc shape, commit subjects
	$(PY) tools/check_rules.py
