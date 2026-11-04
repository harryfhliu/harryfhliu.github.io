#!/usr/bin/env python3
"""
Jekyll -> Astro 文章迁移脚本
- 源：/Users/harry/Documents/GitHub/harryfhliu.github.io/_posts/*.md
- 目标：/Users/harry/Documents/GitHub/harry-blog-astro/src/content/blog/<slug>.md

规则：
1. 日期以 front matter 的 date 为权威（文件名日期仅兜底）。
2. 无 front matter 的文章（1 篇）从正文标题/报告日期兜底。
3. slug 做 URL 安全清理，保留中文；同时写回 legacySlug 供 SEO 重定向。
4. 正文原样保留（含 $$ 数学公式、GFM 表格）。
"""
import os
import re
import glob
import shutil
import yaml

SRC = "/Users/harry/Documents/GitHub/harryfhliu.github.io/_posts"
DST = "/Users/harry/Documents/GitHub/harry-blog-astro/src/content/blog"

# 无 front matter 兜底表：文件名 -> (date, title, tags)
NO_FM_FALLBACK = {
    "2026年中国地热能领域投资风向报告.md": {
        "date": "2026-03-31",
        "title": "2026年中国地热能领域投资风向报告",
        "tags": ["地热能", "投资", "行业报告"],
        "header-img": "img/post-bg-jade-geothermal.jpg",
    }
}


def slugify(text: str) -> str:
    """URL 安全 slug：保留中文/字母/数字，其余转连字符，去首尾连字符，压缩连续连字符。"""
    # 常见书名号/括号/方括号/引号 直接删除
    text = re.sub(r"[《》「」『』【】\[\]（）()“”\"'？?！!，,。：:、]", "", text)
    # 空格、间隔号、℃、· 等转连字符
    text = re.sub(r"[\s·℃、/\\]+", "-", text)
    # 其余非中文非字母非数字非连字符，转连字符
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text


def parse_front_matter(text: str):
    """返回 (front_matter_dict_or_None, body)。无 front matter 返回 (None, text)。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None, text
    fm = yaml.safe_load(m.group(1))
    return fm, text[m.end():]


def format_date(d) -> str:
    """统一为 YYYY-MM-DD。"""
    if isinstance(d, str):
        d = d.strip()
        m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", d)
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        return d
    # datetime/date 对象
    return f"{d.year:04d}-{d.month:02d}-{d.day:02d}"


def build_front(fm: dict) -> list:
    """由 front matter 生成 Astro YAML 头。返回行列表。"""
    lines = ["---"]
    lines.append(f'title: "{str(fm.get("title", "")).strip()}"')
    if fm.get("subtitle"):
        lines.append(f'subtitle: "{str(fm["subtitle"]).strip()}"')
    lines.append(f'date: {format_date(fm.get("date", "1970-01-01"))}')
    lines.append(f'author: "{str(fm.get("author", "沐杰")).strip()}"')
    if fm.get("header-img"):
        lines.append(f'header-img: "{str(fm["header-img"]).strip()}"')
    tags = fm.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    if tags:
        lines.append("tags:")
        for t in tags:
            lines.append(f'  - "{str(t).strip()}"')
    lines.append(f'catalog: {"true" if fm.get("catalog") else "false"}')
    lines.append("---")
    return lines


def main():
    os.makedirs(DST, exist_ok=True)
    # 清空旧迁移结果（幂等）
    for f in glob.glob(os.path.join(DST, "*.md")):
        os.remove(f)

    posts = sorted(glob.glob(os.path.join(SRC, "*.md")))
    ok = 0
    no_fm_count = 0
    report = []

    for path in posts:
        fname = os.path.basename(path)
        text = open(path, encoding="utf-8").read()

        # 无 front matter 兜底
        if fname in NO_FM_FALLBACK:
            fb = NO_FM_FALLBACK[fname]
            fm = fb
            body = text
            no_fm_count += 1
        else:
            fm, body = parse_front_matter(text)
            if fm is None:
                # 未在兜底表里但仍无 front matter：从文件名推断日期
                m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", fname)
                date = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else "1970-01-01"
                # 标题 = 文件名去日期前缀
                title = re.sub(r"^\d{4}-\d{2}-\d{2}-?", "", fname).replace(".md", "")
                fm = {"date": date, "title": title, "tags": []}
                body = text
                no_fm_count += 1
                report.append(f"  [兜底] {fname} 无 front matter，日期推断为 {date}")

        date = format_date(fm.get("date", "1970-01-01"))
        title = str(fm.get("title", "")).strip()
        slug = slugify(title) if title else slugify(fname.replace(".md", ""))

        # 确保 slug 唯一（同标题/同日可能重复）
        # 文件名去日期前缀作为 legacySlug 参考（旧站 slug 规则）
        legacy = slugify(re.sub(r"^\d{4}-\d{2}-\d{2}-?", "", fname).replace(".md", ""))

        head = build_front(fm)
        # 追加 legacySlug（在 --- 之后、正文之前的位置，插入到 front matter 内）
        head.insert(-1, f'legacySlug: "{legacy}"')

        out = os.path.join(DST, f"{slug}.md")
        # 若 slug 重复，加日期后缀
        if os.path.exists(out):
            out = os.path.join(DST, f"{slug}-{date}.md")
            report.append(f"  [重名] {fname} -> {os.path.basename(out)}")

        content = "\n".join(head) + "\n\n" + body.lstrip("\n")
        open(out, "w", encoding="utf-8").write(content)
        ok += 1

    print(f"迁移完成：{ok} 篇 -> {DST}")
    print(f"其中无 front matter（兜底）：{no_fm_count} 篇")
    if report:
        print("\n处理报告：")
        for r in report:
            print(r)

    # 统计
    total = len(glob.glob(os.path.join(DST, "*.md")))
    print(f"\n目标目录现有 {total} 篇")


if __name__ == "__main__":
    main()
