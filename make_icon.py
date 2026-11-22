import os, sys
from PIL import Image, ImageDraw
src, res = sys.argv[1:3]
im = Image.open(src).convert("RGB")
cl = im.point(lambda v: 0 if v < 14 else min(255, int((v - 14) * 255 / 241)))
m = cl.convert("L").point(lambda v: 255 if v > 40 else 0)
x0, y0, x1, y1 = m.getbbox()
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
w = m.width
r = max([((i % w - cx) ** 2 + (i // w - cy) ** 2) ** .5 for i, v in enumerate(m.tobytes()) if v] + [1.0])

def render(n, f):
    s = f * n / r
    a = cl.resize((max(1, round(im.width * s)),) * 2, Image.LANCZOS)
    c = Image.new("RGB", (n, n), (0, 0, 0))
    c.paste(a, (round(n / 2 - cx * s), round(n / 2 - cy * s)))
    return c

def circle(img):
    n = img.width
    b = Image.new("L", (n * 4, n * 4), 0)
    ImageDraw.Draw(b).ellipse((0, 0, n * 4 - 1, n * 4 - 1), fill=255)
    o = img.convert("RGBA")
    o.putalpha(b.resize((n, n), Image.LANCZOS))
    return o

def save(img, d, name):
    os.makedirs(res + "/mipmap-" + d, exist_ok=True)
    img.save(res + "/mipmap-" + d + "/" + name + ".png")

for d, k in {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}.items():
    n = round(108 * k)
    fg = render(n, 0.31)
    save(fg.convert("RGBA"), d, "niche_icon_foreground")
    al = fg.convert("L").point(lambda v: min(255, int(max(0, v - 20) * 1.7)))
    mo = Image.new("RGBA", (n, n), (255, 255, 255, 0))
    mo.putalpha(al)
    save(mo, d, "niche_icon_monochrome")

for d, k in {"ldpi": .75, "mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}.items():
    full = render(round(48 * k), 0.42)
    save(full.convert("RGBA"), d, "ic_launcher")
    save(circle(full), d, "ic_launcher_round")

open(res + "/values/niche_colors.xml", "w").write(
    '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    '    <color name="niche_icon_background">#000000</color>\n</resources>\n')
ad = ('<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
      '  <background android:drawable="@color/niche_icon_background"/>\n'
      '  <foreground android:drawable="@mipmap/niche_icon_foreground"/>\n'
      '  <monochrome android:drawable="@mipmap/niche_icon_monochrome"/>\n</adaptive-icon>\n')
for f in ("ic_launcher", "ic_launcher_round"):
    open(res + "/mipmap-anydpi-v26/" + f + ".xml", "w").write(ad)
print("icons done")
