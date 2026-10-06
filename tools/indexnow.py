"""公開後に、Bingなど IndexNow 対応の検索エンジンへ「ページが更新された」と知らせる。"""
import json, pathlib, re, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent.parent
key = (ROOT / "tools/indexnow_key.txt").read_text().strip()
host = "osusume-site.toresharetore.workers.dev"
urls = re.findall(r"<loc>(.*?)</loc>", (ROOT / "public/sitemap.xml").read_text(encoding="utf-8"))
data = json.dumps({"host": host, "key": key, "keyLocation": f"https://{host}/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=data, headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print("IndexNow:", r.status, len(urls), "URLs")
except Exception as e:
    print("IndexNow failed:", e)
