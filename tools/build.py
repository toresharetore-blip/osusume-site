"""content/*.html(本文)から public/*.html を作る。
本文の1行目は JSON のメタ情報: {"title":..., "description":..., "date":..., "tag":...}
本文中の {{LINK:型番}} は links/items.json の値から楽天リンクに置き換える。"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rlink import build as rlink

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "くらべてえらぶ"
BASE = "https://osusume-site.toresharetore.workers.dev"
items = json.loads((ROOT / "links/items.json").read_text(encoding="utf-8"))
legacy = json.loads((ROOT / "links/kashitsuki.json").read_text(encoding="utf-8"))

HEAD = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {site}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{base}/{slug}.html">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="site-header">
  <a class="logo" href="/">{site}</a>
  <nav class="nav"><a href="/about.html">このサイトについて</a><a href="/privacy.html">プライバシーポリシー</a></nav>
</header>
<main>
<p class="pr-note">【PR】この記事には広告(楽天アフィリエイト)のリンクが含まれます。</p>
<h1>{title}</h1>
<p class="meta">公開:{date} ／ 価格・仕様の確認日:{date}</p>
"""
FOOT = """
</main>
<footer class="site-footer">
  <nav><a href="/about.html">このサイトについて・運営者情報</a><a href="/privacy.html">プライバシーポリシー・免責事項</a></nav>
  <div>当サイトは楽天アフィリエイトを利用しています。記事内のリンクから商品が購入されると、運営者に紹介料が支払われることがあります。</div>
  <div>&copy; 2026 {site}</div>
</footer>
</body>
</html>
"""


def link(m):
    k = m.group(1)
    code = rlink(items[k]) if k in items else legacy[k]
    return f'<div class="table-wrap">{code}</div>'


def build_all():
    out = []
    for f in sorted((ROOT / "content").glob("*.html")):
        first, body = f.read_text(encoding="utf-8").split("\n", 1)
        meta = json.loads(first)
        slug = f.stem
        body = re.sub(r"\{\{LINK:([^}]+)\}\}", link, body)
        assert "{{" not in body, slug
        html = HEAD.format(site=SITE, base=BASE, slug=slug, **meta) + body + FOOT.format(site=SITE)
        (ROOT / "public" / f"{slug}.html").write_text(html, encoding="utf-8")
        out.append((slug, meta))
    return out


def write_index_and_sitemap(built):
    arts = [("kashitsuki-denkidai", "加湿器の電気代は方式で50倍違う！スチーム式は月3,050円、気化式は月60円【2026年モデルで計算】", "加湿器")]
    arts += [(s, m["title"], m.get("tag", "")) for s, m in built]
    items_html = "\n".join(f'  <li><a href="/{s}.html">{t}<span>2026年10月 ／ {g}</span></a></li>' for s, t, g in reversed(arts))
    ix = ROOT / "public/index.html"
    s = ix.read_text(encoding="utf-8")
    s = re.sub(r'(<ul class="cards" id="articles">\n).*?(\n</ul>)', lambda m: m.group(1) + items_html + m.group(2), s, flags=re.S)
    ix.write_text(s, encoding="utf-8")
    urls = [""] + [f"{a[0]}.html" for a in arts] + ["about.html", "privacy.html"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"<url><loc>{BASE}/{u}</loc><lastmod>2026-10-06</lastmod></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "public/sitemap.xml").write_text(sm, encoding="utf-8")


if __name__ == "__main__":
    write_index_and_sitemap(build_all())
