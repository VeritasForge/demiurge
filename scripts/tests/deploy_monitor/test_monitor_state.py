"""bin/monitor-state 검증: 회차 창, 정규화, 신규/급증/watch 판정, 요약."""

import json
import os
import tempfile
import unittest
from pathlib import Path

import fakes

MS = str(fakes.SKILL_BIN / "monitor-state")
T0 = 1_800_000_000  # 배포 시각
H = 3600


class MonitorStateCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        self.state = str(self.dir / "state.json")
        self.env = fakes.env_with(self.dir)

    def ms(self, *args):
        return fakes.run([MS, *args], self.env)

    def ok(self, *args):
        r = self.ms(*args)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def init(self, hours=24, step=5, mult="3.0", spike_min=5):
        return self.ok(
            "init", "--state", self.state, "--ticket", "AOTA-1",
            "--deploy-time", str(T0), "--end-time", str(T0 + hours * H),
            "--spike-multiplier", mult, "--spike-min", str(spike_min),
            "--realert-step", str(step),
        )

    def write_json(self, name, data):
        p = self.dir / name
        p.write_text(json.dumps(data, ensure_ascii=False))
        return str(p)

    def baseline(self, counts, hours):
        return self.ok(
            "baseline", "--state", self.state,
            "--counts", self.write_json("base.json", counts), "--hours", str(hours),
        )

    def judge(self, payload, start, end, name="j.json"):
        return self.ms(
            "judge", "--state", self.state,
            "--counts", self.write_json(name, payload),
            "--start", str(start), "--end", str(end),
        )

    def judge_ok(self, payload, start, end):
        r = self.judge(payload, start, end)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def record(self, start, end, status, reason=None):
        args = ["record", "--state", self.state, "--start", str(start),
                "--end", str(end), "--status", status]
        if reason:
            args += ["--reason", reason]
        return self.ok(*args)

    def window(self, now):
        return self.ok("window", "--state", self.state, "--now", str(now))


class TestMonitorState(MonitorStateCase):
    def test_init_refuses_existing_state(self):
        self.init()
        before = Path(self.state).read_text()
        r = self.ms(
            "init", "--state", self.state, "--ticket", "OTHER",
            "--deploy-time", str(T0), "--end-time", str(T0 + H),
            "--spike-multiplier", "3.0", "--spike-min", "5", "--realert-step", "5",
        )
        self.assertEqual(r.returncode, 1)
        self.assertEqual(Path(self.state).read_text(), before)
        bad = self.ms(
            "init", "--state", str(self.dir / "other.json"), "--ticket", "T",
            "--deploy-time", str(T0), "--end-time", str(T0),
            "--spike-multiplier", "3.0", "--spike-min", "5", "--realert-step", "5",
        )
        self.assertEqual(bad.returncode, 2)

    def test_window_starts_at_deploy_time_then_last_ok_end(self):
        self.init()
        w = self.window(T0 + H)
        self.assertEqual((w["start"], w["end"], w["final"]), (T0, T0 + H, False))
        self.record(w["start"], w["end"], "ok")
        w2 = self.window(T0 + 2 * H)
        self.assertEqual(w2["start"], T0 + H)
        self.assertEqual(w2["end"], T0 + 2 * H)

    def test_window_after_failure_covers_gap(self):
        self.init()
        self.record(T0, T0 + H, "ok")
        self.record(T0 + H, T0 + 2 * H, "failed", "aws expired")
        w = self.window(T0 + 3 * H)
        self.assertEqual(w["start"], T0 + H)
        self.assertEqual(w["end"], T0 + 3 * H)
        empty = self.window(T0 + H)
        self.assertTrue(empty["empty"])

    def test_window_final_when_now_past_end(self):
        self.init(hours=2)
        w = self.window(T0 + 5 * H)
        self.assertEqual(w["end"], T0 + 2 * H)
        self.assertTrue(w["final"])

    def test_normalize_masks_ids_and_merges(self):
        self.init()
        out = self.baseline(
            {
                "channel C0BQ7V65QE5 not found": 3,
                "channel C0CB35QMU5U not found": 4,
                "mail a@b.com failed": 1,
                "TIMEOUTERROR": 2,
            },
            7,
        )
        self.assertEqual(out, {"signatures": 3})
        state_text = Path(self.state).read_text()
        for secret in ("C0BQ7V65QE5", "C0CB35QMU5U", "a@b.com"):
            self.assertNotIn(secret, state_text)
        self.assertIn("channel <id> not found", state_text)
        self.assertIn("mail <email> failed", state_text)
        self.assertIn("TIMEOUTERROR", state_text)
        self.assertNotIn("<id>ERROR", state_text)
        r = self.judge_ok(
            {"errors": {"channel C0BQ7V65QE5 not found": 1}, "watch": {}},
            T0, T0 + H,
        )
        self.assertEqual(r["existing"], {"channel <id> not found": 1})
        self.assertNotIn("C0BQ7V65QE5", json.dumps(r))
        os.remove(self.state)
        self.init()
        self.baseline({"user 1234567 failed": 1, "user 12345678 failed": 1}, 7)
        self.assertIn("user <n> failed", Path(self.state).read_text())
        self.assertNotIn("<hex>", Path(self.state).read_text())

    def test_judge_new_spike_existing(self):
        self.init()
        self.baseline({"OSError x": 168}, 168)
        r = self.judge_ok(
            {"errors": {"OSError x": 2, "Brand new": 1}, "watch": {}}, T0, T0 + H
        )
        self.assertEqual(
            r["alerts"],
            [{"kind": "new", "signature": "Brand new", "count": 1, "total": 1}],
        )
        self.assertEqual(r["existing"], {"OSError x": 2})
        r2 = self.judge_ok(
            {"errors": {"OSError x": 6}, "watch": {}}, T0 + H, T0 + 2 * H
        )
        self.assertEqual(
            r2["alerts"],
            [{"kind": "spike", "signature": "OSError x", "count": 6, "total": 6}],
        )

    def test_watch_alerts_on_positive_count(self):
        self.init()
        r = self.judge_ok({"errors": {}, "watch": {"Slack API 호출 실패": 0}}, T0, T0 + H)
        self.assertEqual(r["alerts"], [])
        r2 = self.judge_ok(
            {"errors": {}, "watch": {"Slack API 호출 실패": 2}}, T0 + H, T0 + 2 * H
        )
        self.assertEqual(
            r2["alerts"],
            [{"kind": "watch", "signature": "Slack API 호출 실패", "count": 2, "total": 2}],
        )

    def test_realert_only_after_step(self):
        self.init(step=5)
        alerted = []
        for i in range(6):
            r = self.judge_ok(
                {"errors": {"Brand new": 1}, "watch": {}}, T0 + i * H, T0 + (i + 1) * H
            )
            alerted.append(len(r["alerts"]))
        self.assertEqual(alerted, [1, 0, 0, 0, 0, 1])
        s = self.ok("summary", "--state", self.state)
        self.assertEqual(s["alerts"][0]["total"], 6)

    def test_judge_rejects_already_judged_window(self):
        self.init()
        payload = {"errors": {"Brand new": 1}, "watch": {}}
        self.judge_ok(payload, T0, T0 + H)
        before = Path(self.state).read_text()
        r = self.judge(payload, T0, T0 + H)
        self.assertEqual(r.returncode, 3)
        overlap = self.judge(payload, T0 + H // 2, T0 + 2 * H)
        self.assertEqual(overlap.returncode, 3)
        self.assertEqual(Path(self.state).read_text(), before)
        s = self.ok("summary", "--state", self.state)
        self.assertEqual(s["alerts"][0]["total"], 1)

    def test_summary_reports_failures_and_existing(self):
        self.init()
        self.baseline({"OSError x": 168}, 168)
        self.judge_ok({"errors": {"OSError x": 2}, "watch": {}}, T0, T0 + H)
        self.record(T0, T0 + H, "ok")
        self.record(T0 + H, T0 + 2 * H, "failed", "aws expired")
        s = self.ok("summary", "--state", self.state)
        self.assertEqual(s["ticket"], "AOTA-1")
        self.assertEqual((s["deploy_time"], s["end_time"]), (T0, T0 + 24 * H))
        self.assertEqual(s["covered_until"], T0 + H)
        self.assertEqual(
            s["failures"],
            [{"start": T0 + H, "end": T0 + 2 * H, "reason": "aws expired"}],
        )
        self.assertEqual(s["existing"], {"OSError x": 2})
        self.assertEqual(s["alerts"], [])

    def test_judge_below_spike_min_is_existing(self):
        self.init()
        self.baseline({"OSError x": 168}, 168)
        r = self.judge_ok({"errors": {"OSError x": 4}, "watch": {}}, T0, T0 + H)
        self.assertEqual(r["alerts"], [])
        self.assertEqual(r["existing"], {"OSError x": 4})

    def test_judge_advances_window_without_record(self):
        self.init()
        self.judge_ok({"errors": {}, "watch": {}}, T0, T0 + H)
        w = self.window(T0 + 2 * H)
        self.assertEqual(w["start"], T0 + H)
        self.judge_ok({"errors": {}, "watch": {}}, w["start"], w["end"])
        self.record(T0, T0 + H, "ok")  # 뒤늦은 record 가 되돌리지 않는다
        self.assertEqual(self.window(T0 + 3 * H)["start"], T0 + 2 * H)

    def test_record_accumulates_bytes_scanned(self):
        self.init()
        self.assertEqual(
            self.ok("summary", "--state", self.state)["bytes_scanned_total"], 0.0
        )
        self.ok("record", "--state", self.state, "--start", str(T0),
                "--end", str(T0 + H), "--status", "ok", "--bytes-scanned", "1500.5")
        self.ok("record", "--state", self.state, "--start", str(T0 + H),
                "--end", str(T0 + 2 * H), "--status", "failed",
                "--bytes-scanned", "500")
        self.record(T0 + 2 * H, T0 + 3 * H, "ok")  # 생략하면 더하지 않는다
        s = self.ok("summary", "--state", self.state)
        self.assertEqual(s["bytes_scanned_total"], 2000.5)

    def test_invalid_utf8_error_does_not_echo_input(self):
        self.init()
        p = self.dir / "bad.json"
        p.write_bytes(
            '{"errors": {"mail secret@x.com C0BQ7V65QE5 \ud55c'.encode("utf-8")[:-1]
            + b'": 1}}'
        )
        r = self.ms("judge", "--state", self.state, "--counts", str(p),
                    "--start", str(T0), "--end", str(T0 + H))
        self.assertEqual(r.returncode, 2)
        self.assertIn("STATE_ERROR", r.stderr)
        for secret in ("secret@x.com", "C0BQ7V65QE5"):
            self.assertNotIn(secret, r.stderr)
            self.assertNotIn(secret, r.stdout)


if __name__ == "__main__":
    unittest.main()
