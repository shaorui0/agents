#!/usr/bin/env python3
"""Self-check for this repository.

Checks:
  1. required files exist
  2. docs/METHOD.md has >= 2 mermaid blocks and the step / failure-mode tables
  3. docs/REQUIREMENTS.md has a data-boundary section
  4. pre-existing public content (knowledge/, facets/, skills/, SKILL.md,
     ARCHITECTURE.md) was not modified or deleted since the base commit
  5. every commit after the base commit has subject
     `c<NNNN>-<slug> [k/n <stage>]: <text>` (merge commits excepted)
  6. leak scan: files ADDED after the base commit must have zero hits.
     Legacy files (already public at the base commit) are scanned and
     reported, never edited. Use --list-legacy to print file:line.

Leak patterns = generic public ones below + private ones from
`.leak_patterns.local` (one regex per line, gitignored, so the repo never
contains the words it guards against).

Exit 0 = pass, 1 = fail.
Usage: python3 tools/check_rules.py [--list-legacy] [repo_root]
"""
import re
import subprocess
import sys
from pathlib import Path

BASE = "9268df3"
REQUIRED = [
    "README.md", "LICENSE", "docs/METHOD.md", "docs/REQUIREMENTS.md",
    ".claude/skills/agents-change-loop/SKILL.md", "tools/check_rules.py",
]
PROTECTED = ["knowledge", "facets", "skills", "SKILL.md", "ARCHITECTURE.md"]
SUBJECT_RE = re.compile(r"^c\d{4}-[a-z0-9-]+ \[\d+/\d+ [a-z+]+\]: \S.*")
PUBLIC_LEAKS = [
    r"(?<![\w.-])\d{12}(?![\w.])",  # 12-digit account id (all-same-digit placeholders allowed)
    r"AKIA[0-9A-Z]{16}",           # AWS access key id
    r"/Users/[A-Za-z0-9_.-]+/",    # local home paths
    r"hooks\.slack\.com/services/", # webhook url
]
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}
TEXT_EXT = {".md", ".py", ".json", ".yaml", ".yml", ".html", ".txt", ".sh", ".toml", ".jsonl", ""}


def git(root, *args):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout


def leak_patterns(root):
    pats = list(PUBLIC_LEAKS)
    local = root / ".leak_patterns.local"
    if local.exists():
        pats += [l.strip() for l in local.read_text().splitlines() if l.strip() and not l.startswith("#")]
    return [re.compile(p, re.IGNORECASE) for p in pats]


def scan_text(text, pats):
    """Return list of 1-based line numbers with a hit (same-char runs ignored)."""
    hits = []
    for p in pats:
        for m in p.finditer(text):
            if len(set(m.group())) > 1:
                hits.append(text.count("\n", 0, m.start()) + 1)
    return sorted(set(hits))


def repo_files(root):
    rc, out = git(root, "ls-files", "--cached", "--others", "--exclude-standard")
    if rc == 0:
        return [root / p for p in out.split("\n") if p]
    return [p for p in root.rglob("*") if p.is_file() and not SKIP_DIRS & set(p.parts)]


def check(root, list_legacy=False):
    errors, info = [], []
    for rel in REQUIRED:
        if not (root / rel).exists():
            errors.append(f"missing required file: {rel}")

    method = root / "docs/METHOD.md"
    if method.exists():
        t = method.read_text()
        n = len(re.findall(r"^```mermaid", t, re.M))
        if n < 2:
            errors.append(f"docs/METHOD.md: {n} mermaid blocks, need >= 2")
        for h in ("## Method as steps", "## Failure modes"):
            if h not in t:
                errors.append(f"docs/METHOD.md: missing section '{h}'")
    req = root / "docs/REQUIREMENTS.md"
    if req.exists() and "Data boundary" not in req.read_text():
        errors.append("docs/REQUIREMENTS.md: missing data boundary section")

    rc, _ = git(root, "rev-parse", "--verify", "-q", BASE)
    legacy = set()
    if rc == 0:
        _, out = git(root, "ls-tree", "-r", "--name-only", BASE)
        legacy = {p for p in out.split("\n") if p}
        _, changed = git(root, "diff", "--name-only", BASE, "--", *PROTECTED)
        for p in changed.split("\n"):
            if p:
                errors.append(f"legacy public file modified since base: {p}")
        _, subjects = git(root, "log", "--no-merges", "--format=%s", f"{BASE}..HEAD")
        for s in subjects.split("\n"):
            if s and not SUBJECT_RE.match(s):
                errors.append(f"commit subject not in c<NNNN>-<slug> [k/n stage]: form: {s[:70]}")

    pats = leak_patterns(root)
    legacy_hits = []
    for f in repo_files(root):
        rel = str(f.relative_to(root))
        if f.suffix not in TEXT_EXT or not f.is_file() or f.name == ".leak_patterns.local":
            continue
        try:
            text = f.read_text()
        except UnicodeDecodeError:
            continue
        lines = scan_text(text, pats)
        for ln in lines:
            if rel in legacy:
                legacy_hits.append(f"{rel}:{ln}")
            else:
                errors.append(f"leak pattern in {rel}:{ln}")
    if legacy_hits:
        files = {h.rsplit(":", 1)[0] for h in legacy_hits}
        info.append(f"legacy leak hits (reported, not modified): {len(legacy_hits)} lines in {len(files)} files")
        if list_legacy:
            info += [f"  LEGACY {h}" for h in legacy_hits]
    return errors, info


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]) if args else Path(__file__).resolve().parent.parent
    errors, info = check(root, "--list-legacy" in sys.argv)
    for i in info:
        print(i)
    for e in errors:
        print(f"FAIL {e}")
    if not errors:
        print("check_rules: OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
