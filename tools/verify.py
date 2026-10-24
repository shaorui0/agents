#!/usr/bin/env python3
"""Structure gate for a triage report.md.

    python3 tools/verify.py report.md [--json]

Checks (code in brackets is what the output prints):
  S1  required sections present
  E1  every conclusion cites at least one [E<n>]
  E2  every cited id is defined in the Investigation Log
  E3  evidence has a timestamp and a query/command in backticks (warning)
  A1  Slack Response has no over-assertion words
  A2  Slack Response contains hedging language (warning)
  O1  every mutating command in Operation Commands has a `# INTENT:` line
      (mutating is decided by hooks/k8s_gate.py, so the two never drift)
  O2  Operation Commands mentions approval when it holds mutating commands (warning)

Exit codes: 0 PASS, 1 WARN (review before sending), 2 FAIL (do not send).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hooks"))
import k8s_gate  # noqa: E402

REQUIRED = {
    "investigation plan": ["investigation plan"],
    "extracted signals": ["extracted signals"],
    "investigation log": ["investigation log"],
    "conclusions": ["conclusions"],
    "slack response": ["slack response"],
    "operation commands": ["operation commands"],
    "links": ["links"],
}
ASSERTIONS = [
    (r"\bdefinitely\b", "'definitely'"),
    (r"\bcertainly\b", "'certainly'"),
    (r"\bclearly\b", "'clearly'"),
    (r"\bobviously\b", "'obviously'"),
    (r"\bwithout (a )?doubt\b", "'without doubt'"),
    (r"\b100%", "'100%'"),
    (r"\bguaranteed?\b", "'guarantee'"),
    (r"\ball (users|customers)\b", "scope 'all users/customers'"),
    (r"\beveryone\b", "scope 'everyone'"),
    (r"\bconfirmed that\b", "'confirmed that'"),
    (r"\broot cause is\b(?!.*\b(?:likely|possibly|probably|consistent)\b)", "'root cause is' without hedge"),
]
HEDGES = re.compile(r"\b(consistent with|evidence suggests|likely|possibly|probably|unknown|may be)\b", re.I)
TS = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
EVID_DEF = re.compile(r"^\s*(?:[-*]\s*)?\**(E\d+)\**\s*[:.)]\s*(.*)$")
EVID_REF = re.compile(r"\[(E\d+)\]")
ITEM = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+(.*)$")


def parse_sections(text):
    """heading (lowercased) -> body text, for #, ## and ### headings."""
    sections, cur, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.+?)\s*$", line)
        if m:
            if cur is not None:
                sections[cur] = "\n".join(buf)
            cur, buf = m.group(1).strip().lower(), []
        else:
            buf.append(line)
    if cur is not None:
        sections[cur] = "\n".join(buf)
    return sections


def find(sections, key):
    for alias in REQUIRED[key]:
        for h, body in sections.items():
            if h == alias or h.startswith(alias):
                return body
    return None


def code_blocks(body):
    return re.findall(r"```[a-zA-Z]*\n(.*?)```", body, re.S)


def command_units(block):
    """Split a code block into units separated by blank lines; an INTENT line stays with its command."""
    units, cur = [], []
    for line in block.splitlines():
        if not line.strip():
            if cur:
                units.append("\n".join(cur))
            cur = []
        else:
            cur.append(line)
    if cur:
        units.append("\n".join(cur))
    return units


def verify(text):
    findings = []  # (level, code, message)

    def add(level, code, msg):
        findings.append((level, code, msg))

    sections = parse_sections(text)
    for key in REQUIRED:
        if find(sections, key) is None:
            add("FAIL", "S1", f"missing required section: {key}")

    log = find(sections, "investigation log") or ""
    defined = {}
    for line in log.splitlines():
        m = EVID_DEF.match(line)
        if m:
            defined[m.group(1)] = m.group(2)
    for eid, body in defined.items():
        if not TS.search(body):
            add("WARN", "E3", f"{eid}: no timestamp (use YYYY-MM-DDTHH:MMZ)")
        if "`" not in body:
            add("WARN", "E3", f"{eid}: no query or command in backticks")

    concl = find(sections, "conclusions")
    if concl is not None:
        items = [m.group(1) for m in (ITEM.match(l) for l in concl.splitlines()) if m]
        if not items:
            add("FAIL", "E1", "Conclusions has no list items")
        for it in items:
            refs = EVID_REF.findall(it)
            if not refs:
                add("FAIL", "E1", f"conclusion without evidence reference: \"{it[:70]}\"")
            for r in refs:
                if r not in defined:
                    add("FAIL", "E2", f"{r} cited but not defined in Investigation Log")

    slack = find(sections, "slack response")
    if slack is not None:
        for rx, label in ASSERTIONS:
            if re.search(rx, slack, re.I):
                add("FAIL", "A1", f"over-assertion in Slack Response: {label}")
        if slack.strip() and not HEDGES.search(slack):
            add("WARN", "A2", "Slack Response has no hedging language (consistent with / evidence suggests / unknown)")

    ops = find(sections, "operation commands")
    if ops is not None:
        try:
            cfg = k8s_gate.load_config()
        except (OSError, ValueError) as e:
            cfg = None
            add("FAIL", "O1", f"cannot load gate config to classify commands: {e}")
        any_mut = False
        for block in code_blocks(ops):
            for unit in command_units(block):
                if cfg is None:
                    break
                d = k8s_gate.decide(unit, cfg)
                if d["mutating"]:
                    any_mut = True
                    if not d["intent"]:
                        first = next((l for l in unit.splitlines() if not l.startswith("#")), unit)
                        add("FAIL", "O1", f"mutating command without '# INTENT:': {first[:70]}")
        if any_mut and not re.search(r"\b(approv|await)", ops, re.I):
            add("WARN", "O2", "mutating commands present but section does not say they await approval")
    return findings


def exit_code(findings):
    levels = {f[0] for f in findings}
    return 2 if "FAIL" in levels else (1 if "WARN" in levels else 0)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(args[0]) as f:
            text = f.read()
    except OSError as e:
        print(f"FAIL cannot read {args[0]}: {e}", file=sys.stderr)
        return 2
    findings = verify(text)
    code = exit_code(findings)
    if "--json" in argv:
        print(json.dumps({"exit": code, "findings": [{"level": l, "code": c, "message": m} for l, c, m in findings]}))
    else:
        for l, c, m in findings:
            print(f"{l} [{c}] {m}")
        print({0: "PASS", 1: "WARN (review before sending)", 2: "FAIL (do not send)"}[code])
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
