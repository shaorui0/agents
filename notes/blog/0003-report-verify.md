# 0003 report-verify

- Core idea: every real oncall is an eval run, but only if "good" is an exit code. Prompt advice cannot be trended; a pass/warn/fail per report can.
- The verifier imports the gate's classifier instead of keeping its own list of mutating verbs. Two lists drift; one list cannot.
- Counter-intuitive: the best test design was one golden fixture plus one-line edits. Each test names the single check it expects to react, so a red test points at a check, not at a fixture nobody remembers writing.
- Dangling evidence id is a FAIL, missing timestamp is a WARN. The question is whether the conclusion has any support, not whether the support is tidy.
- Pitfall: `grep -c` and exit codes through pipes hid failures in earlier steps. The verifier's own exit code is the contract, so tests call it as a subprocess and assert the integer.
- Pitfall: a Slack-reply word list over-fires on honest hedged sentences ("root cause is likely"). The rule is "root cause is" without a hedge in the same text, not the phrase alone.
- Limit: this checks shape, not truth. A well-formed report can still be wrong. Shape is what a machine can gate; truth is what the red-team and the human gate are for.
