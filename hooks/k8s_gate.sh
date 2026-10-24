#!/usr/bin/env bash
# Gate 3: deterministic PreToolUse hook for infra commands.
#   stdin : Claude Code hook JSON  {"tool_input":{"command":"..."}}
#   exit 0: allow (the normal permission flow still applies)
#   exit 2: block; stderr carries the reason and the command for a human to run
# Config: config/env_map.yaml, or the file named by $AGENTS_ENV_MAP.
SELF="$(python3 -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "${BASH_SOURCE[0]}")"
exec python3 "$(dirname "$SELF")/k8s_gate.py" "$@"
