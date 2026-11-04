#!/usr/bin/env python3
"""生成「如是我闻」站标 favicon（朱砂印章 + 金文「我」字）。

字形源：scripts/43_EFBE.svg —— 金文「我」字，从戈从𠂉，本义为带齿的
戈类兵器：左侧锯齿状竖排部件，右侧上翘的戈援与长柄底座。笔画浑厚，
近金文铸刻的墨拓质感，比此前的描边大篆更写实可辨。

形制：朱砂印章（白文印），红底白字，取金文朱拓之意，与墨韵东方主题
（--gold: #b03a2e）呼应。字形中部镂空留红，模拟篆刻的「留红」效果。

生成：favicon.svg + favicon-{16,32,192,512}.png + favicon.ico
      + apple-touch-icon.png(180)
"""
from PIL import Image, ImageDraw
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "scripts", "43_EFBE.svg")
PUBLIC = os.path.join(BASE, "public")

RED = (0xB0, 0x3A, 0x2E, 255)   # 朱砂红 #b03a2e
INK = (0xF7, 0xF2, 0xE6, 255)   # 米白 #f7f2e6
RED_HEX = "#b03a2e"
INK_HEX = "#f7f2e6"

VIEW = 64  # SVG viewBox 边长


def tokenize(d):
    return re.findall(r"[A-Za-z]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", d)


def parse_subpaths(d):
    """解析 SVG path d，返回子路径点集列表（含三次贝塞尔采样）。"""
    tokens = tokenize(d)
    subpaths = []
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    pts = []
    i = 0
    cmd = None
    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            cmd = t
            i += 1
            continue
        if cmd is None:
            i += 1
            continue
        c = cmd
        if c in "Mm":
            x = float(tokens[i]); y = float(tokens[i + 1]); i += 2
            cur = (cur[0] + x, cur[1] + y) if c == "m" else (x, y)
            if pts:
                subpaths.append(pts)
            pts = [cur]
            start = cur
            cmd = "L" if c == "M" else "l"
        elif c in "Ll":
            x = float(tokens[i]); y = float(tokens[i + 1]); i += 2
            cur = (cur[0] + x, cur[1] + y) if c == "l" else (x, y)
            pts.append(cur)
        elif c in "Hh":
            x = float(tokens[i]); i += 1
            cur = (cur[0] + x, cur[1]) if c == "h" else (x, cur[1])
            pts.append(cur)
        elif c in "Vv":
            y = float(tokens[i]); i += 1
            cur = (cur[0], cur[1] + y) if c == "v" else (cur[0], y)
            pts.append(cur)
        elif c in "Cc":
            x1 = float(tokens[i]); y1 = float(tokens[i + 1])
            x2 = float(tokens[i + 2]); y2 = float(tokens[i + 3])
            x = float(tokens[i + 4]); y = float(tokens[i + 5]); i += 6
            if c == "c":
                p1 = (cur[0] + x1, cur[1] + y1)
                p2 = (cur[0] + x2, cur[1] + y2)
                cur = (cur[0] + x, cur[1] + y)
            else:
                p1 = (x1, y1)
                p2 = (x2, y2)
                cur = (x, y)
            p0 = pts[-1]
            N = 16
            for k in range(1, N + 1):
                t = k / N
                mt = 1 - t
                pts.append((
                    mt ** 3 * p0[0] + 3 * mt ** 2 * t * p1[0]
                    + 3 * mt * t ** 2 * p2[0] + t ** 3 * cur[0],
                    mt ** 3 * p0[1] + 3 * mt ** 2 * t * p1[1]
                    + 3 * mt * t ** 2 * p2[1] + t ** 3 * cur[1],
                ))
        elif c in "Zz":
            pts.append(start)
            subpaths.append(pts)
            pts = []
            cur = start
            i += 1
        else:
            i += 1
    if pts:
        subpaths.append(pts)
    return subpaths


def main():
    svg = open(SRC).read()
    # 提取主体「我」字 path（fill 为近黑 #010104 的那条）
    found = re.findall(r'<path d="([^"]+)" fill="([^"]+)"', svg)
    main_d = next(d for d, f in found if f.lower() == "#010104")

    # 拆分外轮廓与内部镂空两个子路径的 d（保持原始贝塞尔精度）
    parts = re.findall(r"[Mm][^Mm]*?[Zz]", main_d)
    if len(parts) < 1:
        raise SystemExit("未找到子路径")
    outer_d = parts[0]
    inner_d = parts[1] if len(parts) > 1 else None

    # 计算字形包围盒（用采样点）
    subpaths = parse_subpaths(main_d)
    xs = [p[0] for sp in subpaths for p in sp]
    ys = [p[1] for sp in subpaths for p in sp]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    h = maxy - miny
    cx = (minx + maxx) / 2.0
    cy = (miny + maxy) / 2.0

    # 字形高度定 40/64，居中放入印章框
    target_h = 40.0
    s = target_h / h
    tx = VIEW / 2.0 - cx * s
    ty = VIEW / 2.0 - cy * s

    # ---- 1. 生成 SVG ----
    inner = f'<path d="{inner_d}" fill="{RED_HEX}"/>' if inner_d else ""
    svg_out = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW} {VIEW}" width="{VIEW}" height="{VIEW}">
  <!--
    「如是我闻」站标
    字形：金文「我」——从戈从𠂉，本义为带齿的戈类兵器，左侧锯齿竖排 +
          右侧戈援与长柄底座，笔画浑厚近金文墨拓，写实可辨。
    形制：朱砂印章（白文印），红底白字，字中镂空留红。
  -->
  <rect x="2" y="2" width="60" height="60" rx="14" fill="{RED_HEX}"/>
  <g transform="translate({tx:.4f} {ty:.4f}) scale({s:.6f})">
    <path d="{outer_d}" fill="{INK_HEX}"/>
    {inner}
  </g>
</svg>
'''
    with open(os.path.join(PUBLIC, "favicon.svg"), "w") as f:
        f.write(svg_out)
    print("OK  favicon.svg")

    # ---- 2. 生成 PNG / ICO ----
    def draw(size, rounded=True):
        sc = size / float(VIEW)
        if rounded:
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            dr = ImageDraw.Draw(img)
            dr.rounded_rectangle(
                [2 * sc, 2 * sc, 62 * sc, 62 * sc], radius=14 * sc, fill=RED)
        else:
            img = Image.new("RGBA", (size, size), RED)  # 满幅红底
            dr = ImageDraw.Draw(img)

        def map_pt(p):
            return ((p[0] * s + tx) * sc, (p[1] * s + ty) * sc)

        dr.polygon([map_pt(p) for p in subpaths[0]], fill=INK)
        if len(subpaths) > 1:
            dr.polygon([map_pt(p) for p in subpaths[1]], fill=RED)
        return img

    targets = {
        "favicon-16.png": (16, True),
        "favicon-32.png": (32, True),
        "favicon-192.png": (192, True),
        "favicon-512.png": (512, True),
        "apple-touch-icon.png": (180, False),
    }
    for name, (size, rounded) in targets.items():
        draw(size, rounded).save(os.path.join(PUBLIC, name))
        print(f"OK  {name}  ({size}x{size})")

    # 多尺寸 ICO（兼容旧浏览器 / Windows）
    sizes = [(16, 16), (32, 32)]
    frames = [draw(sz[0]) for sz in sizes]
    frames[0].save(
        os.path.join(PUBLIC, "favicon.ico"),
        sizes=sizes,
        append_images=frames[1:],
    )
    print("OK  favicon.ico  (16+32)")


if __name__ == "__main__":
    main()
