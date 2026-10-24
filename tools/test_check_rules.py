import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_rules as cr


class ScanText(unittest.TestCase):
    def test_hit_reports_line(self):
        pats = [re.compile(r"secretword", re.I)]
        self.assertEqual(cr.scan_text("a\nb SecretWord\n", pats), [2])

    def test_same_digit_placeholder_ignored(self):
        pats = [re.compile(p) for p in cr.PUBLIC_LEAKS]
        self.assertEqual(cr.scan_text("acct " + "1" * 12 + " ok", pats), [])
        self.assertEqual(cr.scan_text("acct " + "123456" + "789012" + " bad", pats), [1])

    def test_home_path_flagged(self):
        pats = [re.compile(p) for p in cr.PUBLIC_LEAKS]
        self.assertEqual(cr.scan_text("see /" + "Users" + "/someone/x", pats), [1])

    def test_cluster_name_flagged(self):
        pats = [re.compile(p) for p in cr.PUBLIC_LEAKS]
        self.assertEqual(cr.scan_text("cluster " + "aws-" + "uswest2-prod-a", pats), [1])

    def test_subject_format(self):
        self.assertTrue(cr.SUBJECT_RE.match("c0001-requirements-and-method [3/5 docs]: text"))
        self.assertTrue(cr.SUBJECT_RE.match("c0002-deterministic-gates [4/6 spec+tasks]: text"))
        self.assertFalse(cr.SUBJECT_RE.match("fix stuff"))


if __name__ == "__main__":
    unittest.main()
