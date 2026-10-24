## 1. Rewrite
- [x] 1.1 backup branch `pre-public-history`; local identity set to the canonical email
- [x] 1.2 generalize identifiers in the pre-existing files; commit as single root
- [x] 1.3 replay the 16 process commits on the new root; re-author all commits

## 2. Tooling
- [x] 2.1 `tools/check_rules.py`: remove legacy exemption; root commit is the base for subject checks
- [x] 2.2 leak patterns: cluster-name and ops-directory families

## 3. Docs
- [x] 3.1 README and `docs/REQUIREMENTS.md` (R8, data boundary) describe the rebuilt history

## 4. Acceptance
- [x] 4.1 before: old tree scan shows N hit lines in M files; after: 0
- [x] 4.2 one author email; commit count; `make test` green; `git status` clean
- [x] 4.3 `check_rules` OK, `openspec validate c0004-public-history-rewrite`
- [x] 4.4 evidence.md (categories and counts only), report, blog note, Progress row
