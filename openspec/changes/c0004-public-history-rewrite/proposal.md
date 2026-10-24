## Why

c0001 added a leak scan and found that content already public in this repository (the pre-existing `knowledge/`, `facets/`, `skills/` files) carried internal identifiers: real cluster aliases and cluster names, ticket ids, an internal work-repo path, a local home path and a workspace domain. c0001 reported them and left them alone, because rewriting published history is a separate decision. That decision is now made: a public repo that teaches "fail-closed, data boundary enforced" should not itself contain the data it forbids, and a scan that exempts "legacy" files is an exemption nobody wants to maintain.

## What Changes

- History is rebuilt locally: the pre-existing content, with internal identifiers generalized (class-for-class replacement, same original mapped to the same replacement, meaning unchanged), becomes a single root commit. The 16 process commits from c0001 to c0003 are replayed on top unchanged in content. A local backup branch `pre-public-history` keeps the old history and is never pushed.
- All commits are re-authored with the repository's canonical email.
- `tools/check_rules.py`: the legacy exemption is removed. Every file is scanned; any hit fails. The "legacy files untouched" check is dropped (those files are now ordinary files).
- `docs/REQUIREMENTS.md` R8 and the data-boundary paragraph, and the README, are updated to say the history was rebuilt and identifiers generalized.
- Leak patterns gain two families (cloud-style cluster names, internal ops-directory name).

## Gates and rollback

Local only; push is a human action. Rollback: `git reset --hard pre-public-history` restores the previous history exactly.

## Capabilities

### New Capabilities
- `zero-leak-history`: the whole repository, not just new files, has zero leak-pattern hits.

### Modified Capabilities
- `requirements-doc`: R8 no longer says legacy content is preserved verbatim.

## Impact

Commit hashes of c0001-c0003 change. Anyone holding the old hashes should use the backup branch. Evidence for this change records categories and counts only, never the original identifiers.
