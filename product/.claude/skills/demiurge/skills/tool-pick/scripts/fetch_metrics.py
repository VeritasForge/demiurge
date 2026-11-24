#!/usr/bin/env python3
"""도구 하나의 사용량·유지보수 수치를 공개 API에서 모아 JSON으로 출력한다.

사용 예:
  fetch_metrics.py --github abiosoft/colima --brew colima
  fetch_metrics.py --github astral-sh/uv --pypi uv
  fetch_metrics.py --github spf13/cobra --go github.com/spf13/cobra
  fetch_metrics.py --github colinhacks/zod --npm zod --security

출처 하나가 실패해도 나머지는 계속 조회하고, 실패한 출처에는 {"error": ...}를 남긴다.
인증: GH_TOKEN 또는 GITHUB_TOKEN이 있으면 쓰고, 없으면 `gh auth token`을 시도한다.
둘 다 없으면 인증 없이 호출한다 (GitHub 시간당 60회 제한, 도구 하나에 4회 사용).
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "tool-pick-metrics/1.0"
NOW = dt.datetime.now(dt.timezone.utc)


def _github_token():
    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(key):
            return os.environ[key]
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


GH_TOKEN = _github_token()


def get(url, raw=False, headers=None):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8", "replace")
    return body if raw else json.loads(body)


def gh(path):
    headers = {"Accept": "application/vnd.github+json"}
    if GH_TOKEN:
        headers["Authorization"] = f"Bearer {GH_TOKEN}"
    return get(f"https://api.github.com/{path}", headers=headers)


def days_ago(iso):
    if not iso:
        return None
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return (NOW - t).days


def is_bot(login):
    return login.endswith("[bot]") or login.endswith("-bot")


def fetch_github(repo):
    r = gh(f"repos/{repo}")
    out = {
        "repo": repo,
        "stars": r["stargazers_count"],
        "forks": r["forks_count"],
        "open_issues_and_prs": r["open_issues_count"],
        "archived": r["archived"],
        "license": (r.get("license") or {}).get("spdx_id"),
        "created_at": r["created_at"][:10],
        "pushed_at": r["pushed_at"][:10],
        "days_since_push": days_ago(r["pushed_at"]),
    }

    releases = gh(f"repos/{repo}/releases?per_page=10")
    out["releases_seen"] = len(releases)
    if releases:
        latest = releases[0]
        out["latest_release"] = latest["tag_name"]
        out["latest_release_date"] = (latest.get("published_at") or "")[:10]
        out["days_since_release"] = days_ago(latest.get("published_at"))
        out["recent_release_dates"] = [(x.get("published_at") or "")[:10] for x in releases]

    since = (NOW - dt.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    commits = gh(f"repos/{repo}/commits?since={since}&per_page=100")
    human = [c for c in commits if not is_bot((c.get("author") or {}).get("login", "") or "")]
    out["commits_last_90d"] = f"{len(commits)}+" if len(commits) == 100 else len(commits)
    out["human_commits_last_90d"] = len(human)

    contributors = gh(f"repos/{repo}/contributors?per_page=30")
    people = [c for c in contributors if not is_bot(c["login"]) and c.get("type") != "Bot"]
    total = sum(c["contributions"] for c in people) or 1
    out["top_contributors"] = [
        {"login": c["login"], "commits": c["contributions"]} for c in people[:3]
    ]
    out["top1_share_of_top30_humans"] = round(people[0]["contributions"] / total, 2) if people else None

    # 소스가 비공개인 앱은 GitHub 레포를 이슈 트래커로만 쓴다 → star·커밋 비교가 무의미하다.
    if out["releases_seen"] == 0 and out["days_since_push"] is not None and out["days_since_push"] > 180:
        out["warning"] = "릴리스 0개 + 180일 넘게 push 없음: 이슈 트래커 전용 레포(비공개 소스)일 수 있어 star·커밋 비교에서 제외 검토"
    return out


def fetch_scorecard(repo, security):
    key = urllib.parse.quote(f"github.com/{repo}", safe="")
    d = get(f"https://api.deps.dev/v3/projects/{key}")
    sc = d.get("scorecard")
    if not sc:
        return {"error": "Scorecard 결과 없음 (스캔 대상이 아닌 레포)"}
    wanted = {"Maintained", "Code-Review"}
    if security:
        wanted |= {"Security-Policy", "Signed-Releases"}
    checks = {
        c["name"]: {"score": c["score"], "reason": c["reason"]}
        for c in sc["checks"]
        if c["name"] in wanted
    }
    # 총점은 일부러 내보내지 않는다: 보안 관행 가중치가 커서 유지보수 활발도와 반대로 나올 수 있다.
    return {"scan_date": sc["date"][:10], "checks": checks}


def fetch_brew(name):
    for kind in ("formula", "cask"):
        try:
            d = get(f"https://formulae.brew.sh/api/{kind}/{name}.json")
        except urllib.error.HTTPError:
            # 없는 이름에 404가 아니라 503을 돌려주는 경우가 있어 상태 코드로 구분하지 않는다.
            continue
        inst = d["analytics"]["install"]
        version = d["versions"]["stable"] if kind == "formula" else d.get("version")
        return {
            "kind": kind,
            "version": version,
            "installs_30d": sum(inst["30d"].values()),
            "installs_90d": sum(inst["90d"].values()),
            "installs_365d": sum(inst["365d"].values()),
        }
    return {"error": f"Homebrew에서 formula/cask '{name}'를 찾지 못함 (이름 오류 또는 일시 장애)"}


def fetch_npm(pkg):
    enc = urllib.parse.quote(pkg, safe="@")
    m = get(f"https://api.npmjs.org/downloads/point/last-month/{enc}")
    w = get(f"https://api.npmjs.org/downloads/point/last-week/{enc}")
    return {"downloads_last_week": w["downloads"], "downloads_last_month": m["downloads"], "period_end": m["end"]}


def fetch_pypi(pkg):
    d = get(f"https://pypistats.org/api/packages/{pkg.lower()}/recent")["data"]
    return {"downloads_last_week": d["last_week"], "downloads_last_month": d["last_month"]}


def fetch_crate(name):
    c = get(f"https://crates.io/api/v1/crates/{name}")["crate"]
    return {
        "downloads_total": c["downloads"],
        "downloads_last_90d": c["recent_downloads"],
        "max_version": c["max_version"],
        "updated_at": c["updated_at"][:10],
    }


def fetch_go(module):
    # 공식 API가 없어 pkg.go.dev HTML에서 "Imported by" 수를 읽는다. 페이지 구조가 바뀌면 실패한다.
    html = get(f"https://pkg.go.dev/{module}", raw=True)
    m = re.search(r"Imported by:\s*</span>\s*([\d,]+)", html)
    if not m:
        return {"error": "pkg.go.dev에서 'Imported by' 수를 찾지 못함 (페이지 구조 변경 가능성). GitHub·Scorecard만으로 판정할 것"}
    return {"imported_by": int(m.group(1).replace(",", "")), "note": "다운로드 수가 아니라 이 모듈을 import하는 모듈 수"}


def run(label, fn, *args):
    try:
        return fn(*args)
    except urllib.error.HTTPError as e:
        hint = " (GitHub 비인증 호출 한도 초과 가능성)" if e.code in (403, 429) and "github" in e.url else ""
        return {"error": f"HTTP {e.code} {e.url}{hint}"}
    except Exception as e:  # 출처 하나의 실패가 전체 조회를 멈추지 않게 한다
        return {"error": f"{label}: {type(e).__name__}: {e}"}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--github", help="owner/repo")
    p.add_argument("--brew", help="Homebrew formula 또는 cask 이름")
    p.add_argument("--npm", help="npm 패키지 이름")
    p.add_argument("--pypi", help="PyPI 패키지 이름")
    p.add_argument("--crate", help="crates.io crate 이름")
    p.add_argument("--go", help="Go module 경로 (예: github.com/spf13/cobra)")
    p.add_argument("--security", action="store_true", help="Scorecard 보안 항목(Security-Policy, Signed-Releases)도 포함")
    a = p.parse_args()

    if not any([a.github, a.brew, a.npm, a.pypi, a.crate, a.go]):
        p.error("출처를 하나 이상 지정하세요")

    result = {"fetched_at": NOW.strftime("%Y-%m-%d"), "github_auth": bool(GH_TOKEN)}
    if a.github:
        result["github"] = run("github", fetch_github, a.github)
        result["scorecard"] = run("scorecard", fetch_scorecard, a.github, a.security)
    if a.brew:
        result["homebrew"] = run("homebrew", fetch_brew, a.brew)
    if a.npm:
        result["npm"] = run("npm", fetch_npm, a.npm)
    if a.pypi:
        result["pypi"] = run("pypi", fetch_pypi, a.pypi)
    if a.crate:
        result["crates"] = run("crates", fetch_crate, a.crate)
    if a.go:
        result["go"] = run("go", fetch_go, a.go)

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
