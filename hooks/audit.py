#!/usr/bin/env python3
"""Audit trail for infra commands: `audit.py pre` (PreToolUse) and `audit.py post` (PostToolUse).

Records are appended to <audit_dir>/YYYY-MM-DD.jsonl, one JSON object per line.
audit_dir = $AGENTS_AUDIT_DIR, default <repo>/records/audit (gitignored).

pre : only mutating infra commands (including ones Gate 3 will block). Writes
      phase=pre with op_id, INTENT (reasoning, null when missing) and the Gate 3 decision,
      and drops an inflight marker keyed by the command fingerprint.
post: every infra command. Pairs with the pre record through the inflight marker (same op_id),
      stores truncated stdout/stderr, and prints a verification reminder after a mutation (Gate 4).
Never blocks: always exit 0.
"""
import datetime
import json
import os
import sys
import uuid

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import k8s_gate  # noqa: E402


def audit_dir():
    d = os.environ.get("AGENTS_AUDIT_DIR") or os.path.join(HERE, "..", "records", "audit")
    os.makedirs(d, exist_ok=True)
    return d


def write(rec):
    now = datetime.datetime.now(datetime.timezone.utc)
    rec = {"timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"), **rec}
    path = os.path.join(audit_dir(), now.strftime("%Y-%m-%d") + ".jsonl")
    with open(path, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def inflight_path(fp):
    d = os.path.join(audit_dir(), ".inflight")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, fp)


def main(argv):
    phase = argv[0] if argv else ""
    try:
        data = json.loads(sys.stdin.read())
        cmd = (data.get("tool_input") or {}).get("command") or ""
        cfg = k8s_gate.load_config()
    except (ValueError, OSError, AttributeError):
        return 0
    if not cmd:
        return 0
    d = k8s_gate.decide(cmd, cfg)
    if not d["infra"]:
        return 0
    base = {
        "session_id": data.get("session_id", "unknown"),
        "cwd": data.get("cwd", "unknown"),
        "command": cmd,
        "fingerprint": d["fingerprint"],
    }
    decision = {k: d[k] for k in ("action", "tier", "mutating", "hard_block", "unknown_alias")}
    if phase == "pre":
        if not d["mutating"] and not d["hard_block"]:
            return 0
        op_id = uuid.uuid4().hex[:12]
        with open(inflight_path(d["fingerprint"]), "w") as f:
            f.write(op_id)
        write({"phase": "pre", "op_id": op_id, **base, "reasoning": d["reasoning"], "decision": decision})
    elif phase == "post":
        op_id = None
        p = inflight_path(d["fingerprint"])
        if os.path.exists(p):
            with open(p) as f:
                op_id = f.read().strip() or None
            os.unlink(p)
        resp = data.get("tool_response") or {}
        verify_required = bool(d["mutating"] and d["action"] != "block")
        write({"phase": "post", "op_id": op_id, **base,
               "stdout": str(resp.get("stdout", ""))[:500], "stderr": str(resp.get("stderr", ""))[:200],
               "verify_required": verify_required})
        if verify_required:
            print("[audit] Gate 4: verify the change now (rollout status / get / helm status). "
                  "If verification fails or is ambiguous, stop and report.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
