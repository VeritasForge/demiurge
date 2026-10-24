"""bin/awsq 검증. 가짜 aws가 호출 argv를 남기고 상황별 응답을 돌려준다."""

import json
import tempfile
import unittest
from pathlib import Path

import fakes

AWSQ = fakes.SKILL_BIN / "awsq"

FAKE_AWS = """#!/usr/bin/env python3
import json, os, sys
d = os.environ["FAKE_DIR"]
with open(os.path.join(d, "calls.jsonl"), "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\\n")
if os.environ.get("FAKE_STDERR"):
    print(os.environ["FAKE_STDERR"], file=sys.stderr)
    sys.exit(int(os.environ.get("FAKE_EXIT", "255")))
kind, sub = sys.argv[1], sys.argv[2]
if sub == "start-query":
    print(json.dumps({"queryId": "q-1"}))
elif sub == "get-query-results":
    counter = os.path.join(d, "counter")
    n = int(open(counter).read()) if os.path.exists(counter) else 0
    open(counter, "w").write(str(n + 1))
    if n == 0:
        print(json.dumps({"status": "Running", "results": [], "statistics": {}}))
    else:
        print(json.dumps({
            "status": os.environ.get("FAKE_FINAL", "Complete"),
            "results": [[
                {"field": "@timestamp", "value": "2026-10-24 01:00:00"},
                {"field": "msg", "value": "boom"},
                {"field": "@ptr", "value": "ptr-1"},
            ]],
            "statistics": {"bytesScanned": 4096.0},
        }))
elif sub == "get-metric-statistics":
    print(json.dumps({"Label": "m", "Datapoints": [
        {"Timestamp": "2026-10-24T01:10:00+00:00", "Maximum": 3.0, "Average": 1.0},
        {"Timestamp": "2026-10-24T01:00:00+00:00", "Maximum": 7.0, "Average": 2.0},
        {"Timestamp": "2026-10-24T01:05:00+00:00", "Maximum": 5.0, "Average": 1.5},
    ]}))
"""

EXPIRED = "aws: [ERROR]: Your session has expired. Please reauthenticate using 'aws login'."


class AwsqTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="deploy-monitor-awsq-")
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        fakes.make_fake_bin(self.dir, "aws", FAKE_AWS)
        (self.dir / "q.txt").write_text("fields @timestamp, msg | limit 5")

    def awsq(self, args, **extra):
        env = fakes.env_with(
            self.dir, FAKE_DIR=str(self.dir), AWSQ_POLL_SECONDS="0", **extra
        )
        return fakes.run([str(AWSQ), *args], env)

    def logs(self, *groups, **extra):
        args = ["logs", "--region", "ap-northeast-2"]
        for g in groups:
            args += ["--log-group", g]
        args += ["--start", "1790000000", "--end", "1790003600",
                 "--query-file", str(self.dir / "q.txt")]
        return self.awsq(args, **extra)

    def calls(self):
        lines = (self.dir / "calls.jsonl").read_text().splitlines()
        return [json.loads(line) for line in lines]

    def test_logs_complete_returns_rows_without_ptr(self):
        result = self.logs("g1")
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout)
        self.assertEqual(out["status"], "Complete")
        self.assertEqual(
            out["rows"], [{"@timestamp": "2026-10-24 01:00:00", "msg": "boom"}]
        )
        self.assertEqual(out["bytes_scanned"], 4096.0)
        for call in self.calls():
            self.assertIn("--region", call)
            self.assertIn("json", call)

    def test_logs_passes_multiple_log_groups(self):
        result = self.logs("a", "b")
        self.assertEqual(result.returncode, 0, result.stderr)
        start = next(c for c in self.calls() if c[1] == "start-query")
        i = start.index("--log-group-names")
        self.assertEqual(start[i + 1 : i + 3], ["a", "b"])

    def test_logs_failed_status_exit_2(self):
        result = self.logs("g1", FAKE_FINAL="Failed")
        self.assertEqual(result.returncode, 2)
        self.assertIn("AWS_ERROR", result.stderr)

    def test_expired_session_exit_3(self):
        result = self.logs("g1", FAKE_STDERR=EXPIRED, FAKE_EXIT="255")
        self.assertEqual(result.returncode, 3)
        self.assertTrue(result.stderr.startswith("AWS_AUTH_EXPIRED:"), result.stderr)

    def test_other_aws_error_exit_2(self):
        result = self.logs("g1", FAKE_STDERR="AccessDeniedException", FAKE_EXIT="254")
        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.startswith("AWS_ERROR:"), result.stderr)

    def test_metric_datapoints_sorted(self):
        result = self.awsq([
            "metric", "--region", "ap-northeast-2", "--namespace", "AWS/ECS",
            "--metric", "CPUUtilization", "--dimension", "ClusterName=c",
            "--dimension", "ServiceName=s", "--start", "1790000000",
            "--end", "1790003600", "--stat", "Maximum",
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        points = json.loads(result.stdout)["datapoints"]
        self.assertEqual([p["v"] for p in points], [7.0, 5.0, 3.0])
        self.assertEqual(points[0]["t"], 1792803600)
        self.assertEqual(points[1]["t"] - points[0]["t"], 300)
        call = self.calls()[0]
        i = call.index("--dimensions")
        self.assertEqual(call[i + 1 : i + 3], ["ClusterName=c", "ServiceName=s"])


if __name__ == "__main__":
    unittest.main()
