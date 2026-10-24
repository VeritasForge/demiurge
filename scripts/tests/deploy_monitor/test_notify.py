"""bin/notify 검증. 가짜 osascript가 받은 argv를 JSON으로 남긴다."""

import json
import tempfile
import unittest
from pathlib import Path

import fakes

NOTIFY = fakes.SKILL_BIN / "notify"

FAKE_OSASCRIPT = """#!/usr/bin/env python3
import json, os, sys
with open(os.environ["ARGV_OUT"], "w") as f:
    json.dump(sys.argv[1:], f)
sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
"""


class NotifyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="deploy-monitor-notify-")
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.out = self.dir / "argv.json"
        fakes.make_fake_bin(self.dir, "osascript", FAKE_OSASCRIPT)

    def notify(self, kind, message, **extra):
        env = fakes.env_with(self.dir, ARGV_OUT=str(self.out), **extra)
        return fakes.run([str(NOTIFY), kind, message], env)

    def argv(self):
        return json.loads(self.out.read_text())

    def script_text(self):
        argv = self.argv()
        return "\n".join(a for i, a in enumerate(argv) if i and argv[i - 1] == "-e")

    def test_start_has_no_sound(self):
        result = self.notify("start", "배포 감시 시작")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("sound name", self.script_text())
        self.assertEqual(self.argv()[-2:], ["배포 감시 시작", "deploy-monitor"])

    def test_anomaly_has_glass_sound(self):
        result = self.notify("anomaly", "이상 감지")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('sound name "Glass"', self.script_text())

    def test_message_with_quotes_passed_verbatim(self):
        message = "AOTA-324 이상: \"x\" \\ 'y'"
        result = self.notify("done", message)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.argv()[-2], message)

    def test_osascript_failure_exit_1(self):
        result = self.notify("auth", "로그인 필요", FAKE_EXIT="1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("NOTIFY_FAILED", result.stderr)

    def test_unknown_kind_exit_2(self):
        result = self.notify("bogus", "x")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
