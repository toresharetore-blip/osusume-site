"""稼働率の集計。uptime ブランチの uptime.csv を読む。
使い方: git fetch origin uptime && git show origin/uptime:uptime.csv | python3 tools/uptime_report.py [日数]
"""
import csv
import sys
from datetime import datetime, timedelta, timezone

days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
since = datetime.now(timezone.utc) - timedelta(days=days)
rows = [r for r in csv.DictReader(sys.stdin)
        if datetime.strptime(r["time_utc"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc) >= since]
if not rows:
    print("記録なし")
    sys.exit(0)
ok = sum(r["ok"] == "1" for r in rows)
ms = sorted(int(r["slowest_ms"]) for r in rows)
print(f"過去{days}日: 確認{len(rows)}回 / 正常{ok}回 / 稼働率 {ok / len(rows) * 100:.2f}%")
print(f"応答(4ページのうち最も遅いもの): 中央値 {ms[len(ms) // 2]}ms / 最大 {ms[-1]}ms")
for r in rows:
    if r["ok"] != "1":
        print("  異常:", r["time_utc"], r["status_codes"])
