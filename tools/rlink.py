"""楽天アフィリエイトの「画像とテキスト(240x240)」リンクを、リンク作成画面と同じ形で組み立てる。
値はリンク作成画面のソースから取り出したものだけを使う(改変しない)。"""
UT = "eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0dGV4dCIsInNpemUiOiIyNDB4MjQwIiwibmFtIjoxLCJuYW1wIjoicmlnaHQiLCJjb20iOjEsImNvbXAiOiJkb3duIiwicHJpY2UiOjEsImJvciI6MSwiY29sIjoxLCJiYnRuIjoxLCJwcm9kIjowLCJhbXAiOmZhbHNlfQ"
ALT = "[商品価格に関しましては、リンクが作成された時点と現時点で情報が変更されている場合がございます。]"


def build(d):
    base = f"https://hb.afl.rakuten.co.jp/ichiba/{d['id']}/?pc={d['pc']}&link_type=picttext&ut={UT}%3D%3D"
    btn = f"https://hb.afl.rakuten.co.jp/ichiba/{d['id']}/?pc={d['pc']}%3Fscid%3Daf_pc_bbtn&link_type=picttext&ut={UT}=="
    a = 'target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"'
    return (
        '<table border="0" cellpadding="0" cellspacing="0"><tr><td><div style="border:1px solid #95a5a6;border-radius:.75rem;background-color:#FFFFFF;width:504px;margin:0px;padding:5px;text-align:center;overflow:hidden;"><table><tr><td style="width:240px">'
        f'<a href="{base}" {a}><img src="{d["img"]}" border="0" style="margin:2px" alt="{ALT}" title="{ALT}"></a></td>'
        '<td style="vertical-align:top;width:248px;display: block;"><p style="font-size:12px;line-height:1.4em;text-align:left;margin:0px;padding:2px 6px;word-wrap:break-word">'
        f'<a href="{base}" {a}>{d["name"]}</a><br><span >{d["price"]}</span> <span style="color:#BBB">{d["date"]}</span></p>'
        f'<div style="margin:10px;"><a href="{base}" {a}><img src="https://static.affiliate.rakuten.co.jp/makelink/rl.svg" style="float:left;max-height:27px;width:auto;margin-top:0" ></a>'
        f'<a href="{btn}" {a}><div style="float:right;width:41%;height:27px;background-color:#bf0000;color:#fff!important;font-size:12px;font-weight:500;line-height:27px;margin-left:1px;padding: 0 12px;border-radius:16px;cursor:pointer;text-align:center;"> 楽天で購入 </div></a></div>'
        '</td></tr></table></div><br><p style="color:#000000;font-size:12px;line-height:1.4em;margin:5px;word-wrap:break-word"></p></td></tr></table>'
    )


UT128 = "eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0dGV4dCIsInNpemUiOiIxMjh4MTI4IiwibmFtIjoxLCJuYW1wIjoicmlnaHQiLCJjb20iOjEsImNvbXAiOiJkb3duIiwicHJpY2UiOjEsImJvciI6MSwiY29sIjoxLCJiYnRuIjoxLCJwcm9kIjowLCJhbXAiOmZhbHNlfQ"


def build128(d):
    """スマホ幅に収まる「画像とテキスト(128x128)」版。リンク作成画面でサイズ128を選んだ時と同じ形。"""
    base = f"https://hb.afl.rakuten.co.jp/ichiba/{d['id']}/?pc={d['pc']}&link_type=picttext&ut={UT128}%3D%3D"
    import re as _re
    img = _re.sub(r"\d+x\d+", "128x128", d["img"])
    a = 'target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"'
    return (
        '<table border="0" cellpadding="0" cellspacing="0"><tr><td><div style="border:1px solid #95a5a6;border-radius:.75rem;background-color:#FFFFFF;width:280px;margin:0px;padding:5px;text-align:center;overflow:hidden;"><table><tr><td style="width:128px">'
        f'<a href="{base}" {a}><img src="{img}" border="0" style="margin:2px" alt="{ALT}" title="{ALT}"></a></td>'
        '<td style="vertical-align:top;width:136px;display: block;"><p style="font-size:12px;line-height:1.4em;text-align:left;margin:0px;padding:2px 6px;word-wrap:break-word">'
        f'<a href="{base}" {a}>{d["name"]}</a><br><span >{d["price"]}</span> <span style="color:#BBB">{d["date"]}</span></p>'
        '</td></tr></table></div><br><p style="color:#000000;font-size:12px;line-height:1.4em;margin:5px;word-wrap:break-word"></p></td></tr></table>'
    )


def thumb_url(d, size=240):
    """表示用の商品画像。広告ブロッカーに消されにくいよう、楽天の画像サーバーのURLを直接使う。"""
    from urllib.parse import urlparse, parse_qs
    q = parse_qs(urlparse(d["img"]).query)
    import re as _re
    return _re.sub(r"_ex=\d+x\d+", f"_ex={size}x{size}", q["pc"][0])


def card(d):
    """商品カード(楽天のアフィリエイトURLと画像をそのまま使い、表示だけ自前のデザインにする)。"""
    base = f"https://hb.afl.rakuten.co.jp/ichiba/{d['id']}/?pc={d['pc']}&link_type=picttext&ut={UT}%3D%3D"
    a = 'target="_blank" rel="nofollow sponsored noopener"'
    chips = "".join(f"<li>{c}</li>" for c in d.get("chips", []))
    import re as _re
    m = _re.match(r"価格：([\d,]+円)(.*)", d["price"])
    price = f'{m.group(1)}<span class="tax">{m.group(2)}</span>' if m else d["price"]
    return (f'<div class="pcard"><a class="pimg" href="{base}" {a}><img src="{thumb_url(d)}" alt="{d["short"]}" loading="lazy" width="240" height="240"></a>'
            f'<div class="pbody"><p class="pname"><a href="{base}" {a}>{d["short"]}</a></p><ul class="chips">{chips}</ul>'
            f'<p class="pprice">{price}<small>楽天市場での価格{d["date"]}。最新の価格は販売ページで確認してください</small></p>'
            f'<a class="pbtn" href="{base}" {a}>楽天市場で見る</a></div></div>')


def minicard(d, label="この記事のおすすめ"):
    """記事上部に置く小さな商品リンク(結論のすぐ下で楽天へ進めるように)。"""
    base = f"https://hb.afl.rakuten.co.jp/ichiba/{d['id']}/?pc={d['pc']}&link_type=picttext&ut={UT}%3D%3D"
    a = 'target="_blank" rel="nofollow sponsored noopener"'
    import re as _re
    m = _re.match(r"価格：([\d,]+円)", d["price"])
    price = m.group(1) if m else ""
    return (f'<div class="minicard"><span class="mlabel">{label}</span><a class="mrow" href="{base}" {a}>'
            f'<img src="{thumb_url(d, 128)}" alt="" width="64" height="64" loading="lazy">'
            f'<span class="mtxt"><b>{d["short"]}</b><span>楽天市場 {price}〜{d["date"]}</span></span>'
            f'<span class="mbtn">価格とレビューを見る</span></a></div>')


def minirow(d, article_url):
    """「同じカテゴリーでよく売れている商品」の1行。"""
    base = f"https://hb.afl.rakuten.co.jp/ichiba/{d['id']}/?pc={d['pc']}&link_type=picttext&ut={UT}%3D%3D"
    a = 'target="_blank" rel="nofollow sponsored noopener"'
    import re as _re
    m = _re.match(r"価格：([\d,]+円)", d["price"])
    price = m.group(1) if m else ""
    rv = f'・レビュー{d["reviews"]:,}件' if d.get("reviews") else ""
    return (f'<div class="arow"><a class="aimg" href="{base}" {a}><img src="{thumb_url(d, 128)}" alt="" width="56" height="56" loading="lazy"></a>'
            f'<div class="atxt"><a class="aname" href="{base}" {a}>{d["short"]}</a><span>楽天市場 {price}〜{rv}</span>'
            f'<a class="aart" href="{article_url}">この商品の比較記事を読む</a></div>'
            f'<a class="abtn" href="{base}" {a}>楽天で見る</a></div>')


def _yen(d):
    import re as _re
    m = _re.match(r"価格：([\d,]+)円", d["price"])
    return int(m.group(1).replace(",", "")) if m else None


def pricebox(ds, pick=None, names=None):
    """結論のすぐ下に置く「比べた商品の楽天価格」。安い順に全商品を同じ扱いで並べ、読者が自分で選べるようにする。"""
    a = 'target="_blank" rel="nofollow sponsored noopener"'
    rows = sorted(ds, key=lambda kd: (_yen(kd[1]) is None, _yen(kd[1]) or 0))
    out = []
    for i, (k, d) in enumerate(rows):
        base = f"https://hb.afl.rakuten.co.jp/ichiba/{d['id']}/?pc={d['pc']}&link_type=picttext&ut={UT}%3D%3D"
        y = _yen(d)
        price = f"{y:,}円{'〜' if '～' in d['price'] or '〜' in d['price'] else ''}" if y else ""
        tags = ""
        if i == 0 and len(rows) > 1:
            tags += '<em class="t-cheap">いちばん安い</em>'
        if k == pick and len(rows) > 1:
            tags += '<em class="t-pick">記事のおすすめ</em>'
        rv = f'・レビュー{d["reviews"]:,}件' if d.get("reviews") else ""
        nm = (names or {}).get(k)
        label = d["short"]
        out.append(f'<a class="prow" href="{base}" {a}><img src="{thumb_url(d, 128)}" alt="" width="56" height="56" loading="lazy">'
                   f'<span class="ptxt"><span class="ptags">{tags}</span><b>{label}</b><span>楽天市場 <strong>{price}</strong>{d["date"]}{rv}</span></span>'
                   f'<span class="pgo">楽天で見る</span></a>')
    return ('<div class="pricebox"><p class="plabel">この記事で比べた商品の楽天価格(安い順)</p>' + "".join(out) +
            '<p class="pnote">価格は確認日時点。最新の価格・在庫は販売ページで確認してください。</p></div>')
