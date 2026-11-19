"""Run the same Chrome checks on a local build or the deployed Pages URL."""
from argparse import ArgumentParser
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.request import urlopen
import json
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parent
parser = ArgumentParser()
parser.add_argument("--url")
args = parser.parse_args()
DOCS = ROOT / "docs"
mode = "live" if args.url else "local"
out = ROOT / "qa" / mode
out.mkdir(parents=True, exist_ok=True)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DOCS, **kw)
    def log_message(self, *_):
        pass

server = None
url = args.url
if not url:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/"

def journey(browser, width, height):
    context = browser.new_context(viewport={"width": width, "height": height}, is_mobile=width<500, has_touch=width<500)
    context.grant_permissions(["clipboard-read", "clipboard-write"])
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda exc:errors.append(str(exc)))
    page.on("response", lambda resp:errors.append(f"{resp.status} {resp.url}") if resp.status>=400 else None)
    page.on("requestfailed", lambda req:errors.append(f"{req.failure} {req.url}") if not req.is_navigation_request() else None)
    result = page.goto(url, wait_until="networkidle")
    assert result and result.ok
    expect(page.get_by_role("heading",level=1)).to_contain_text("門市銷售講義")
    expect(page.locator("article.product")).to_have_count(14)
    expect(page.locator(".product .points li")).to_have_count(42)
    expect(page.locator(".scenario")).to_have_count(6)
    page.screenshot(path=out/f"{width}-home.png",animations="disabled")
    page.locator(".hero-actions .primary").click()
    assert page.evaluate("location.hash")=="#catalog"
    assert page.evaluate("document.documentElement.scrollWidth")<=width
    search = page.get_by_role("searchbox")
    search.fill("s32fm703uc")
    expect(page.locator("#results")).to_have_text("3個銷售配置")
    assert page.locator(".product:visible").evaluate_all("(nodes) => nodes.map(n=>n.id)") == [
        "followme_regular_32","followme_pro_32","m7_desktop_white"]
    page.screenshot(path=out/f"{width}-search.png",animations="disabled")
    page.locator(".tile:visible a[href='#followme_pro_32']").click()
    pro = page.locator("#followme_pro_32")
    expect(pro).to_be_focused()
    assert pro.bounding_box()["y"] >= page.locator(".site-header").bounding_box()["height"]
    pro.locator("summary").click()
    expect(pro.get_by_text("氣壓升降 188 mm",exact=False)).to_be_visible()
    expect(pro.get_by_role("link",name="查看台灣三星面板規格 ↗")).to_have_attribute("href", "https://www.samsung.com/tw/monitors/smart/smart-monitor-m7-32-inch-smart-tv-apps-4k-uhd-ls32fm703ucxzw/")
    page.screenshot(path=out/f"{width}-product.png",animations="disabled")
    pro.get_by_role("button",name="複製型號").click()
    expect(pro.get_by_role("button",name="已複製")).to_be_visible()
    assert page.evaluate("navigator.clipboard.readText()") == "S32FM703UC"
    page.locator(".site-header a[href='#catalog']").click()
    search.fill("不存在型號")
    expect(page.get_by_text("找不到符合的機款。")).to_be_visible()
    page.get_by_role("button",name="清除篩選").click()
    expect(search).to_be_focused()
    for title,count in [("OLED電競",2),("IPS平面電競",4),("曲面電競",2),("FollowMe移動組",3),("M7桌上型",2),("日常文書",1)]:
        btn = page.get_by_role("button",name=title,exact=True)
        btn.click()
        expect(btn).to_have_attribute("aria-pressed","true")
        expect(page.locator(".tile:visible")).to_have_count(count)
    page.locator(".site-header a[href='#needs']").click()
    page.locator("#needs a[href='#curve_g5_32']").click()
    expect(page.locator("#curve_g5_32")).to_be_focused()
    expect(page.locator("#results")).to_have_text("14個銷售配置")
    page.locator(".site-header a[href='#practice']").click()
    page.screenshot(path=out/f"{width}-quiz.png",animations="disabled")
    for index, choice in enumerate([1,0,1,1,0,2,1,0,2,0]):
        expect(page.locator("#quiz-progress")).to_have_text(f"第{index+1}題，共10題")
        page.locator("#quiz-choices button").nth(choice).click()
        expect(page.locator("#quiz-feedback")).not_to_be_empty()
        page.locator("#quiz-next").click()
    expect(page.locator("#quiz-question")).to_have_text("本次答對9／10題")
    page.get_by_role("button",name="重新作答").click()
    expect(page.locator("#quiz-progress")).to_have_text("第1題，共10題")
    images = page.locator(".product img")
    assert images.count()==14
    for image in images.all():
        image.scroll_into_view_if_needed()
        page.wait_for_function("image => image.complete && image.naturalWidth>0", arg=image.element_handle())
    assert page.evaluate("document.documentElement.scrollWidth")<=width
    assert not errors, errors
    context.close()
    return {"viewport":[width,height],"products":14,"menu_filters":6,"quiz_completed":True,"all_images_loaded":True,"errors":errors}

try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        report = [journey(browser,w,h) for w,h in [(390,844),(1280,720),(1440,900)]]
        browser.close()
    if args.url:
        for file in DOCS.rglob("*"):
            if file.is_file() and file.name != ".nojekyll":
                remote = url.rstrip("/") + "/" + file.relative_to(DOCS).as_posix()
                with urlopen(remote, timeout=25) as response:
                    assert sha256(response.read()).digest()==sha256(file.read_bytes()).digest(), remote
    (out/"browser.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
finally:
    if server:
        server.shutdown()
