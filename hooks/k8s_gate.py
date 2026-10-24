#!/usr/bin/env python3
"""Gate 3: classify an infra command and decide allow (exit 0) or block (exit 2).

Hook mode (default): read Claude Code PreToolUse JSON on stdin.
`--classify`       : same input, print the decision as JSON on stdout, always exit 0
                     (used by audit.py; never blocks).

Fail-closed: unreadable config or non-JSON stdin exits 2; an alias that is not in
config/env_map.yaml is treated as production.
"""
import hashlib
import json
import os
import re
import shlex
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
DEFAULT_CONFIG = os.path.join(HERE, "..", "config", "env_map.yaml")
TIERS = ("dev", "staging", "prod")
SEPARATORS = {"&&", "||", ";", "|", "&", "(", ")", "`"}
WRAPPERS = {"sudo", "time", "command", "env", "nohup", "exec"}
SHELLS = {"bash", "sh", "zsh"}


# ---------------------------------------------------------------- config

def _scalar(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        return s[1:-1]
    if s.startswith("[") and s.endswith("]"):
        return [_scalar(x) for x in s[1:-1].split(",") if x.strip()]
    return s


def parse_config(text):
    """Tiny YAML subset: top-level `k: v`, `k: [a, b]`, and indented `- item` lists or `k: v` maps."""
    cfg, cur = {}, None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not raw.startswith(" "):
            key, _, val = line.partition(":")
            key = key.strip()
            if val.strip():
                cfg[key] = _scalar(val)
                cur = None
            else:
                cfg[key] = None
                cur = key
        elif cur is not None:
            body = line.strip()
            if body.startswith("- "):
                if cfg[cur] is None:
                    cfg[cur] = []
                cfg[cur].append(_scalar(body[2:]))
            else:
                if cfg[cur] is None:
                    cfg[cur] = {}
                k, _, v = body.partition(":")
                cfg[cur][k.strip()] = _scalar(v)
    return cfg


def load_config(path=None):
    path = path or os.environ.get("AGENTS_ENV_MAP") or DEFAULT_CONFIG
    with open(path) as f:
        cfg = parse_config(f.read())
    for need in ("aliases", "mutating_verbs", "hard_blocks"):
        if not cfg.get(need):
            raise ValueError(f"config {path}: '{need}' is missing or empty")
    cfg.setdefault("default_tier", "prod")
    return cfg


# ---------------------------------------------------------------- parsing

def split_command(cmd):
    """Return (intent, [segments]) where each segment is a token list.

    Comment lines are dropped (`# INTENT:` is captured). Unquoted &&, ||, ;, |, &, ( ), backtick split segments.
    Raises ValueError on unbalanced quotes.
    """
    intent, segments = None, []
    for line in cmd.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            m = re.match(r"#\s*INTENT:\s*(.*)", stripped)
            if m and intent is None and m.group(1).strip():
                intent = m.group(1).strip()
            continue
        if not stripped:
            continue
        lex = shlex.shlex(line, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        lex.commenters = ""
        cur = []
        for tok in lex:
            if tok in SEPARATORS or re.fullmatch(r"[;&|()]+", tok) and tok not in ("&>",):
                if cur:
                    segments.append(cur)
                cur = []
            else:
                cur.append(tok)
        if cur:
            segments.append(cur)
    return intent, segments


def strip_prefix(tokens):
    """Drop env assignments and wrappers (sudo, time, ...)."""
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", t) or t in WRAPPERS:
            i += 1
        else:
            break
    return tokens[i:]


def first_verb(tokens, cfg):
    """Index and value of the first non-flag token after tokens[0]."""
    vflags = set(cfg.get("value_flags") or [])
    i = 1
    while i < len(tokens):
        t = tokens[i]
        if t.startswith("-"):
            i += 1 if ("=" in t or t not in vflags) else 2
        else:
            return i, t
    return None, None


def is_dry_run(tokens):
    for t in tokens:
        if t == "--dry-run":
            return True
        if t.startswith("--dry-run="):
            return t.split("=", 1)[1].lower() not in ("none", "false")
    return False


def classify_segment(tokens, cfg, depth=0):
    """Classify one segment; returns a list of segment decisions (recursion for bash -c)."""
    tokens = strip_prefix(tokens)
    if not tokens:
        return []
    tool = tokens[0]
    base = os.path.basename(tool)

    if base in SHELLS and "-c" in tokens and depth < 3:
        j = tokens.index("-c")
        if j + 1 < len(tokens):
            return classify_text(tokens[j + 1], cfg, depth + 1)[1]
        return []
    if base == "eval" and depth < 3:
        return classify_text(" ".join(tokens[1:]), cfg, depth + 1)[1]

    aliases = cfg["aliases"]
    tool_prefixes = set(cfg.get("tool_prefixes") or [])
    ignore = set(cfg.get("ignore_commands") or [])
    alias_re = re.compile(cfg.get("alias_regex") or r"^k[a-z0-9]+$")

    if tool in aliases:
        tier, unknown = aliases[tool], False
        if tier not in TIERS:
            tier = "prod"
    elif tool in tool_prefixes:
        tier, unknown = cfg["default_tier"], True
    elif tool not in ignore and alias_re.match(tool):
        tier, unknown = cfg["default_tier"], True
    else:
        return []  # not an infra command
    if tier not in TIERS:
        tier = "prod"

    text = " ".join(tokens)
    hard = next((n for n, rx in cfg["hard_blocks"].items() if re.search(rx, text)), None)

    # kubectl-like (alias or kubectl/helm bare) vs aws
    kind = "aws" if tool == "aws" else ("helm" if tool == "helm" else "kube")
    idx, verb = first_verb(tokens, cfg)
    sub = None
    if kind == "aws":
        # aws <service> <operation>
        rest = [t for t in tokens[1:] if not t.startswith("-")]
        verb = rest[1] if len(rest) > 1 else None
        mutating = bool(verb) and any(verb.startswith(p) for p in cfg.get("aws_mutating_prefixes") or [])
        deleting = bool(verb) and verb.startswith("delete")
    else:
        if verb == "rollout" and idx is not None:
            sub = next((t for t in tokens[idx + 1:] if not t.startswith("-")), None)
            mutating = sub in (cfg.get("rollout_mutating") or [])
            deleting = False
        else:
            mutating = verb in (cfg.get("mutating_verbs") or [])
            deleting = verb in ("delete", "del", "uninstall")
    return [{
        "tool": tool, "tier": tier, "unknown_alias": unknown, "verb": (f"{verb} {sub}" if sub else verb),
        "mutating": mutating or deleting, "delete": deleting, "dry_run": is_dry_run(tokens),
        "hard_block": hard, "text": text,
    }]


def classify_text(cmd, cfg, depth=0):
    try:
        intent, segs = split_command(cmd)
    except ValueError:
        # unparseable: if it even mentions an infra tool, fail closed as an unknown prod mutation
        mentions = re.search(r"\b(kubectl|helm|aws|eksctl|k[a-z0-9]+)\b", cmd)
        if mentions and any(re.search(rf"\b{re.escape(a)}\b", cmd) for a in list(cfg["aliases"]) + ["kubectl", "helm", "aws"]):
            return None, [{"tool": "?", "tier": "prod", "unknown_alias": True, "verb": "unparseable",
                           "mutating": True, "delete": False, "dry_run": False, "hard_block": None, "text": cmd}]
        return None, []
    out = []
    for s in segs:
        out += classify_segment(s, cfg, depth)
    return intent, out


# ---------------------------------------------------------------- decision

def fingerprint(cmd):
    norm = "\n".join(l.strip() for l in cmd.splitlines() if l.strip() and not l.strip().startswith("#"))
    return hashlib.sha1(norm.encode()).hexdigest()[:12]


def decide(cmd, cfg):
    """Return decision dict: action allow|block, reasons[], notes[], plus classification fields."""
    intent, segs = classify_text(cmd, cfg)
    d = {"action": "allow", "infra": bool(segs), "intent": intent, "reasoning": intent,
         "mutating": False, "tier": None, "reasons": [], "notes": [], "hard_block": None,
         "unknown_alias": False, "fingerprint": fingerprint(cmd), "verify_hints": []}
    if not segs:
        return d
    rank = {"dev": 0, "staging": 1, "prod": 2}
    d["tier"] = max((s["tier"] for s in segs), key=rank.get)
    d["unknown_alias"] = any(s["unknown_alias"] for s in segs)
    needs_intent = False
    for s in segs:
        who = f"{s['tool']}"
        if s["hard_block"]:
            d["action"] = "block"
            d["hard_block"] = s["hard_block"]
            d["reasons"].append(f"BLOCKED (hard-block: {s['hard_block']}): not allowed via agent on any tier ({who}). Run it manually.")
            continue
        if not s["mutating"]:
            continue
        if s["dry_run"]:
            d["notes"].append(f"{s['tier'].upper()} ({who}): --dry-run detected, plan only.")
            continue
        d["mutating"] = True
        tier = s["tier"]
        if tier == "prod":
            d["action"] = "block"
            if s["unknown_alias"]:
                d["reasons"].append(f"BLOCKED: unclassified alias ({who}), treated as PROD: mutating op not allowed via agent.")
            else:
                d["reasons"].append(f"BLOCKED: mutating op on PROD ({who}) not allowed via agent.")
            d["reasons"].append("Policy: read-only. Generate the command for a human to run.")
            if s["unknown_alias"]:
                d["reasons"].append("Add the alias to config/env_map.yaml if it should be less restricted.")
        elif tier == "staging":
            if s["delete"]:
                d["action"] = "block"
                d["reasons"].append(f"BLOCKED: delete on STAGING ({who}) not allowed via agent.")
            else:
                d["notes"].append(f"WARNING: mutating op on STAGING ({who}) without --dry-run. Run --dry-run first, then get human approval.")
                needs_intent = True
        else:  # dev
            if s["delete"]:
                d["notes"].append(f"WARNING: delete on DEV ({who}). Confirm the target resource.")
            needs_intent = True
        verb = s["verb"] or ""
        if verb.startswith(("scale", "apply", "create", "patch", "rollout", "set", "replace", "edit", "upgrade", "install", "rollback")):
            d["verify_hints"].append(
                "VERIFY after: helm status <release> && kubectl get pods -n <namespace>" if s["tool"] == "helm" or verb.startswith(("upgrade", "install", "rollback"))
                else "VERIFY after: kubectl rollout status <resource> && kubectl get <resource>")
    if d["mutating"] and not intent:
        d["notes"].append("INTENT MISSING: add '# INTENT: <what you saw, what you conclude, expected effect>' before this command; audit will record reasoning: null.")
    if d["action"] == "block":
        d["notes"] = [n for n in d["notes"] if not n.startswith("VERIFY")]
        d["verify_hints"] = []
    return d


def emit(d, cmd):
    for r in d["reasons"]:
        print(f"[k8s-gate] {r}", file=sys.stderr)
    if d["action"] == "block":
        print("[k8s-gate] Command for a human to run:", file=sys.stderr)
        for line in cmd.splitlines():
            print(f"[k8s-gate] -> {line}", file=sys.stderr)
    for n in d["notes"]:
        print(f"[k8s-gate] {n}", file=sys.stderr)
    for h in d["verify_hints"]:
        print(f"[k8s-gate] {h}", file=sys.stderr)


def read_command(stdin_text):
    data = json.loads(stdin_text)
    if data.get("tool_name") not in (None, "Bash"):
        return None
    return (data.get("tool_input") or {}).get("command") or None


def main(argv):
    classify_only = "--classify" in argv
    try:
        cmd = read_command(sys.stdin.read())
    except (ValueError, AttributeError) as e:
        print(f"[k8s-gate] BLOCKED: cannot parse hook input ({e}); failing closed.", file=sys.stderr)
        return 0 if classify_only else 2
    if not cmd:
        return 0
    try:
        cfg = load_config()
    except (OSError, ValueError) as e:
        print(f"[k8s-gate] BLOCKED: gate config unusable ({e}); failing closed.", file=sys.stderr)
        return 0 if classify_only else 2
    d = decide(cmd, cfg)
    if classify_only:
        print(json.dumps(d))
        return 0
    emit(d, cmd)
    return 2 if d["action"] == "block" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
