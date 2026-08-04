#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stage.py — 把语雀导出的 markdown 暂存进 Hugo 内容树。

用法
----
    ./scripts/stage.py <input.md> [slug]      # 处理单个文件
    ./scripts/stage.py <dir>                   # 批量处理目录下所有 *.md（递归）
    ./scripts/stage.py <input.md> --draft      # 以草稿发布(draft: true)
    ./scripts/stage.py <input.md> -n           # dry-run，只打印计划不写盘

它做三件事
----------
1. 补 Hugo front matter：若无则注入。title 取正文第一个一级标题，否则取文件名；
   date 取已有 front matter 的 date，否则取文件 mtime（Asia/Shanghai）。
2. 图片本地化：
   - 远程图（http/https，含语雀 cdn.nlark.com）→ 下载到文章目录 images/，改写为相对路径；
   - 本地图（源文件旁边的 assets/xxx、images/xxx 等相对引用）→ 复制进文章目录 images/，改写；
   - 下载/复制失败 → 原样保留链接并告警（不静默吞掉）。
3. 输出为 Hugo page bundle：content/posts/<slug>/index.md (+ images/)。

依赖：Python 3.8+，仅标准库。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import re
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# 仓库根 = 本文件所在 scripts/ 的上一级
REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "content" / "posts"
TZ = _dt.timezone(_dt.timedelta(hours=8))  # Asia/Shanghai

# Markdown 图片语法: ![alt](url "optional title")
MD_IMG_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
# HTML <img src="..."> —— 非贪婪，且要求 src 前是空白，避免误匹配 data-src 等
HTML_IMG_RE = re.compile(r'<img[^>]*?\ssrc=["\']([^"\']+)["\']', re.IGNORECASE)
# 一级标题
H1_RE = re.compile(r'^#\s+(.+?)\s*$', re.MULTILINE)

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico", ".avif"}


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def slugify(text: str) -> str:
    """把标题/文件名转成 URL 安全的 slug。中文字符保留（Hugo 接受，浏览器会百分号编码）。"""
    text = text.strip()
    # 只保留「字母/数字/下划线/连字符」，其余（含全角标点、空格、路径符）→ -
    text = re.sub(r"[^\w\-]+", "-", text, flags=re.UNICODE)
    text = re.sub(r"-{2,}", "-", text)
    text = text.strip("-_.")
    return text or "untitled"


def safe_filename(name: str, ext: str, seen: set[str]) -> str:
    """生成不冲突的文件名。"""
    stem = slugify(name) or "image"
    stem = re.sub(r"[^\w\-.]", "-", stem) or "image"
    # 截断，避免过长
    stem = stem[:60].strip("-_.")
    candidate = f"{stem}{ext.lower()}"
    if candidate not in seen:
        seen.add(candidate)
        return candidate
    n = 1
    while f"{stem}-{n}{ext.lower()}" in seen:
        n += 1
    candidate = f"{stem}-{n}{ext.lower()}"
    seen.add(candidate)
    return candidate


def parse_front_matter(text: str) -> tuple[dict, str, bool]:
    """
    返回 (已有FM字典, 正文, 是否存在FM)。
    只解析轻量 YAML（key: value、列表用 [a, b]）；够用即可。
    """
    if not text.startswith("---"):
        return {}, text, False
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text, False
    fm_raw = parts[1].strip("\n")
    body = parts[2].lstrip("\n") if len(parts) == 3 else ""
    fm: dict = {}
    for line in fm_raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^([A-Za-z0-9_]+)\s*:\s*(.*)$', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        # 去引号
        if val and val[0] in "\"'" and val[-1] == val[0]:
            val = val[1:-1]
        if val.lower() in ("true", "false"):
            fm[key] = val.lower() == "true"
        elif val.startswith("[") and val.endswith("]"):
            # flow list: [a, b, c]
            inner = val[1:-1].strip()
            items = [x.strip().strip("\"'") for x in inner.split(",")] if inner else []
            fm[key] = [x for x in items if x]
        else:
            fm[key] = val
    return fm, body, True


def build_front_matter(fm: dict, title: str, date_str: str, draft: bool) -> str:
    """生成/补全 front matter 文本。"""
    fm.setdefault("title", title)
    fm.setdefault("date", date_str)
    fm["draft"] = draft
    fm.setdefault("description", "")
    fm.setdefault("tags", [])
    fm.setdefault("categories", [])
    fm["ShowToc"] = True
    fm["TocOpen"] = True

    def fmt_val(k, v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, list):
            if not v:
                return "[]"
            return "[" + ", ".join(str(x) for x in v) + "]"
        s = str(v)
        # 含特殊字符则加引号
        if s and re.search(r'[:#\[\]{}"&]', s):
            return '"' + s.replace('"', '\\"') + '"'
        return s

    order = ["title", "date", "draft", "description", "tags", "categories", "ShowToc", "TocOpen"]
    lines = ["---"]
    for k in order:
        if k in fm:
            lines.append(f"{k}: {fmt_val(k, fm[k])}")
    # 其余原有键追加在后
    for k, v in fm.items():
        if k in order:
            continue
        lines.append(f"{k}: {fmt_val(k, v)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def ext_from_url(url: str, content_type: str | None = None) -> str:
    """从 URL 或 content-type 推断图片扩展名。"""
    path = urllib.parse.urlparse(url).path
    ext = Path(path).suffix.lower()
    if ext in IMAGE_EXTS:
        return ext
    # content-type 兜底
    ct_map = {
        "image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif",
        "image/webp": ".webp", "image/svg+xml": ".svg", "image/bmp": ".bmp",
        "image/avif": ".avif", "image/x-icon": ".ico",
    }
    if content_type:
        for k, v in ct_map.items():
            if k in content_type.lower():
                return v
    return ".png"  # 默认


def fetch_remote(url: str, dest_dir: Path, seen: set[str]) -> str | None:
    """下载远程图片到 dest_dir/images，返回新的相对路径；失败/非图片返回 None。"""
    data: bytes | None = None
    ctype = ""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 stage.py"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
            ctype = resp.headers.get("Content-Type", "")
            # 语雀/部分 CDN 需要 referer，疑似非图片时带 referer 重试一次
            if not data or len(data) < 64 or "text" in ctype.lower() or "html" in ctype.lower():
                raise IOError("suspected non-image body")
    except Exception:
        # 带 Referer 重试（语雀 CDN 常见）
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 stage.py",
                    "Referer": "https://www.yuque.com/",
                },
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                ctype = resp.headers.get("Content-Type", "")
        except Exception as e:
            log(f"    ⚠ 下载失败（保留原链接）: {url}  ({e})")
            return None

    # 重试后仍要校验：HTML/文本（如过期的 CDN 登录页，HTTP 200 但 body 是 HTML）不能当图片
    if not data or len(data) < 64 or "text" in ctype.lower() or "html" in ctype.lower():
        log(f"    ⚠ 响应不是图片（保留原链接）: {url}  (type={ctype or '?'})")
        return None

    parsed = urllib.parse.urlparse(url)
    base_name = Path(parsed.path).name or hashlib.md5(url.encode()).hexdigest()[:12]
    ext = ext_from_url(url, ctype)
    images_dir = dest_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    fname = safe_filename(Path(base_name).stem or "image", ext, seen)
    (images_dir / fname).write_bytes(data)
    return f"images/{fname}"


def copy_local(src_path: Path, dest_dir: Path, seen: set[str]) -> str | None:
    """把本地图片复制进文章目录 images/，返回新相对路径；文件不存在返回 None。"""
    if not src_path.is_file():
        return None
    ext = src_path.suffix.lower() or ".png"
    images_dir = dest_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    fname = safe_filename(src_path.stem, ext, seen)
    shutil.copy2(src_path, images_dir / fname)
    return f"images/{fname}"


def localize_images(body: str, src_dir: Path, dest_dir: Path) -> str:
    """扫描正文里所有图片引用，下载/复制到 page bundle，改写链接。"""
    seen: set[str] = set()
    src_root = src_dir.resolve()
    repo_root = REPO_ROOT.resolve()

    def rewrite(url: str) -> str:
        if url.startswith("data:"):
            return url  # 内嵌 base64，不动
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme in ("http", "https"):
            new = fetch_remote(url, dest_dir, seen)
            return new if new else url
        # 相对/绝对本地路径 —— 必须落在源文件目录或仓库根内，防止路径穿越读取任意文件
        local = url.split("?")[0].split("#")[0]
        if local.startswith("/"):
            candidate = (REPO_ROOT / local.lstrip("/")).resolve()
            allowed = repo_root
        else:
            candidate = (src_dir / local).resolve()
            allowed = src_root
        try:
            candidate.relative_to(allowed)  # 不在允许范围内 → ValueError
        except ValueError:
            log(f"    ⚠ 路径越界，拒绝读取（保留原链接）: {url}")
            return url
        new = copy_local(candidate, dest_dir, seen)
        if not new:
            log(f"    ⚠ 本地图片缺失（保留原链接）: {url}")
            return url
        return new

    def md_repl(m: re.Match) -> str:
        alt, url = m.group(1), m.group(2)
        return f"![{alt}]({rewrite(url)})"

    def html_repl(m: re.Match) -> str:
        url = m.group(1)
        return m.group(0).replace(url, rewrite(url))

    body = MD_IMG_RE.sub(md_repl, body)
    body = HTML_IMG_RE.sub(html_repl, body)
    return body


def stage_one(
    input_file: Path,
    slug_override: str | None,
    draft: bool,
    dry: bool,
    taken: set[str] | None = None,
    batch: bool = False,
) -> Path | None:
    if not input_file.is_file():
        log(f"✗ 不是文件: {input_file}")
        return None

    text = input_file.read_text(encoding="utf-8")
    fm, body, _had_fm = parse_front_matter(text)

    # 标题：已有 FM > 第一个 H1 > 文件名
    title = fm.get("title") if isinstance(fm.get("title"), str) else None
    h1_match = H1_RE.search(body)
    title_from_h1 = False
    if not title:
        if h1_match:
            title = h1_match.group(1).strip()
            title_from_h1 = True
        else:
            title = input_file.stem
    title = str(title)

    # 若标题取自正文首个 H1，从正文去掉它，避免与页面标题重复
    if title_from_h1 and h1_match:
        body = body.replace(h1_match.group(0), "", 1).lstrip("\n")

    # 日期：已有 FM date > 文件 mtime
    date_str = fm.get("date") if isinstance(fm.get("date"), str) else None
    if not date_str:
        mtime = _dt.datetime.fromtimestamp(input_file.stat().st_mtime, TZ)
        date_str = mtime.strftime("%Y-%m-%dT%H:%M:%S%z")
        date_str = date_str[:-2] + ":" + date_str[-2:]  # +0800 → +08:00

    # slug；批量模式下若与已处理篇撞名则自动加后缀，避免静默覆盖丢稿
    slug = slugify(slug_override) if slug_override else slugify(title or input_file.stem)
    if batch and taken is not None:
        if slug in taken:
            base, n = slug, 2
            while f"{base}-{n}" in taken:
                n += 1
            slug = f"{base}-{n}"
            log(f"    ↻ 撞名，改用 slug: {slug}")
        taken.add(slug)
    dest_dir = POSTS_DIR / slug
    out_md = dest_dir / "index.md"

    if out_md.exists():
        log(f"⚠ 已存在，覆盖: {out_md.relative_to(REPO_ROOT)}")

    # 图片本地化（基于源文件所在目录解析相对图片）。dry-run 绝不落盘。
    if dry:
        new_body = body
    else:
        # 重新暂存时清掉上次的图片残留，保证 bundle 只含当前正文引用的图
        stale_images = dest_dir / "images"
        if stale_images.is_dir():
            shutil.rmtree(stale_images, ignore_errors=True)
        new_body = localize_images(body, input_file.parent, dest_dir)

    new_fm = build_front_matter(dict(fm), title, date_str, draft)
    output = new_fm + "\n" + new_body.lstrip("\n")

    if dry:
        log(f"[dry-run] → {out_md.relative_to(REPO_ROOT)}")
        log(f"          title={title!r}  date={date_str}  slug={slug!r}  draft={draft}")
        log("\n----- 生成的 front matter -----")
        log(new_fm)
        return None

    dest_dir.mkdir(parents=True, exist_ok=True)
    out_md.write_text(output, encoding="utf-8")
    rel = out_md.relative_to(REPO_ROOT)
    log(f"✓ {input_file.name}  →  {rel}")
    log(f"  title={title!r}  date={date_str}  slug={slug!r}  draft={draft}")
    return out_md


def main() -> int:
    ap = argparse.ArgumentParser(description="暂存语雀导出的 md 到 Hugo 内容树。")
    ap.add_argument("input", help="单个 .md 文件，或一个目录（递归处理其中所有 .md）")
    ap.add_argument("slug", nargs="?", help="可选：自定义 URL slug（仅单文件时生效）")
    ap.add_argument("-d", "--draft", action="store_true", help="以草稿发布(draft: true)")
    ap.add_argument("-n", "--dry-run", action="store_true", help="只打印计划，不写盘")
    args = ap.parse_args()

    target = Path(args.input).expanduser().resolve()
    if not target.exists():
        log(f"✗ 路径不存在: {target}")
        return 2

    staged = []
    taken: set[str] = set()
    if target.is_dir():
        # 大小写不敏感地收集 .md（兼容 .MD / Windows 来源），排除 readme
        md_files = sorted(
            p for p in target.rglob("*")
            if p.is_file() and p.suffix.lower() == ".md" and p.name.lower() != "readme.md"
        )
        if not md_files:
            log(f"✗ 目录里没有 .md: {target}")
            return 2
        log(f"发现 {len(md_files)} 个 md，开始处理…")
        for f in md_files:
            r = stage_one(f, None, args.draft, args.dry_run, taken=taken, batch=True)
            if r:
                staged.append(r)
    else:
        r = stage_one(target, args.slug, args.draft, args.dry_run)
        if r:
            staged.append(r)

    if staged and not args.dry_run:
        log(f"\n完成 {len(staged)} 篇。下一步：")
        log("  git add content/ && git commit -m 'post: ...' && git push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
