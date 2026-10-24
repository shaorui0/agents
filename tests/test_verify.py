import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VERIFY = os.path.join(ROOT, "tools", "verify.py")
OK = os.path.join(ROOT, "fixtures", "report_ok.md")
BAD = os.path.join(ROOT, "fixtures", "report_bad.md")


def run(path, *flags):
    r = subprocess.run([sys.executable, VERIFY, path, *flags], capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout


def run_text(tmp_path, text):
    with open(tmp_path, "w") as f:
        f.write(text)
    return run(tmp_path)


class Fixtures(unittest.TestCase):
    def test_ok_report_exits_0(self):
        rc, out = run(OK)
        self.assertEqual(rc, 0, out)
        self.assertIn("PASS", out)

    def test_bad_report_exits_2_with_every_defect_named(self):
        rc, out = run(BAD)
        self.assertEqual(rc, 2)
        for code in ("[S1]", "[E1]", "[E2]", "[A1]", "[O1]"):
            self.assertIn(code, out)

    def test_json_output(self):
        rc, out = run(BAD, "--json")
        d = json.loads(out)
        self.assertEqual(d["exit"], rc)
        self.assertTrue(any(f["code"] == "A1" for f in d["findings"]))

    def test_unreadable_file_exits_2(self):
        self.assertEqual(run("/nonexistent/report.md")[0], 2)


class Mutations(unittest.TestCase):
    """Edit the ok fixture in one place and check the specific gate reacts."""

    def setUp(self):
        with open(OK) as f:
            self.ok = f.read()
        self.tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"verify_{os.getpid()}.md")

    def tearDown(self):
        if os.path.exists(self.tmp):
            os.unlink(self.tmp)

    def test_missing_timestamp_is_warn_exit_1(self):
        text = self.ok.replace(" at 2026-03-02T10:12Z", "")
        rc, out = run_text(self.tmp, text)
        self.assertEqual(rc, 1, out)
        self.assertIn("[E3]", out)

    def test_dangling_reference_is_fail(self):
        rc, out = run_text(self.tmp, self.ok.replace("[E2] [E3].", "[E7]."))
        self.assertEqual(rc, 2)
        self.assertIn("[E2]", out)

    def test_hedged_root_cause_is_allowed(self):
        text = self.ok.replace("Evidence suggests the p99 spike", "The root cause is likely pool exhaustion; evidence suggests the p99 spike")
        self.assertEqual(run_text(self.tmp, text)[0], 0)

    def test_unhedged_slack_is_fail(self):
        rc, out = run_text(self.tmp, self.ok.replace("Evidence suggests", "It is definitely true"))
        self.assertEqual(rc, 2)
        self.assertIn("definitely", out)

    def test_missing_intent_on_mutating_is_fail(self):
        text = self.ok.replace("# INTENT: preview the pool size change without applying it\n", "")
        # the dry-run command does not mutate, so removing its INTENT is fine
        self.assertEqual(run_text(self.tmp, text)[0], 0)
        text = self.ok.replace("# INTENT: pool pinned at 50/50 with 312 acquire timeouts, restart to clear stuck connections; expect pool in_use to drop below 50\n", "")
        rc, out = run_text(self.tmp, text)
        self.assertEqual(rc, 2)
        self.assertIn("[O1]", out)

    def test_missing_links_section_is_fail(self):
        rc, out = run_text(self.tmp, self.ok.split("## Links")[0])
        self.assertEqual(rc, 2)
        self.assertIn("links", out)

    def test_unknown_alias_does_not_change_intent_check(self):
        text = self.ok.replace("kprod rollout restart", "kmystery rollout restart")
        self.assertEqual(run_text(self.tmp, text)[0], 0)  # INTENT is present; classification does not change that


if __name__ == "__main__":
    unittest.main()
