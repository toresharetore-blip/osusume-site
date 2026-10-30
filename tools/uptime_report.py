"""稼働率の集計。GitHub Actions の uptime ワークフローの実行履歴(成功=正常、失敗=異常)を読む。
使い方: python3 tools/uptime_report.py [日数(既定30)]
"""
import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

REPO = "toresharetore-blip/osusume-site"
days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
since = datetime.now(timezone.utc) - timedelta(days=days)
runs, page = [], 1
while True:
    url = (f"https://api.github.com/repos/{REPO}/actions/workflows/uptime.yml/runs"
           f"?per_page=100&page={page}&created=>={since:%Y-%m-%d}")
    with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})) as r:
        d = json.load(r)
    runs += [x for x in d["workflow_runs"] if x["status"] == "completed"]
    if len(d["workflow_runs"]) < 100:
        break
    page += 1
runs = [x for x in runs if datetime.fromisoformat(x["created_at"].replace("Z", "+00:00")) >= since]
if not runs:
    print("記録なし")
    sys.exit(0)
ok = sum(x["conclusion"] == "success" for x in runs)
print(f"過去{days}日: 確認{len(runs)}回 / 正常{ok}回 / 稼働率 {ok / len(runs) * 100:.2f}%")
for x in runs:
    if x["conclusion"] != "success":
        print("  異常:", x["created_at"], x["conclusion"], x["html_url"])
