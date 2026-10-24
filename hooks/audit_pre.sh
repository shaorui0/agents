#!/usr/bin/env bash
# PreToolUse: record mutating infra commands (with INTENT) before they run.
# Records go to $AGENTS_AUDIT_DIR (default records/audit/). Always exits 0.
SELF="$(python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "${BASH_SOURCE[0]}")"
exec python3 "$(dirname "$SELF")/audit.py" pre
