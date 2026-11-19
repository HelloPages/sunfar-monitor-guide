"""Import public product specs and resize approved V12 product images."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from PIL import Image, ImageChops
import json
import re

ROOT = Path(__file__).resolve().parent
parser = ArgumentParser()
parser.add_argument("source", type=Path, help="V12 print project folder")
source = parser.parse_args().source
products = json.loads((source / "products.json").read_text(encoding="utf-8"))["products"]
manifest = {p["item_id"]: p for p in json.loads((source / "assets/manifest.json").read_text(encoding="utf-8"))}
images = ROOT / "docs/images"
images.mkdir(parents=True, exist_ok=True)
specs, origins = [], ["# 公開商品圖來源\n"]
for p in products:
    key = p["item_id"]
    file = source / "assets" / f"{key}.png"
    assert sha256(file.read_bytes()).hexdigest() == manifest[key]["sha256"], key
    with Image.open(file) as src:
        pic = src.convert("RGBA")
        alpha = pic.getchannel("A")
        if alpha.getextrema()[0] == 0:
            signal = alpha
        else:
            rgb = pic.convert("RGB")
            signal = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).convert("L")
        bounds = signal.point(lambda v: 255 if v > 25 else 0).getbbox()
        if bounds:
            left, top, right, bottom = bounds
            pad = round(max(right-left,bottom-top)*.04)
            pic = pic.crop((max(0,left-pad),max(0,top-pad),min(pic.width,right+pad),min(pic.height,bottom+pad)))
        pic.thumbnail((790,670), Image.Resampling.LANCZOS)
        pic.save(images / f"{key}.webp", quality=88, method=6)
    entry = {name: p[name] for name in ("item_id","model","group","inches","url")}
    entry["rows"] = [re.sub(r"(?<!2K )\bQHD\b", "2K QHD", row) for row in p["rows"]]
    specs.append(entry)
    origin = manifest[key]["origin"]
    provenance = f"[原始商品照]({origin})" if origin.startswith("https://images.samsung.com/") else "V12核對商品照"
    if p["group"] == "followme":
        provenance = "V12對應移動架3D組合示意"
    origins.append(f"- {key}／{p['model']}：{provenance}。[對應面板或產品]({p['url']})")
(ROOT/"specs.json").write_text(json.dumps(specs,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"ASSETS.md").write_text("\n".join(origins)+"\n",encoding="utf-8")
print(f"{len(specs)}組：{sum(p.stat().st_size for p in images.glob('*.webp')):,} bytes")
