# 0001 requirements-and-method

- Core idea: label every safety claim "enforced" or "advised". A rule that lives in a prompt is advice; only an exit code is safety. The labelled table made the gaps visible immediately (Gate 1 and Gate 4 are advised only).
- Context is RAM, not disk. Every other design decision (fork, 500-token summary, phase lock) is a consequence of keeping the main agent's window for judgment.
- Counter-intuitive: the leak scanner's first run on the already-public repo found 36 hit lines in 11 files. "Public" did not mean "clean". The scan has to be a gate on new files and a report on old ones, because rewriting published history is a different decision.
- Pitfall: my own test file tripped the leak scan (a fake home path and a fake 12-digit id in literals). Build such strings by concatenation so the repo never contains the pattern it guards against.
- Pitfall: I committed before reading the check output because the pipe to `tail` hid the failing exit code. Gates need `set -o pipefail` or they lie.
- A verb deny-list is fail-open by construction. Say so in the doc, then put a second layer behind it.
