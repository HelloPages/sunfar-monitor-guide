"""Generate an accessible static training page from the specifications and lesson content."""
from html import escape as e
from pathlib import Path
from urllib.parse import urlparse
import json
import re

ROOT = Path(__file__).resolve().parent
DOCS = ROOT/"docs"
specs = json.loads((ROOT/"specs.json").read_text(encoding="utf-8"))
content = json.loads((ROOT/"content.json").read_text(encoding="utf-8"))
groups, notes = content["groups"], content["items"]
by_id = {p["item_id"]:p for p in specs}
assert len(specs)==len(by_id)==14 and len({p["model"] for p in specs})==12
assert set(by_id)==set(notes) and set(groups)=={p["group"] for p in specs}
assert len(content["needs"])==len(groups)==6 and len(content["questions"])==10

def title(p):
    return notes[p["item_id"]][0]

def image(p, *, tile=False, hero=False):
    key = p["item_id"]
    assert (DOCS/f"images/{key}.webp").is_file(), key
    alt = "" if tile else f"{title(p)}{'組合示意' if p['group']=='followme' else '產品外觀'}"
    loading = 'fetchpriority="high"' if hero else 'loading="lazy"'
    return f'<img src="images/{key}.webp" alt="{e(alt)}" {loading} decoding="async">'

def tile(p):
    key = p["item_id"]
    return f'''<li class="tile" data-key="{key}"><a href="#{key}">
      <span class="tile-photo">{image(p,tile=True)}</span><span class="tile-title">{e(title(p))}</span>
      <span class="tile-model">{e(p["model"])}</span></a></li>'''

def price(p):
    row = content["prices"].get(p["item_id"])
    if not row:
        return '<div class="price unavailable">實售請洽門市</div>'
    amount, source = row
    assert urlparse(source).hostname=="news.samsung.com"
    return f'''<div class="price"><span>三星上市建議售價</span><strong><small>NT$</small>{amount:,}</strong>
      <a href="{e(source)}" target="_blank" rel="noopener">查閱公告</a></div>'''

def spec_rows(p):
    labels = ("尺寸／面板","解析度","最高更新率","反應時間","HDR","典型亮度／色域","同步技術","主要連接埠","支架／壁掛（mm）","選購特點")
    if p["group"] not in {"oled","ips","curve"}:
        labels = ("尺寸／面板","解析度／效能","亮度／色域","主要連接埠","使用功能","支架／壁掛（mm）")
    return "".join(f"<div><dt>{e(k)}</dt><dd>{e(v).replace(chr(10), '<br>')}</dd></div>"
                   for k,v in zip(labels,p["rows"],strict=True))

def card(p):
    key, group, model = p["item_id"], p["group"], p["model"]
    name, fit, question, points, demo = notes[key]
    assert len(points)==3 and urlparse(p["url"]).hostname=="www.samsung.com"
    lines = "".join(f"<li>{e(line)}</li>" for line in points)
    shared = group=="followme" or key=="m7_desktop_white"
    source = "查看台灣三星面板規格" if shared else "台灣三星完整規格"
    hint = '<p class="notice">官網可能展示同一面板的其他組合。底座或移動架以門市組合為準。</p>' if shared else ""
    caption = "<figcaption>組合示意</figcaption>" if group=="followme" else ""
    res = p["rows"][1].splitlines()
    peak = p["rows"][2].splitlines()[0] if group in {"oled","ips","curve"} else res[1].split("·")[0].strip()
    if peak=="DP／HDMI":
        peak = p["rows"][2].splitlines()[1]
    return f'''<article class="product" id="{key}" data-key="{key}" data-family="{group}" tabindex="-1" aria-labelledby="{key}-title">
      <header class="product-cover"><figure>{image(p)}{caption}</figure>
        <div class="identity"><p class="family">{e(groups[group])}</p><h3 id="{key}-title">{e(name)}</h3>
          <span class="model">{e(model)}</span><p class="key-spec">{e(res[0])}<br>{e(peak)}</p>{price(p)}</div>
      </header>
      <div class="product-body"><p class="suitable"><strong>適合</strong>{e(fit)}</p>
        <section class="ask"><h4>開場這樣問</h4><p>{e(question)}</p></section>
        <h4>三個賣點</h4><ol class="points">{lines}</ol>
        <section class="demo"><h4>現場示範</h4><p>{e(demo)}</p></section>{hint}
        <details><summary>展開重點規格</summary><dl class="specs">{spec_rows(p)}</dl></details>
        <div class="actions"><a href="{e(p["url"])}" target="_blank" rel="noopener">{source} ↗</a>
          <button type="button" class="copy" data-model="{e(model)}">複製型號</button></div>
      </div></article>'''

def quick_needs():
    panels = []
    for heading, text, keys in content["needs"]:
        links = "".join(f'<a href="#{key}">{e(title(by_id[key]))} <span aria-hidden="true">↗</span></a>' for key in keys)
        panels.append(f'<div class="scenario"><h3>{e(heading)}</h3><p>{e(text)}</p><div>{links}</div></div>')
    return "".join(panels)

quiz = []
for prompt, keys, answer, reason in content["questions"]:
    assert len(keys)==len(set(keys))==3 and 0<=answer<len(keys)
    quiz.append({"prompt":prompt,"choices":[{"name":title(by_id[k]),"id":k} for k in keys],"answer":answer,"reason":reason})

filters = "".join(f'<button type="button" data-group="{key}" aria-pressed="false">{e(value)}</button>' for key,value in groups.items())
terms = "".join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k,v in content["glossary"])
quiz_json = json.dumps({"questions":quiz},ensure_ascii=False).replace("<",chr(92)+"u003c")
html = f'''<!doctype html>
<html lang="zh-Hant-TW">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="順發各門市共用的三星螢幕教育講義，包含14個銷售配置、規格速查、現場示範與情境練習。">
<meta name="robots" content="noindex,follow"><meta name="theme-color" content="#142f33">
<link rel="icon" href="data:,"><link rel="stylesheet" href="guide.css"><script src="guide.js" defer></script>
<title>順發通路｜三星螢幕門市講義</title></head>
<body id="top">
<a href="#catalog" class="skip">跳至機款總覽</a>
<header class="site-header"><div class="wrap topbar"><a class="brand" href="#top">順發通路<span>門市講義</span></a>
<nav aria-label="講義導覽"><a href="#catalog">機款</a><a href="#needs">選機</a><a href="#practice">練習</a></nav></div></header>
<main>
<section class="hero"><div class="wrap hero-grid"><div class="hero-copy">
<h1>三星螢幕<br>門市銷售講義</h1><p>從顧客需求出發，快速找到適合的機款、推薦話術與現場示範。</p>
<div class="hero-actions"><a class="primary" href="#catalog">查詢14個銷售配置 ↓</a><a class="secondary" href="#needs">依需求選機</a></div></div>
<a class="hero-product" href="#oled_g8_32" aria-label="查看OLED G8 32吋講義">{image(by_id["oled_g8_32"],hero=True)}
<span><strong>Odyssey OLED G8</strong><small>32吋・4K UHD・240Hz</small></span></a></div></section>
<section class="wrap section" id="catalog" aria-labelledby="catalog-title">
<div class="section-heading"><div><h2 id="catalog-title">機款速查</h2><p>依型號或系列找到講義。同一螢幕搭配不同底座時，分開列出。</p></div></div>
<div class="catalog-tools"><label class="search"><span>搜尋機款</span><input id="query" type="search" placeholder="輸入型號、系列或尺寸" autocomplete="off"></label>
<div class="filters" role="group" aria-label="依系列篩選"><button type="button" data-group="" aria-pressed="true">全部</button>{filters}</div></div>
<div class="results-note" id="results" role="status">14個銷售配置</div>
<ul class="tiles" aria-label="機款總覽">{''.join(tile(p) for p in specs)}</ul>
<div class="empty" id="empty" hidden><p>找不到符合的機款。</p><button id="reset-filter" type="button">清除篩選</button></div>
</section>
<section class="wrap section" id="needs" aria-labelledby="needs-title">
<div class="section-heading"><div><h2 id="needs-title">依顧客需求選機</h2><p>先問用途、桌面空間或是否需要移動，再帶顧客看實機。</p></div></div>
<div class="scenarios">{quick_needs()}</div></section>
<section class="wrap section" id="lessons" aria-labelledby="lessons-title">
<div class="section-heading"><div><h2 id="lessons-title">機款講解</h2><p>建議售價取自三星上市公告。實售、配件與活動以各門市現場為準。</p></div><a class="text-link" href="#catalog">回速查 ↑</a></div>
<div class="card-grid">{''.join(card(p) for p in specs)}</div></section>
<section class="practice section" id="practice" aria-labelledby="practice-title">
<div class="wrap practice-layout"><div><h2 id="practice-title">門市情境練習</h2><p>用顧客的需求選機，即時看解析。共10題，作答留在自己的瀏覽器。</p></div>
<div id="quiz" class="quiz" aria-label="情境練習"><noscript>請開啟JavaScript使用情境練習。</noscript>
<div class="quiz-top"><span id="quiz-progress"></span><span id="quiz-score"></span></div>
<h3 id="quiz-question" tabindex="-1"></h3><div id="quiz-choices" class="choices"></div><p id="quiz-feedback" role="status"></p>
<div class="quiz-actions"><a id="quiz-review" hidden>看對應機款 ↗</a><button type="button" id="quiz-next" class="primary" hidden>下一題</button>
<button type="button" id="quiz-reset">重新作答</button></div></div></div></section>
<section class="wrap section" id="terms"><div class="section-heading"><h2>門市規格小抄</h2></div><dl class="terms">{terms}</dl></section>
</main><footer><div class="wrap footer-inner"><div><strong>順發通路｜三星螢幕門市講義</strong>
<p>適用各門市教育訓練。產品及規格來源為台灣三星，FollowMe為對應組合示意。</p>
<p>教材更新 {e(content['release'].replace('-', '/'))}</p></div><a href="#top" class="text-link">回到頂端 ↑</a></div></footer>
<p id="announcement" class="sr-only" role="status"></p><script id="guide-data" type="application/json">{quiz_json}</script>
</body></html>'''
assert not re.search(r"(?<!2K )\bQHD\b", re.sub(r"https?://[^\s\"<>]+", "", html))
(DOCS/"index.html").write_text(html,encoding="utf-8",newline="\n")
print(f"built {len(specs)} configurations and {len(quiz)} questions")
