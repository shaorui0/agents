import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from _helpers import gate, run_hook, GATE, ROOT  # noqa: E402


class ProdPolicy(unittest.TestCase):
    def test_prod_mutating_blocks_and_prints_command(self):
        cmd = "kprod scale deploy x --replicas=1 -n y"
        rc, _, err = gate(cmd)
        self.assertEqual(rc, 2)
        self.assertIn(cmd, err)
        self.assertIn("BLOCKED", err)

    def test_prod_read_passes(self):
        for c in ("kprod get pods -n y", "kprod logs deploy/x --tail=50", "kprod rollout status deploy/x",
                  "kprod describe pod p"):
            self.assertEqual(gate(c)[0], 0, c)

    def test_prod_flags_before_verb_still_blocked(self):
        self.assertEqual(gate("kprod -n y scale deploy x --replicas=1")[0], 2)
        self.assertEqual(gate("kprod --context=foo -n y rollout restart deploy/x")[0], 2)

    def test_prod_rollout_restart_and_unlisted_looking_verbs(self):
        for c in ("kprod rollout restart deploy/x", "kprod set image deploy/x c=img:1", "kprod replace -f x.yaml",
                  "kprod label pod p a=b", "kprod exec -it p -- sh"):
            self.assertEqual(gate(c)[0], 2, c)

    def test_prod_dry_run_passes(self):
        self.assertEqual(gate("kprod apply -f x.yaml --dry-run=server")[0], 0)
        self.assertEqual(gate("kprod apply -f x.yaml --dry-run")[0], 0)
        self.assertEqual(gate("kprod apply -f x.yaml --dry-run=none")[0], 2)

    def test_intent_line_preserved_in_printed_command(self):
        cmd = "# INTENT: pods crashlooping, OOM in logs, scale down\nkprod scale deploy x --replicas=1 -n y"
        rc, _, err = gate(cmd)
        self.assertEqual(rc, 2)
        self.assertIn("-> # INTENT: pods crashlooping", err)
        self.assertNotIn("INTENT MISSING", err)

    def test_helm_bare_is_unclassified_so_prod(self):
        self.assertEqual(gate("helm upgrade r ./chart")[0], 2)
        self.assertEqual(gate("helm status r")[0], 0)
        self.assertEqual(gate("helm upgrade r ./chart --dry-run")[0], 0)

    def test_aws_mutating_blocked_read_passes(self):
        self.assertEqual(gate("aws s3 rm s3://b/k")[0], 2)
        self.assertEqual(gate("aws ec2 describe-instances")[0], 0)


class FailClosed(unittest.TestCase):
    def test_unknown_alias_mutating_treated_as_prod(self):
        rc, _, err = gate("kmystery scale deploy x --replicas=1")
        self.assertEqual(rc, 2)
        self.assertIn("unclassified alias", err)
        self.assertIn("kmystery scale deploy x", err)

    def test_unknown_alias_read_passes(self):
        self.assertEqual(gate("kmystery get pods")[0], 0)

    def test_bare_kubectl_mutating_blocked(self):
        self.assertEqual(gate("kubectl delete pod p")[0], 2)

    def test_missing_config_exits_2(self):
        rc, _, err = gate("kdev get pods", {"AGENTS_ENV_MAP": "/nonexistent/env_map.yaml"})
        self.assertEqual(rc, 2)
        self.assertIn("failing closed", err)

    def test_garbage_stdin_exits_2(self):
        rc, _, err = run_hook(GATE, "not json")
        self.assertEqual(rc, 2)

    def test_unbalanced_quotes_on_infra_command_fail_closed(self):
        self.assertEqual(gate("kdev get pods -l 'a=b")[0], 2)


class HardBlocks(unittest.TestCase):
    def test_hard_blocks_on_every_tier(self):
        for alias in ("kdev", "kstage", "kprod", "kmystery"):
            for c in (f"{alias} delete ns foo", f"{alias} delete namespace foo",
                      f"{alias} delete pv vol-1", f"{alias} delete pods --all -n x",
                      f"{alias} delete deploy x -A", f"{alias} delete pods --all-namespaces"):
                rc, _, err = gate(c)
                self.assertEqual(rc, 2, c)
                self.assertIn("hard-block", err, c)

    def test_hard_block_beats_dry_run(self):
        self.assertEqual(gate("kdev delete ns foo --dry-run=client")[0], 2)

    def test_iam_and_terminate_and_prod_context(self):
        self.assertEqual(gate("aws iam create-user --user-name u")[0], 2)
        self.assertEqual(gate("aws ec2 terminate-instances --instance-ids i-1")[0], 2)
        self.assertEqual(gate("kdev get pods --context prod")[0], 2)


class NonProdPolicy(unittest.TestCase):
    def test_dev_read_passes(self):
        rc, _, err = gate("kdev get pods -n x")
        self.assertEqual(rc, 0)
        self.assertNotIn("BLOCKED", err)

    def test_dev_mutating_passes_with_intent_reminder_when_missing(self):
        rc, _, err = gate("kdev scale deploy x --replicas=2 -n y")
        self.assertEqual(rc, 0)
        self.assertIn("INTENT MISSING", err)
        self.assertIn("VERIFY after", err)

    def test_dev_mutating_with_intent_has_no_reminder(self):
        rc, _, err = gate("# INTENT: test load, scale up in dev\nkdev scale deploy x --replicas=2")
        self.assertEqual(rc, 0)
        self.assertNotIn("INTENT MISSING", err)

    def test_dev_dry_run_passes_quietly(self):
        rc, _, err = gate("kdev apply -f x.yaml --dry-run=client")
        self.assertEqual(rc, 0)
        self.assertNotIn("INTENT MISSING", err)

    def test_dev_delete_non_hardblock_warns(self):
        rc, _, err = gate("kdev delete pod p -n x")
        self.assertEqual(rc, 0)
        self.assertIn("WARNING: delete on DEV", err)

    def test_staging_scale_passes_with_warning_delete_blocks(self):
        rc, _, err = gate("kstage scale deploy x --replicas=2")
        self.assertEqual(rc, 0)
        self.assertIn("STAGING", err)
        self.assertEqual(gate("kstage delete pod p")[0], 2)


class CompoundAndNonInfra(unittest.TestCase):
    def test_non_infra_commands_pass(self):
        for c in ("ls -la", "git status", "kill -9 123", "grep scale file.txt", "echo kprod scale x"):
            self.assertEqual(gate(c)[0], 0, c)

    def test_compound_strictest_segment_wins(self):
        self.assertEqual(gate("kdev get pods && kprod scale deploy x --replicas=1")[0], 2)
        self.assertEqual(gate("kdev get pods | grep x; kprod delete pod p")[0], 2)
        self.assertEqual(gate("kprod get pods | grep scale")[0], 0)

    def test_env_prefix_and_wrapper(self):
        self.assertEqual(gate("FOO=1 kprod scale deploy x --replicas=1")[0], 2)
        self.assertEqual(gate("sudo kprod scale deploy x --replicas=1")[0], 2)

    def test_shell_indirection_one_level(self):
        self.assertEqual(gate('bash -c "kprod delete pod x"')[0], 2)
        self.assertEqual(gate('eval "kprod scale deploy x --replicas=1"')[0], 2)

    def test_non_bash_tool_ignored(self):
        rc, _, _ = run_hook(GATE, {"tool_name": "Read", "tool_input": {"command": "kprod scale x"}})
        self.assertEqual(rc, 0)

    def test_classify_reports_null_reasoning(self):
        import json
        import subprocess
        r = subprocess.run([sys.executable, os.path.join(ROOT, "hooks", "k8s_gate.py"), "--classify"],
                           input=json.dumps({"tool_input": {"command": "kdev scale deploy x --replicas=2"}}),
                           capture_output=True, text=True)
        d = json.loads(r.stdout)
        self.assertEqual((d["tier"], d["mutating"], d["reasoning"]), ("dev", True, None))

    def test_custom_config_changes_tiers(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            with open(os.path.join(ROOT, "config", "env_map.yaml")) as src:
                f.write(src.read().replace("kdev: dev", "kdev: prod"))
        try:
            self.assertEqual(gate("kdev scale deploy x --replicas=2", {"AGENTS_ENV_MAP": f.name})[0], 2)
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
