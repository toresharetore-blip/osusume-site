"""サイト全体を public/ に書き出す。
- content/*.html : 記事。1行目がJSONのメタ情報 {"title","description","date","tag"}、2行目以降が本文。
  本文の最初の <p class="lead"> は「この記事の結論」枠に、h2 から目次を自動で作る。
  {{LINK:型番}} は楽天リンク(links/items.json か links/kashitsuki.json)に置き換える。
- pages/*.html   : 固定ページ。1行目が<title>、2行目以降が本文。
- トップページとサイトマップも作る。"""
import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from rlink import build128 as rlink, card, thumb_url

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "くらべてえらぶ"
TAGLINE = "ベビー・子育て用品の型番を、同じ表でくらべる"
BASE = "https://osusume-site.toresharetore.workers.dev"
items = json.loads((ROOT / "links/items.json").read_text(encoding="utf-8"))


CATS = {"加湿器": "kashitsuki", "ふとん乾燥機": "futon-kansouki", "ドライヤー": "dryer", "衣類スチーマー": "steamer", "チャイルドシート": "childseat", "抱っこひも": "carrier", "ベビーカー": "stroller", "ベビーラック": "babyrack", "マグ・食器": "mug", "おむつ": "omutsu"}


GROUPS = [("ベビー・キッズ", ["チャイルドシート", "ベビーカー", "抱っこひも", "ベビーラック", "マグ・食器", "おむつ"]),
          ("家電", ["加湿器", "ふとん乾燥機", "ドライヤー", "衣類スチーマー"])]
for _c in CATS:
    if not any(_c in g for _, g in GROUPS):
        GROUPS[-1][1].append(_c)


def cat_url(tag):
    return f"/category/{CATS.get(tag, 'other')}.html"


def head(title, description, canonical, og_image=None, jsonld=None):
    catnav = "".join(f'<div class="grp"><p>{g}</p>' + "".join(f'<a href="{cat_url(c)}">{c}</a>' for c in cs) + '</div>' for g, cs in GROUPS)
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{BASE}/{canonical}">
<meta property="og:type" content="{"article" if og_image else "website"}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{BASE}/{canonical}">
{f'<meta property="og:image" content="{og_image}">' if og_image else ""}
<meta name="twitter:card" content="summary">
{f'<script type="application/ld+json">{jsonld}</script>' if jsonld else ""}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;800&display=swap">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="site-header"><div class="in">
  <a class="logo" href="/"><b>くらべて<i>えらぶ</i></b><small>{TAGLINE}</small></a>
  <form class="sbox" action="/search.html" method="get" role="search"><input type="search" name="q" placeholder="型番・商品名で検索" aria-label="サイト内検索"><button type="submit" aria-label="検索">検索</button></form>
  <details class="catmenu"><summary>カテゴリー</summary><div class="catpanel"><a class="all" href="/">すべての記事</a>{catnav}</div></details>
</div>
</header>
<div class="wrap">
"""


FOOT = f"""
</div>
<footer class="site-footer">
  <nav class="fcats">{"".join(f'<a href="/category/{v}.html">{k}</a>' for k, v in CATS.items())}</nav>
  <nav><a href="/">トップ</a><a href="/about.html">このサイトについて・運営者情報</a><a href="/privacy.html">プライバシーポリシー・免責事項</a></nav>
  <div>当サイトは楽天アフィリエイトを利用しています。記事内のリンクから商品が購入されると、運営者に紹介料が支払われることがあります。</div>
  <div>&copy; 2026 {SITE}</div>
</footer>
<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "f4f779e247ca4834a480cbd373d1959a"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


def cardsub(m):
    return card(items[m.group(1)])


def bars(m):
    """{{BARS:タイトル|補足|単位|ラベル=値[!hi|!bad]|...}} を横棒グラフにする"""
    parts = m.group(1).split("|")
    title, sub, unit, rows = parts[0], parts[1], parts[2], parts[3:]
    data = []
    for r in rows:
        lab, v = r.split("=")
        flag = ""
        if "!" in v:
            v, flag = v.split("!")
        data.append((lab, float(v.replace(",", "")), flag))
    mx = max(v for _, v, _ in data)
    out = [f'<div class="chart"><p class="ct">{title}</p><p class="cs">{sub}</p>']
    for lab, v, flag in data:
        w = v / mx * 100
        txt = (f"{v:,.0f}{unit}" if v >= 1000 or v == int(v) else f"{v:g}{unit}")
        cls = "val out" if w > 55 else "val"
        style = f"left:calc({max(w,1):.1f}% + 6px)" if w <= 55 else ""
        out.append(f'<div class="row {flag}"><span class="lab">{lab}</span><span class="track"><span class="fill" style="--w:{w:.1f}"></span>'
                   f'<span class="{cls}" style="{style}">{txt}</span></span></div>')
    out.append("</div>")
    return "".join(out)


def verdict(m):
    """{{VERDICT:見出し=値|見出し=値|見出し=値*}} 末尾*の枠を強調"""
    tiles = []
    for t in m.group(1).split("|"):
        k, v = t.split("=")
        go = v.endswith("*")
        tiles.append(f'<div class="{"go" if go else ""}"><span>{k}</span><b>{v.rstrip("*")}</b></div>')
    return '<div class="verdict">' + "".join(tiles) + "</div>"


def diffcount(body):
    """比較表の「同じ」セルを数えて、違う項目数を表の上に出す"""
    def f(m):
        table = m.group(0)
        rows = re.findall(r"<tr>(.*?)</tr>", table, re.S)[1:]
        if not rows or 'class="same"' not in table:
            return table
        same = sum(1 for r in rows if 'class="same"' in r)
        diff = len(rows) - same
        boxes = "".join('<i class="d"></i>' for _ in range(diff)) + "".join("<i></i>" for _ in range(same))
        return f'<div class="diffcount">{boxes}<span>全{len(rows)}項目のうち、違いがあるのは<b>{diff}項目</b></span></div>' + table
    return re.sub(r'<div class="table-wrap"><table>.*?</table></div>', f, body, flags=re.S)


def link(m):
    k = m.group(1)
    code = rlink(items[k])
    return f'<div class="product"><div class="table-wrap">{code}</div></div>'


def eye(meta, link_title=None):
    e = meta.get("eye")
    if not e:
        return ""
    imgs = []
    for i, k in enumerate(e.get("items", [])):
        if i:
            imgs.append('<span class="vs">VS</span>' if e.get("vs", True) else "")
        imgs.append(f'<span><img src="{thumb_url(items[k], 128)}" alt="" width="72" height="72">{e.get("names", {}).get(k, k)}</span>')
    t = f'<p class="t">{link_title}</p>' if link_title else ""
    return (f'<div class="eye"><div class="k">{e.get("kicker", meta["tag"])}</div>{t}'
            f'<div class="big">{e["big"]}</div><p class="lb">{e["label"]}</p>'
            f'<div class="imgs">{"".join(imgs)}</div></div>')


def th_images(body):
    """比較表の見出しセルに型番があれば、その商品写真を添える"""
    def f(m):
        cell = m.group(1)
        for k in items:
            if k in cell and "th-img" not in cell:
                return f'<th><img class="th-img" src="{thumb_url(items[k], 128)}" alt="" width="44" height="44">{cell}</th>'
        return m.group(0)
    return re.sub(r"<th>(.*?)</th>", f, body)


def thumb_html(m, size=64):
    k = m.get("thumb")
    return f'<span class="thumb"><img src="{thumb_url(items[k], 128)}" alt="" loading="lazy" width="{size}" height="{size}"></span>' if k else '<span class="thumb"></span>'


def card_li(s_, m):
    return (f'  <li data-cat="{CATS.get(m["tag"], "other")}"><a href="/{s_}.html">{thumb_html(m)}<span class="txt"><span class="ttl">{m.get("short", m["title"])}</span>'
            f'<span class="meta2"><span class="tag">{m["tag"]}</span><span>{m["date"]}</span></span></span></a></li>')


ITEM_HOME = {}


def also_items(slug, meta, body):
    """同じカテゴリーで楽天のレビューが多い、この記事に出てこない商品を3つ"""
    here = set(re.findall(r"\{\{CARD:([^}]+)\}\}", body))
    cand = [(k, h) for k, h in ITEM_HOME.items() if h[0] == meta["tag"] and k not in here and items[k].get("reviews", 0) > 0]
    cand.sort(key=lambda x: -items[x[0]].get("reviews", 0))
    here_names = {re.sub(r"[(（].*", "", items[k]["short"]).strip() for k in here if k in items}
    seen, uniq = set(here_names), []
    for k, h in cand:
        nm = re.sub(r"[(（].*", "", items[k]["short"]).strip()
        if nm not in seen:
            seen.add(nm); uniq.append((k, h))
    cand = uniq
    if not cand:
        return ""
    from rlink import minirow
    rows = "".join(minirow(items[k], f"/{h[1]}.html") for k, h in cand[:3])
    return (f'<section class="alsobuy"><p class="sec-title">同じカテゴリーでよく売れている商品</p>'
            f'<p class="sec-note">楽天市場でレビューが多い順です。それぞれの比較記事もあります。</p>{rows}</section>')


def article(slug, meta, body, all_meta):
    alsobuy = also_items(slug, meta, body)
    first_card = (re.findall(r"\{\{CARD:([^}]+)\}\}", body) or [None])[0]
    pick = meta.get("pick", first_card)
    body = re.sub(r"\{\{CARD:([^}]+)\}\}", cardsub, body)
    body = re.sub(r"\{\{BARS:([^}]+)\}\}", bars, body)
    body = re.sub(r"\{\{VERDICT:([^}]+)\}\}", verdict, body)
    body = diffcount(body)
    body = th_images(body)
    body = re.sub(r"\{\{LINK:([^}]+)\}\}", link, body)
    assert "{{" not in body, slug
    body = re.sub(r'<p class="lead">(.*?)</p>', r'<div class="answer"><p>\1</p></div>', body, count=1, flags=re.S)
    if pick and pick in items:
        from rlink import minicard
        body = body.replace('</div>', '</div>\n' + minicard(items[pick]), 1) if body.startswith('<div class="answer">') else body

    def hint(m):
        first_row = re.search(r"<tr>(.*?)</tr>", m.group(0), re.S).group(1)
        if first_row.count("<th") >= 4:
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
    body = body.replace('<h2 id="s1">', toc + '\n<h2 id="s1">', 1)
    top = (f'<article>\n<p class="crumb"><a href="/">トップ</a> ＞ <a href="{cat_url(meta["tag"])}">{meta["tag"]}</a></p>\n'
           f'<p class="pr-note">PR 広告(楽天アフィリエイト)のリンクを含みます</p>\n'
           f'<h1>{meta["title"]}</h1>\n<p class="meta">公開・価格確認:{meta["date"]}</p>\n'
           f'<div class="badges"><span>メーカー・販売店の公表値で比較</span><span>出典つき</span></div>\n' + eye(meta))
    writer = ('<div class="writer"><p><b>くらべてえらぶ編集部</b><br>メーカーと販売店が公表している仕様・価格を同じ基準で表にまとめています。'
              '数値には出典を付け、実際に使って試していない商品はその旨を明記しています。'
              '<a href="/about.html">運営方針を見る</a></p></div>')
    # 関連記事(同じカテゴリーを優先、足りなければ他から)
    same = [(s_, m) for s_, m in all_meta if s_ != slug and m["tag"] == meta["tag"]]
    other = [(s_, m) for s_, m in all_meta if s_ != slug and m["tag"] != meta["tag"]]
    rel = (same + other)[:4]
    related = ('<section class="related"><h2 class="sec-title">あわせて読みたい</h2><ul class="cards">' +
               "".join(card_li(s_, m) for s_, m in rel) + "</ul></section>") if rel else ""
    og = thumb_url(items[meta["thumb"]], 240) if meta.get("thumb") else None
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Article", "headline": meta["title"], "description": meta["description"],
             "datePublished": "2026-10-07", "dateModified": "2026-10-06",
             "author": {"@type": "Organization", "name": SITE + "編集部", "url": BASE + "/about.html"},
             "publisher": {"@type": "Organization", "name": SITE}, "image": og, "mainEntityOfPage": f"{BASE}/{slug}.html"},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "トップ", "item": BASE + "/"},
                {"@type": "ListItem", "position": 2, "name": meta["tag"], "item": BASE + cat_url(meta["tag"])},
                {"@type": "ListItem", "position": 3, "name": meta.get("short", meta["title"])}]}]}, ensure_ascii=False)
    return (head(f'{meta["title"]} | {SITE}', meta["description"], f"{slug}.html", og, jsonld)
            + top + (body.replace('<h2 id="s' + str(len(heads)) + '">出典', alsobuy + '<h2 id="s' + str(len(heads)) + '">出典', 1) if alsobuy and ('<h2 id="s' + str(len(heads)) + '">出典') in body else body + alsobuy) + writer + "\n</article>" + related + FOOT)


def _pubtime(f):
    import subprocess, time
    try:
        r = subprocess.run(["git", "log", "--diff-filter=A", "--format=%ct", "--", str(f)], cwd=ROOT, capture_output=True, text=True)
        ts = [int(x) for x in r.stdout.split()]
        return min(ts) if ts else int(time.time())
    except Exception:
        return int(time.time())


def load_all():
    out = []
    for f in sorted((ROOT / "content").glob("*.html")):
        first, body = f.read_text(encoding="utf-8").split("\n", 1)
        m = json.loads(first)
        m["_pub"] = _pubtime(f)
        keys = re.findall(r"\{\{CARD:([^}]+)\}\}", body)
        m["_pop"] = max([items.get(k, {}).get("reviews", 0) for k in keys] or [0])
        out.append((f.stem, m, body))
    return out


def build_all():
    loaded = load_all()
    for s_, m, body in sorted(loaded, key=lambda x: x[1]["_pub"]):
        for k in re.findall(r"\{\{CARD:([^}]+)\}\}", body):
            ITEM_HOME.setdefault(k, (m["tag"], s_))
    order = sorted([(s_, m) for s_, m, _ in loaded], key=lambda x: (x[0] != "kashitsuki-denkidai", x[1].get("order", 50), x[0]))
    for s_, m, body in loaded:
        (ROOT / "public" / f"{s_}.html").write_text(article(s_, m, body, order), encoding="utf-8")
    for f in sorted((ROOT / "pages").glob("*.html")):
        title, body = f.read_text(encoding="utf-8").split("\n", 1)
        html = head(title, f"{SITE}の{re.sub(' [|].*', '', title)}です。", f"{f.stem}.html") + f'<div class="panel">\n{body}\n</div>' + FOOT
        (ROOT / "public" / f"{f.stem}.html").write_text(html, encoding="utf-8")
    return order


ICON_SVG = lambda d, c: f'<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{d}</svg>'
ICONS = {"加湿器": ICON_SVG('<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>', "#2C7BD0"),
         "ふとん乾燥機": ICON_SVG('<path d="M3 18V8M21 18v-5a3 3 0 0 0-3-3H8v8M3 14h18"/><circle cx="6" cy="11" r="1.5"/>', "#DD7413"),
         "ドライヤー": ICON_SVG('<path d="M4 8h10a4 4 0 0 1 0 8H4zM9 16l-2 5M17 9h4M17 12h3M17 15h4"/>', "#6A4FB0"),
         "衣類スチーマー": ICON_SVG('<path d="M4 15c0-4 3-7 8-7h6a2 2 0 0 1 2 2v5zM4 15h16M8 5c0-1 1-1 1-2M12 5c0-1 1-1 1-2"/>', "#1F8A70"),
         "チャイルドシート": ICON_SVG('<path d="M7 3h6a3 3 0 0 1 3 3v7l3 5H6l1-5z"/><path d="M10 9h4M8 21h11"/>', "#D0457A"),
         "抱っこひも": ICON_SVG('<circle cx="12" cy="5" r="2.5"/><path d="M7 9c0 6 2 9 5 9s5-3 5-9M7 9l-2 12M17 9l2 12"/>', "#7A5AC8"),
         "ベビーカー": ICON_SVG('<path d="M4 6h3l2 8h9l2-6H8"/><circle cx="9" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>', "#2A8C8C"),
         "ベビーラック": ICON_SVG('<path d="M5 20l3-6h8l3 6M8 14V7a4 4 0 0 1 8 0v7"/>', "#C77D2E"),
         "マグ・食器": ICON_SVG('<path d="M6 8h10v9a3 3 0 0 1-3 3H9a3 3 0 0 1-3-3zM16 10h2a2 2 0 0 1 0 4h-2M11 8V3"/>', "#3B8FB5"),
         "おむつ": ICON_SVG('<path d="M3 7h18v3c0 6-4 10-9 10S3 16 3 10z"/><path d="M3 10h4M17 10h4"/>', "#5A9BD5")}


def feature_and_cats(order):
    top = next((x for x in order if x[1].get("feature")), None) or next((x for x in order if x[1].get("eye")), None)
    feat = f'<a class="feature" href="/{top[0]}.html">{eye(top[1], top[1].get("short", top[1]["title"]))}</a>' if top else ""
    counts = {}
    for _, m in order:
        counts[m["tag"]] = counts.get(m["tag"], 0) + 1
    return feat


SEARCH_JS = """<script>
(function(){
  var q=new URLSearchParams(location.search).get('q')||'';
  var inp=document.getElementById('q'); inp.value=q;
  var msg=document.getElementById('sres-msg'), ul=document.getElementById('sres');
  function norm(s){return (s||'').normalize('NFKC').toLowerCase().replace(/[\\s・　]+/g,' ');}
  function esc(s){return s.replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  if(!q.trim()){msg.textContent='型番や商品名、カテゴリー名を入れて検索してください。';return;}
  fetch('/search-index.json').then(function(r){return r.json();}).then(function(idx){
    var terms=norm(q).split(' ').filter(Boolean);
    var hits=idx.filter(function(x){var hay=norm(x.t+' '+x.h+' '+x.d+' '+x.c).replace(/ /g,'');return terms.every(function(t){return hay.indexOf(t.replace(/ /g,''))>=0;});});
    hits.sort(function(a,b){return b.p-a.p;});
    msg.textContent='「'+q+'」の検索結果:'+hits.length+'件'+(hits.length?'':'。別の言葉(型番の一部やカテゴリー名)でもお試しください。');
    ul.innerHTML=hits.map(function(x){return '<li><a href="'+x.u+'"><span class="thumb">'+(x.i?'<img src="'+x.i+'" alt="" width="64" height="64" loading="lazy">':'')+'</span><span class="txt"><span class="ttl">'+esc(x.t)+'</span><span class="meta2"><span class="tag">'+esc(x.c)+'</span></span></span></a></li>';}).join('');
  });
})();
</script>"""


FILTER_JS = """<script>
(function(){
  var sel=document.getElementById('catsel');
  var items=document.querySelectorAll('#list li');
  function show(c){
    items.forEach(function(li){li.hidden = !(c==='all' || li.dataset.cat===c);});
  }
  sel.addEventListener('change',function(){show(sel.value);});
  show(sel.value);
})();
</script>"""


def write_index_and_sitemap(order):
    counts = {}
    for _, m in order:
        counts[m["tag"]] = counts.get(m["tag"], 0) + 1
    opts = "".join(f'<optgroup label="{g}">' + "".join(f'<option value="{CATS[c]}">{c}({counts.get(c, 0)}本)</option>' for c in cs) + '</optgroup>' for g, cs in GROUPS)
    tabs = (f'<div class="ffilter"><label for="catsel">カテゴリーで絞り込む</label>'
            f'<select id="catsel"><option value="all">すべて({len(order)}本)</option>{opts}</select></div>')
    cards = "\n".join(card_li(s_, m) for s_, m in order)
    latest = sorted(order, key=lambda x: -x[1]["_pub"])
    popular, seen_tag = [], set()
    baby_tags = set(GROUPS[0][1])
    for x in sorted([x for x in order if x[1]["_pop"] > 0 and x[1]["tag"] in baby_tags], key=lambda x: -x[1]["_pop"]):
        if x[1]["tag"] not in seen_tag:
            popular.append(x); seen_tag.add(x[1]["tag"])
        if len(popular) == 4:
            break
    cards_latest = "\n".join(card_li(s_, m) for s_, m in latest[:4])
    cards_pop = "\n".join(card_li(s_, m) for s_, m in popular)
    cards = "\n".join(card_li(s_, m) for s_, m in latest)
    body = (f'<section class="hero"><p class="pr-note">PR 当サイトの記事には広告(楽天アフィリエイト)のリンクが含まれます</p>\n'
            f'<h1>ベビー・子育て用品を、買う前にくらべる</h1>\n<p>チャイルドシート、ベビーカー、抱っこひもなどの<strong>型番の違い</strong>と<strong>いつまで使えるか</strong>を、メーカーの公表値で同じ表に並べています。数字には出典を付けています。</p>'
            f'<div class="stats"><div><b>{len(order)}本</b>比較記事</div><div><b>全記事</b>出典つき</div><div><b>毎回</b>価格の確認日を表示</div></div></section>\n'
            f'<h2 class="sec-title">最新の記事</h2>\n<ul class="cards">\n{cards_latest}\n</ul>\n'
            f'<h2 class="sec-title">人気の記事</h2>\n<p class="sec-note">楽天市場でレビューが多い(よく売れている)商品をあつかった記事です。</p>\n<ul class="cards">\n{cards_pop}\n</ul>\n'
            f'<h2 class="sec-title" id="list-title">記事一覧</h2>\n{tabs}\n<ul class="cards" id="list">\n{cards}\n</ul>' + FILTER_JS)
    (ROOT / "public/index.html").write_text(head(SITE + "｜" + TAGLINE, "チャイルドシート・ベビーカー・抱っこひもなど、ベビー・子育て用品の型番の違いといつまで使えるかを、メーカー公表の仕様と価格で比べるサイトです。", "") + body + FOOT, encoding="utf-8")
    # サイト内検索
    idx = [{"u": f"/{s_}.html", "t": m.get("short", m["title"]), "h": m["title"], "d": m["description"], "c": m["tag"],
            "i": thumb_url(items[m["thumb"]], 128) if m.get("thumb") else "", "p": m["_pub"]} for s_, m in order]
    (ROOT / "public/search-index.json").write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")
    sb = ('<section class="hero"><p class="crumb"><a href="/">トップ</a> ＞ サイト内検索</p><h1>サイト内検索</h1>'
          '<form class="sbox big" action="/search.html" method="get" role="search"><input type="search" name="q" id="q" placeholder="例:オムニクラシック、クルムーヴ、ベビーカー" aria-label="サイト内検索"><button type="submit">検索</button></form>'
          '<p id="sres-msg" class="sec-note"></p></section>\n<ul class="cards" id="sres"></ul>' + SEARCH_JS)
    (ROOT / "public/search.html").write_text(head(f"サイト内検索 | {SITE}", "くらべてえらぶのサイト内検索です。", "search.html") + sb + FOOT, encoding="utf-8")
    # カテゴリーページ
    (ROOT / "public/category").mkdir(exist_ok=True)
    for c, slug in CATS.items():
        lst = sorted([(s_, m) for s_, m in order if m["tag"] == c], key=lambda x: -x[1]["_pub"])
        cards_c = "\n".join(card_li(s_, m) for s_, m in lst)
        b = (f'<section class="hero"><p class="crumb"><a href="/">トップ</a> ＞ {c}</p><h1>{ICONS.get(c, "")} {c}の比較記事</h1>'
             f'<p>{c}の型番ごとの違いを、メーカーと販売店の公表値で比べた記事です。全{len(lst)}本。</p></section>\n'
             f'<ul class="cards" id="list">\n{cards_c}\n</ul>')
        (ROOT / "public/category" / f"{slug}.html").write_text(
            head(f"{c}の比較記事一覧 | {SITE}", f"{c}の型番の違いを公表値で比べた記事の一覧です。", f"category/{slug}.html") + b + FOOT, encoding="utf-8")
    urls = [""] + [f"category/{v}.html" for v in CATS.values()] + [f"{s_}.html" for s_, _ in order] + ["about.html", "privacy.html"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"<url><loc>{BASE}/{u}</loc><lastmod>2026-10-07</lastmod></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "public/sitemap.xml").write_text(sm, encoding="utf-8")


if __name__ == "__main__":
    write_index_and_sitemap(build_all())
    print("built")
