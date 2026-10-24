#!/usr/bin/env bash
# PostToolUse: record the outcome, paired with the pre record by op_id; remind about Gate 4 verification.
# Records go to $AGENTS_AUDIT_DIR (default records/audit/). Always exits 0.
SELF="$(python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "${BASH_SOURCE[0]}")"
exec python3 "$(dirname "$SELF")/audit.py" post
