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
    img = d["img"].replace("240x240", "128x128")
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
    return q["pc"][0].replace("240x240", f"{size}x{size}")


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
