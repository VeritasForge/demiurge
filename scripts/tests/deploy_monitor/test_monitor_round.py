"""bin/monitor-round 검증: 행 변환, 회차 표시, 완료 요약. 원문이 출력에 새지 않는지 본다."""

import json
import tempfile
import unittest
from pathlib import Path

import fakes

MR = str(fakes.SKILL_BIN / "monitor-round")
MS = str(fakes.SKILL_BIN / "monitor-state")
T0 = 1_800_000_000
H = 3600

SENTENCE = "홍길동님 상담 메시지 전달 실패 환불 문의드립니다"
EMAIL = "secret.user@example.com"
CHANNEL = "C0AB12CD34"

PLAN = {
    "ticket": "SHOP-42",
    "error_level": "ERROR",
    "watch": {"refund_api_fail": "환불 API 호출 실패"},
    "success": {"refund_ok": "환불 처리 완료"},
    "metrics": [{"label": "cpu", "limit": 80}],
    "baseline_bytes": 1_000_000_000,
    "logs_price_per_gb": 0.0076,
}


class MonitorRoundCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.env = fakes.env_with(self.dir)
        self.plan = self.write("plan.json", PLAN)
        self.state = str(self.dir / "state.json")

    def write(self, name, data):
        p = self.dir / name
        p.write_text(json.dumps(data, ensure_ascii=False))
        return str(p)

    def run_ok(self, *args):
        r = fakes.run(list(args), self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def awsq(self, name, rows, scanned=1024.0):
        return self.write(name, {"status": "Complete", "rows": rows,
                                 "bytes_scanned": scanned})

    def convert(self, awsq_path, out="round.counts.json", *extra):
        stdout = self.run_ok(MR, "convert", "--plan", self.plan, "--awsq", awsq_path,
                             "--out", str(self.dir / out), *extra)
        return json.loads(stdout), json.loads((self.dir / out).read_text())

    def cpu(self, values):
        return "cpu=" + self.write(
            "metric.cpu.json", {"datapoints": [{"t": T0 + i, "v": v}
                                               for i, v in enumerate(values)]})

    def start_state(self):
        self.run_ok(MS, "init", "--state", self.state, "--ticket", "SHOP-42",
                    "--deploy-time", str(T0), "--end-time", str(T0 + 4 * H),
                    "--spike-multiplier", "3.0", "--spike-min", "5",
                    "--realert-step", "5")
        base = self.write("base.json", {"post | OSError: [Errno 104] reset": 168})
        self.run_ok(MS, "baseline", "--state", self.state, "--counts", base,
                    "--hours", "168")

    def judge(self, counts_path, start, end, name="judge.json"):
        stdout = self.run_ok(MS, "judge", "--state", self.state, "--counts",
                             counts_path, "--start", str(start), "--end", str(end))
        (self.dir / name).write_text(stdout)
        return str(self.dir / name)

    def show(self, judge_path):
        return self.run_ok(MR, "show", "--judge", judge_path, "--ticket", "SHOP-42")


class TestConvert(MonitorRoundCase):
    def test_classifies_rows_and_metrics(self):
        rows = [
            {"level": "ERROR", "src": "post", "sig": "OSError: [Errno 104] reset", "n": "2"},
            {"level": "ERROR", "src": "refund", "sig": "환불 API 호출 실패 code=500", "n": "1"},
            {"level": "INFO", "src": "refund", "sig": "환불 처리 완료", "n": "7"},
            {"level": "INFO", "src": "x", "sig": "그냥 정보", "n": "9"},
        ]
        info, counts = self.convert(self.awsq("r.json", rows), "round.counts.json",
                                    "--metric", self.cpu([10, 95, 99]))
        self.assertEqual(counts["errors"], {"post | OSError: [Errno 104] reset": 2})
        self.assertEqual(counts["watch"], {"refund_api_fail": 1, "metric:cpu>80": 2})
        self.assertEqual(counts["success"], {"refund_ok": 7})
        self.assertEqual(info["rows"], 4)
        self.assertFalse(info["truncated"])
        self.assertEqual(info["bytes_scanned"], 1024.0)
        self.assertEqual(info["metrics"], {"cpu": {"max": 99, "points": 3, "limit": 80}})

    def test_empty_metric_is_nodata_and_missing_metric_is_error(self):
        _, counts = self.convert(self.awsq("r.json", []), "c.json",
                                 "--metric", self.cpu([]))
        self.assertEqual(counts["watch"], {"nodata:cpu": 1})
        r = fakes.run([MR, "convert", "--plan", self.plan, "--awsq",
                       self.awsq("r2.json", []), "--out", str(self.dir / "c2.json")],
                      self.env)
        self.assertEqual(r.returncode, 2)

    def test_baseline_mode_flat_and_truncation_flag(self):
        rows = [{"level": "ERROR", "src": "a", "sig": f"E{i}", "n": "1"} for i in range(3)]
        info, counts = self.convert(self.awsq("b.json", rows), "b.counts.json",
                                    "--mode", "baseline", "--limit", "3")
        self.assertEqual(counts, {"a | E0": 1, "a | E1": 1, "a | E2": 1})
        self.assertTrue(info["truncated"])

    def test_sentry_issues_become_watch_labels(self):
        sentry = self.write("sentry.json", {"SHOP-API-1A": 4})
        _, counts = self.convert(self.awsq("r.json", []), "c.json",
                                 "--metric", self.cpu([1]), "--sentry", sentry)
        self.assertEqual(counts["watch"], {"sentry:SHOP-API-1A": 4})

    def test_stdout_has_no_message_text(self):
        rows = [{"level": "ERROR", "src": "send", "n": "3",
                 "sig": f"{SENTENCE} {EMAIL} channel={CHANNEL}"}]
        r = fakes.run([MR, "convert", "--plan", self.plan, "--awsq",
                       self.awsq("r.json", rows), "--out", str(self.dir / "c.json"),
                       "--metric", self.cpu([1])], self.env)
        for secret in (SENTENCE, EMAIL, CHANNEL, "홍길동"):
            self.assertNotIn(secret, r.stdout + r.stderr)


class TestShowAndSummary(MonitorRoundCase):
    def leaky_round(self, n, name):
        rows = [
            {"level": "ERROR", "src": "send_to_channel", "n": str(n),
             "sig": f"{SENTENCE} {EMAIL} channel={CHANNEL}"},
            {"level": "ERROR", "src": "relay", "n": "6",
             "sig": f"SlackApiError: {SENTENCE} user=U0QW12ER34"},
            {"level": "ERROR", "src": "post", "n": "1", "sig": "OSError: [Errno 104] reset"},
            {"level": "ERROR", "src": "refund", "n": "1", "sig": "환불 API 호출 실패"},
        ]
        _, _ = self.convert(self.awsq(name, rows), name + ".counts",
                            "--metric", self.cpu([1]))
        return str(self.dir / (name + ".counts"))

    def assert_clean(self, text):
        for secret in (SENTENCE, "홍길동", EMAIL, CHANNEL, "U0QW12ER34", "<email>"):
            self.assertNotIn(secret, text)

    def test_show_never_prints_message_text(self):
        self.start_state()
        out = self.show(self.judge(self.leaky_round(3, "r1"), T0, T0 + H))
        self.assert_clean(out)
        self.assertIn("ALERT new send_to_channel #", out)
        self.assertIn("relay · SlackApiError #", out)
        self.assertIn("ALERT watch refund_api_fail 1건", out)
        self.assertIn("EXISTING 1유형 1건", out)
        banner = [l for l in out.splitlines() if l.startswith("BANNER ")]
        self.assertEqual(len(banner), 1)
        self.assertTrue(banner[0].startswith("BANNER SHOP-42 이상: "))
        self.assert_clean(banner[0])

    def test_same_type_same_name_across_rounds(self):
        self.start_state()
        out1 = self.show(self.judge(self.leaky_round(3, "r1"), T0, T0 + H, "j1.json"))
        out2 = self.show(self.judge(self.leaky_round(9, "r2"), T0 + H, T0 + 2 * H,
                                    "j2.json"))
        name = next(l.split()[2:4] for l in out1.splitlines()
                    if l.startswith("ALERT new send_to_channel"))
        self.assertIn(" ".join(name), out2)

    def test_no_alert_round_prints_no_banner(self):
        self.start_state()
        counts = self.write("c.json", {"errors": {"post | OSError: [Errno 104] reset": 1},
                                       "watch": {}, "success": {}})
        out = self.show(self.judge(counts, T0, T0 + H))
        self.assertNotIn("BANNER", out)
        self.assertIn("EXISTING 1유형 1건", out)

    def test_summary_renders_all_sections(self):
        self.start_state()
        self.judge(self.leaky_round(3, "r1"), T0, T0 + H)
        self.run_ok(MS, "record", "--state", self.state, "--start", str(T0),
                    "--end", str(T0 + H), "--status", "ok",
                    "--bytes-scanned", "500000000")
        self.run_ok(MS, "record", "--state", self.state, "--start", str(T0 + H),
                    "--end", str(T0 + 2 * H), "--status", "failed", "--reason", "auth")
        rounds = self.dir / "rounds.log"
        self.run_ok(MR, "log", "--rounds", str(rounds), "--start", str(T0),
                    "--end", str(T0 + H), "--status", "ok",
                    "--counts", str(self.dir / "r1.counts"))
        self.run_ok(MR, "log", "--rounds", str(rounds), "--start", str(T0 + H),
                    "--end", str(T0 + 2 * H), "--status", "failed")
        summary = self.dir / "summary.json"
        summary.write_text(self.run_ok(MS, "summary", "--state", self.state))
        out = self.run_ok(MR, "summary", "--summary", str(summary), "--plan", self.plan,
                          "--rounds", str(rounds))
        self.assert_clean(out)
        for heading in ("티켓 전용 확인 결과", "이상 알림", "기존 오류", "조회 실패 구간",
                        "총 스캔량"):
            self.assertIn(heading, out)
        self.assertIn("refund_api_fail: 1건", out)
        self.assertIn("refund_ok: 0건", out)
        self.assertIn("send_to_channel #", out)
        self.assertIn("post · OSError #", out)
        self.assertIn("auth (아직 조회 못 함)", out)
        self.assertIn("1.50 GB", out)
        self.assertTrue(out.rstrip().splitlines()[-1].startswith(
            "BANNER SHOP-42 모니터링 완료: 이상 "))

    def test_summary_shows_spike_and_existing_side_by_side(self):
        self.start_state()
        spike = self.write("s.json", {"errors": {"post | OSError: [Errno 104] reset": 9},
                                      "watch": {}, "success": {}})
        calm = self.write("c.json", {"errors": {"post | OSError: [Errno 104] reset": 2},
                                     "watch": {}, "success": {}})
        self.judge(spike, T0, T0 + H, "j1.json")
        self.judge(calm, T0 + H, T0 + 2 * H, "j2.json")
        summary = self.dir / "summary.json"
        summary.write_text(self.run_ok(MS, "summary", "--state", self.state))
        out = self.run_ok(MR, "summary", "--summary", str(summary), "--plan", self.plan)
        self.assertIn("급증 회차 9건 + 평소 수준 회차 2건", out)

    def test_summary_marks_recovered_failure(self):
        self.start_state()
        self.run_ok(MS, "record", "--state", self.state, "--start", str(T0),
                    "--end", str(T0 + H), "--status", "failed", "--reason", "auth")
        empty = self.write("e.json", {"errors": {}, "watch": {}, "success": {}})
        self.judge(empty, T0, T0 + 2 * H)
        summary = self.dir / "summary.json"
        summary.write_text(self.run_ok(MS, "summary", "--state", self.state))
        out = self.run_ok(MR, "summary", "--summary", str(summary), "--plan", self.plan)
        self.assertIn("auth (이후 회차가 다시 조회함)", out)


if __name__ == "__main__":
    unittest.main()
