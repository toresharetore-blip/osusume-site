"""サイト全体を public/ に書き出す。
- content/*.html : 記事。1行目がJSONのメタ情報 {"title","description","date","tag"}、2行目以降が本文。
  本文の最初の <p class="lead"> は「この記事の結論」枠に、h2 から目次を自動で作る。
  {{LINK:型番}} は楽天リンク(links/items.json か links/kashitsuki.json)に置き換える。
- pages/*.html   : 固定ページ。1行目が<title>、2行目以降が本文。
- トップページとサイトマップも作る。"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rlink import build128 as rlink

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "くらべてえらぶ"
TAGLINE = "買う前に、仕様と価格を同じ表でくらべる"
BASE = "https://osusume-site.toresharetore.workers.dev"
items = json.loads((ROOT / "links/items.json").read_text(encoding="utf-8"))


def head(title, description, canonical):
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{BASE}/{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;800&display=swap">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="site-header"><div class="in">
  <a class="logo" href="/"><b>くらべて<i>えらぶ</i></b><small>{TAGLINE}</small></a>
  <nav class="nav"><a href="/about.html">このサイトについて</a><a href="/privacy.html">プライバシーポリシー</a></nav>
</div></header>
<div class="wrap">
"""


FOOT = f"""
</div>
<footer class="site-footer">
  <nav><a href="/">トップ</a><a href="/about.html">このサイトについて・運営者情報</a><a href="/privacy.html">プライバシーポリシー・免責事項</a></nav>
  <div>当サイトは楽天アフィリエイトを利用しています。記事内のリンクから商品が購入されると、運営者に紹介料が支払われることがあります。</div>
  <div>&copy; 2026 {SITE}</div>
</footer>
</body>
</html>
"""


def link(m):
    k = m.group(1)
    code = rlink(items[k])
    return f'<div class="product"><div class="table-wrap">{code}</div></div>'


def article(slug, meta, body):
    body = re.sub(r"\{\{LINK:([^}]+)\}\}", link, body)
    assert "{{" not in body, slug
    body = re.sub(r'<p class="lead">(.*?)</p>', r'<div class="answer"><p>\1</p></div>', body, count=1, flags=re.S)
    def hint(m):
        first_row = re.search(r"<tr>(.*?)</tr>", m.group(0), re.S).group(1)
        cols = first_row.count("<th")
        if cols >= 4:
            return '<p class="scroll-hint">表は横にスクロールできます →</p>' + m.group(0).replace("<table>", '<table class="wide">', 1)
        return m.group(0)
    body = re.sub(r'<div class="table-wrap"><table>.*?</table></div>', hint, body, flags=re.S)
    heads = []

    def add_id(m):
        n = len(heads) + 1
        heads.append(re.sub("<[^>]+>", "", m.group(1)))
        return f'<h2 id="s{n}">{m.group(1)}</h2>'
    body = re.sub(r"<h2>(.*?)</h2>", add_id, body)
    toc = '<nav class="toc"><b>目次</b><ol>' + "".join(f'<li><a href="#s{i+1}">{h}</a></li>' for i, h in enumerate(heads)) + "</ol></nav>"
    # 目次は結論枠と最初の説明段落のあと、最初の h2 の直前に置く
    body = body.replace('<h2 id="s1">', toc + '\n<h2 id="s1">', 1)
    top = (f'<article>\n<p class="crumb"><a href="/">トップ</a> ＞ {meta["tag"]}</p>\n'
           f'<p class="pr-note">PR 広告(楽天アフィリエイト)のリンクを含みます</p>\n'
           f'<h1>{meta["title"]}</h1>\n<p class="meta">公開・価格確認:{meta["date"]}</p>\n'
           f'<div class="badges"><span>メーカー・販売店の公表値で比較</span><span>出典つき</span></div>\n')
    return head(f'{meta["title"]} | {SITE}', meta["description"], f"{slug}.html") + top + body + "\n</article>" + FOOT


def build_all():
    out = []
    for f in sorted((ROOT / "content").glob("*.html")):
        first, body = f.read_text(encoding="utf-8").split("\n", 1)
        meta = json.loads(first)
        (ROOT / "public" / f"{f.stem}.html").write_text(article(f.stem, meta, body), encoding="utf-8")
        out.append((f.stem, meta))
    for f in sorted((ROOT / "pages").glob("*.html")):
        title, body = f.read_text(encoding="utf-8").split("\n", 1)
        html = head(title, f"{SITE}の{re.sub(' [|].*', '', title)}です。", f"{f.stem}.html") + f'<div class="panel">\n{body}\n</div>' + FOOT
        (ROOT / "public" / f"{f.stem}.html").write_text(html, encoding="utf-8")
    return out


def write_index_and_sitemap(built):
    order = sorted(built, key=lambda x: x[0] != "kashitsuki-denkidai")  # 総論の記事を先頭に
    cards = "\n".join(
        f'  <li><a href="/{s}.html"><span class="tag">{m["tag"]}</span><br>{m["title"]}<span class="d">{m["date"]}</span></a></li>'
        for s, m in order)
    body = (f'<section class="hero"><p class="pr-note">PR 当サイトの記事には広告(楽天アフィリエイト)のリンクが含まれます</p>\n'
            f'<h1>買う前に、くらべて選ぶ</h1>\n<p>メーカーと販売店が公表している仕様と価格を同じ表に並べ、どれを選べばいいかを短くまとめています。数字には出典を付けています。</p></section>\n'
            f'<h2 class="sec-title">新着記事</h2>\n<ul class="cards">\n{cards}\n</ul>')
    (ROOT / "public/index.html").write_text(head(SITE + "｜" + TAGLINE, "買う前に、メーカー公表の仕様と価格を同じ表に並べて比べる商品比較サイトです。", "") + body + FOOT, encoding="utf-8")
    urls = [""] + [f"{s}.html" for s, _ in order] + ["about.html", "privacy.html"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"<url><loc>{BASE}/{u}</loc><lastmod>2026-10-06</lastmod></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "public/sitemap.xml").write_text(sm, encoding="utf-8")


if __name__ == "__main__":
    write_index_and_sitemap(build_all())
    print("built")
