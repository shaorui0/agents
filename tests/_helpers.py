import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GATE = os.path.join(ROOT, "hooks", "k8s_gate.sh")
AUDIT_PRE = os.path.join(ROOT, "hooks", "audit_pre.sh")
AUDIT_POST = os.path.join(ROOT, "hooks", "audit_log.sh")


def run_hook(script, payload, env_extra=None):
    """Run a hook script with a hook-protocol payload; return (exit_code, stdout, stderr)."""
    env = dict(os.environ)
    env.update(env_extra or {})
    data = payload if isinstance(payload, str) else json.dumps(payload)
    r = subprocess.run(["bash", script], input=data, capture_output=True, text=True, env=env, cwd=ROOT)
    return r.returncode, r.stdout, r.stderr


def gate(command, env_extra=None):
    return run_hook(GATE, {"tool_name": "Bash", "tool_input": {"command": command}}, env_extra)
