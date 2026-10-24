import glob
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from _helpers import run_hook, AUDIT_PRE, AUDIT_POST  # noqa: E402


def records(d):
    out = []
    for f in sorted(glob.glob(os.path.join(d, "*.jsonl"))):
        with open(f) as fh:
            out += [json.loads(l) for l in fh if l.strip()]
    return out


def payload(cmd, **extra):
    return {"tool_name": "Bash", "session_id": "s1", "cwd": "/tmp/work", "tool_input": {"command": cmd}, **extra}


class AuditTrail(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = {"AGENTS_AUDIT_DIR": self.tmp.name}

    def tearDown(self):
        self.tmp.cleanup()

    def test_pre_and_post_share_op_id_and_intent(self):
        cmd = "# INTENT: OOM seen in logs, scaling down\nkdev scale deploy x --replicas=1"
        self.assertEqual(run_hook(AUDIT_PRE, payload(cmd), self.env)[0], 0)
        rc, _, err = run_hook(AUDIT_POST, payload(cmd, tool_response={"stdout": "scaled", "stderr": ""}), self.env)
        self.assertEqual(rc, 0)
        self.assertIn("Gate 4", err)
        pre, post = records(self.tmp.name)
        self.assertEqual((pre["phase"], post["phase"]), ("pre", "post"))
        self.assertTrue(pre["op_id"])
        self.assertEqual(pre["op_id"], post["op_id"])
        self.assertEqual(pre["reasoning"], "OOM seen in logs, scaling down")
        self.assertTrue(post["verify_required"])
        self.assertEqual(post["stdout"], "scaled")

    def test_missing_intent_is_null_reasoning(self):
        run_hook(AUDIT_PRE, payload("kdev scale deploy x --replicas=1"), self.env)
        (pre,) = records(self.tmp.name)
        self.assertIsNone(pre["reasoning"])

    def test_read_commands_not_logged_pre(self):
        run_hook(AUDIT_PRE, payload("kdev get pods"), self.env)
        self.assertEqual(records(self.tmp.name), [])

    def test_read_command_logged_post_without_verify(self):
        run_hook(AUDIT_POST, payload("kdev get pods", tool_response={"stdout": "ok"}), self.env)
        (post,) = records(self.tmp.name)
        self.assertFalse(post["verify_required"])
        self.assertIsNone(post["op_id"])

    def test_blocked_prod_command_still_audited_pre(self):
        run_hook(AUDIT_PRE, payload("kprod scale deploy x --replicas=1"), self.env)
        (pre,) = records(self.tmp.name)
        self.assertEqual(pre["decision"]["action"], "block")
        self.assertEqual(pre["decision"]["tier"], "prod")

    def test_non_infra_ignored_and_never_blocks(self):
        self.assertEqual(run_hook(AUDIT_PRE, payload("ls -la"), self.env)[0], 0)
        self.assertEqual(run_hook(AUDIT_POST, payload("ls -la"), self.env)[0], 0)
        self.assertEqual(run_hook(AUDIT_PRE, "garbage", self.env)[0], 0)
        self.assertEqual(records(self.tmp.name), [])

    def test_repeated_identical_commands_pair_one_to_one(self):
        cmd = "kdev scale deploy x --replicas=1"
        run_hook(AUDIT_PRE, payload(cmd), self.env)
        run_hook(AUDIT_POST, payload(cmd, tool_response={}), self.env)
        run_hook(AUDIT_PRE, payload(cmd), self.env)
        run_hook(AUDIT_POST, payload(cmd, tool_response={}), self.env)
        recs = records(self.tmp.name)
        ids = [r["op_id"] for r in recs]
        self.assertEqual(ids[0], ids[1])
        self.assertEqual(ids[2], ids[3])
        self.assertNotEqual(ids[0], ids[2])


if __name__ == "__main__":
    unittest.main()
