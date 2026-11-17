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

它做四件事
----------
1. 补 Hugo front matter：若无则注入。title 取正文代码块之外的首个一级标题，否则取文件名；
   date 取已有 front matter 的 date，否则取文件 mtime（Asia/Shanghai）。
2. 正文结构清洗：
   - 移除用于提取标题的首个 H1 及其紧邻的多余分割线（---），避免与页面主标题重复；
   - 自动剔除语雀导出的手写「## 目录」锚点列表（站点已内置响应式目录，避免正文开头重复）。
3. 图片本地化（含同 URL 自动去重缓存）：
   - 远程图（http/https，含语雀 cdn.nlark.com）→ 下载到文章目录 images/，改写为相对路径；
   - 本地图（源文件旁边的 assets/xxx、images/xxx 等相对引用）→ 复制进文章目录 images/，改写；
   - 下载/复制失败 → 原样保留链接并告警（不静默吞掉）。
4. 输出为 Hugo page bundle：content/posts/<slug>/index.md (+ images/)。

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

# Markdown 图片语法：兼容 <url>、带一层括号的文件名（如 img (1).png）及可选 "title"
MD_IMG_RE = re.compile(
    r'!\[([^\]]*)\]\('
    r'(?:<([^>\n]+)>|((?:[^()\s]|\([^()\s]*\))+))'
    r'(?:\s+"[^"]*")?\)'
)
# HTML <img src="..."> —— 非贪婪，且要求 src 前是空白，避免误匹配 data-src 等
HTML_IMG_RE = re.compile(r'<img[^>]*?\ssrc=["\']([^"\']+)["\']', re.IGNORECASE)
# 围栏代码块起始/结束（``` 或 ~~~）
FENCE_RE = re.compile(r'^[ \t]*(`{3,}|~{3,})(.*)$')
# 行内代码 span（用于避免改写行内反引号里的示例图片语法）
INLINE_CODE_RE = re.compile(r'(`+)([^\n]*?)\1')
# Front Matter 边界（必须以独立 --- 行起止）
FM_BLOCK_RE = re.compile(r'\A---[ \t]*\n(.*?\n)?---[ \t]*(?:\n|\Z)', re.DOTALL)
# 水平分割线（--- / *** / ___）
HR_RE = re.compile(r'^\s*(?:-{3,}|\*{3,}|_{3,})\s*$')
# 手写目录段落（## 目录 + 列表项 + 可选分割线）
MANUAL_TOC_RE = re.compile(
    r'^\s*#{2,3}\s*(?:目录|Table\s+of\s+Contents)\s*\n'
    r'(?:[ \t]*(?:[-*+]|\d+\.)[ \t]+.+\n|\s*\n)+'
    r'(?:[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t]*\n+)?',
    re.IGNORECASE | re.MULTILINE,
)

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


def _unquote(val: str) -> str:
    val = val.strip()
    if len(val) >= 2 and val[0] in "\"'" and val[-1] == val[0]:
        return val[1:-1]
    return val


def parse_front_matter(text: str) -> tuple[dict, str, bool]:
    """
    返回 (已有FM字典, 正文, 是否存在FM)。
    支持单行 key: value、行内列表 [a, b] 与多行 YAML 列表（- item），
    并校验结构防止把正文开头的两条分割线 --- 误判为 Front Matter。
    """
    m_block = FM_BLOCK_RE.match(text)
    if not m_block:
        return {}, text, False

    fm_raw = (m_block.group(1) or "").strip("\n")
    body = text[m_block.end():].lstrip("\n")
    fm: dict = {}
    current_list_key: str | None = None

    for raw_line in fm_raw.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m_item = re.match(r'^-\s+(.*)$', stripped)
        if m_item and current_list_key is not None:
            if not isinstance(fm[current_list_key], list):
                fm[current_list_key] = []
            item_val = _unquote(m_item.group(1))
            if item_val:
                fm[current_list_key].append(item_val)
            continue

        m_kv = re.match(r'^([A-Za-z0-9_]+)\s*:\s*(.*)$', stripped)
        if not m_kv:
            # 存在非注释、非合法 YAML 键值对的行，说明这是正文而非 Front Matter
            return {}, text, False

        key, val = m_kv.group(1), m_kv.group(2).strip()
        current_list_key = None
        if not val:
            # 默认空字符串，若后续紧跟 `- item` 则自动转为列表
            fm[key] = ""
            current_list_key = key
        elif val.lower() in ("true", "false"):
            fm[key] = val.lower() == "true"
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = [_unquote(x) for x in inner.split(",")] if inner else []
            fm[key] = [x for x in items if x]
        else:
            fm[key] = _unquote(val)

    return fm, body, True


def _update_fence_state(
    line: str, in_fence: bool, fence_char: str, fence_len: int
) -> tuple[bool, str, int, bool]:
    """按 CommonMark 规则判断围栏代码块起止；返回 (in_fence, fence_char, fence_len, is_fence_line)。"""
    m = FENCE_RE.match(line)
    if not m:
        return in_fence, fence_char, fence_len, False
    marker, rest = m.group(1), m.group(2)
    ch, length = marker[0], len(marker)
    if not in_fence:
        if ch == "`" and "`" in rest:
            return in_fence, fence_char, fence_len, False
        return True, ch, length, True
    if ch == fence_char and length >= fence_len and not rest.strip():
        return False, "", 0, True
    return in_fence, fence_char, fence_len, False


def extract_first_h1(body: str) -> tuple[str | None, str]:
    """
    在围栏代码块（``` / ~~~）之外查找文档开头的第一个一级标题（# Title）。
    仅在遇到任何二级及以下标题（##）之前提取，避免误把正文深处的注释当标题。
    若提取成功，同时移除该行及紧随其后的首条孤立分割线（---）。
    """
    lines = body.splitlines(keepends=True)
    in_fence = False
    fence_char = ""
    fence_len = 0
    h1_idx: int | None = None
    h1_title: str | None = None

    for idx, line in enumerate(lines):
        in_fence, fence_char, fence_len, is_fence_line = _update_fence_state(
            line, in_fence, fence_char, fence_len
        )
        if is_fence_line or in_fence:
            continue

        # 遇到二级或更深标题仍未见 H1，说明本文无顶层 H1，停止搜索
        if re.match(r'^#{2,6}\s+', line):
            break

        m_h1 = re.match(r'^#\s+(.+?)\s*$', line)
        if m_h1:
            h1_idx = idx
            h1_title = m_h1.group(1).strip()
            break

    if h1_idx is None or not h1_title:
        return None, body

    # 移除 H1 行，并清理紧随其后的空行与单条孤立分割线
    remaining = lines[:h1_idx] + lines[h1_idx + 1 :]
    while remaining and not remaining[0].strip():
        remaining.pop(0)
    if remaining and HR_RE.match(remaining[0]):
        remaining.pop(0)
        while remaining and not remaining[0].strip():
            remaining.pop(0)

    return h1_title, "".join(remaining)


def clean_body_structure(body: str, keep_toc: bool = False) -> str:
    """清理正文开头孤立的分割线以及语雀导出的手写『## 目录』段落。"""
    lines = body.splitlines(keepends=True)
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and HR_RE.match(lines[0]):
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
    cleaned = "".join(lines)

    if not keep_toc:
        cleaned = MANUAL_TOC_RE.sub("", cleaned, count=1).lstrip("\n")
    return cleaned


def build_front_matter(fm: dict, title: str, date_str: str, draft: bool) -> str:
    """生成/补全 front matter 文本。"""
    fm.setdefault("title", title)
    fm.setdefault("date", date_str)
    fm["draft"] = draft
    fm.setdefault("description", "")
    fm.setdefault("tags", [])
    fm.setdefault("categories", [])
    fm.setdefault("ShowToc", True)

    def fmt_val(v) -> str:
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, list):
            if not v:
                return "[]"
            return "[" + ", ".join('"' + str(x).replace('"', '\\"') + '"' for x in v) + "]"
        s = str(v)
        if not s:
            return '""'
        # 含特殊字符则加引号
        if re.search(r'[:#\[\]{}"&\s]', s):
            return '"' + s.replace('"', '\\"') + '"'
        return s

    order = ["title", "date", "draft", "description", "tags", "categories", "ShowToc"]
    lines = ["---"]
    for k in order:
        if k in fm:
            lines.append(f"{k}: {fmt_val(fm[k])}")
    # 其余原有键追加在后
    for k, v in fm.items():
        if k in order:
            continue
        lines.append(f"{k}: {fmt_val(v)}")
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


def _is_valid_image(data: bytes, content_type: str) -> bool:
    """校验响应是否为真实图片（排除 HTML 登录页 / JSON 报错等伪 200 响应）。"""
    if not data or len(data) < 32:
        return False
    ct = content_type.split(";", 1)[0].strip().lower()
    head = data[:512].lstrip()
    head_low = head.lower()

    # 明确拒绝 HTML / JSON / 纯文本报错体
    if head_low.startswith((b"<!doctype", b"<html", b"<head", b"<body", b"{", b"[")):
        return False
    if ct and not ct.startswith("image/") and ct != "application/octet-stream":
        return False

    # 检查常见图片魔数或 SVG 标记
    if data.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"GIF87a", b"GIF89a", b"BM", b"\x00\x00\x01\x00")):
        return True
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True
    if len(data) >= 12 and data[4:8] == b"ftyp" and data[8:12] in (b"avif", b"avis", b"heic", b"heix", b"mif1"):
        return True
    if b"<svg" in head_low:
        return True
    return ct.startswith("image/")


def fetch_remote(url: str, images_dir: Path, seen: set[str]) -> str | None:
    """下载远程图片到 images_dir，返回新的相对路径；失败/非图片返回 None。"""
    data: bytes | None = None
    ctype = ""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 stage.py"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
            ctype = resp.headers.get("Content-Type", "")
            # 语雀/部分 CDN 需要 referer，校验不通过时带 referer 重试一次
            if not _is_valid_image(data, ctype):
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

    if not _is_valid_image(data, ctype):
        log(f"    ⚠ 响应不是图片（保留原链接）: {url}  (type={ctype or '?'})")
        return None

    parsed = urllib.parse.urlparse(url)
    base_name = Path(parsed.path).name or hashlib.md5(url.encode()).hexdigest()[:12]
    ext = ext_from_url(url, ctype)
    images_dir.mkdir(parents=True, exist_ok=True)
    fname = safe_filename(Path(base_name).stem or "image", ext, seen)
    (images_dir / fname).write_bytes(data)
    return f"images/{fname}"


def copy_local(src_path: Path, images_dir: Path, seen: set[str]) -> str | None:
    """把本地图片复制进 images_dir，返回新相对路径；文件不存在返回 None。"""
    if not src_path.is_file():
        return None
    ext = src_path.suffix.lower() or ".png"
    images_dir.mkdir(parents=True, exist_ok=True)
    fname = safe_filename(src_path.stem, ext, seen)
    shutil.copy2(src_path, images_dir / fname)
    return f"images/{fname}"


def localize_images(body: str, src_dir: Path, images_dir: Path) -> tuple[str, bool]:
    """
    扫描正文非代码块区域里的图片引用，下载/复制到 images_dir，
    并改写为相对路径 images/<fname>（同 URL 自动去重复用）。
    返回 (改写后的正文, 是否存在失败的图片)。
    """
    seen: set[str] = set()
    url_cache: dict[str, str] = {}
    had_failures = False
    src_root = src_dir.resolve()
    repo_root = REPO_ROOT.resolve()

    def rewrite(url: str) -> str:
        nonlocal had_failures
        if url.startswith("data:"):
            return url  # 内嵌 base64，不动
        if url in url_cache:
            return url_cache[url]

        parsed = urllib.parse.urlparse(url)
        if parsed.scheme in ("http", "https"):
            new = fetch_remote(url, images_dir, seen)
            if new:
                url_cache[url] = new
                return new
            had_failures = True
            return url

        # 相对/绝对本地路径 —— 必须落在源文件目录或仓库根内，防止路径穿越读取任意文件
        local = urllib.parse.unquote(url.split("?")[0].split("#")[0])
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
            had_failures = True
            return url
        new = copy_local(candidate, images_dir, seen)
        if not new:
            log(f"    ⚠ 本地图片缺失（保留原链接）: {url}")
            had_failures = True
            return url
        url_cache[url] = new
        return new

    def md_repl(m: re.Match) -> str:
        alt = m.group(1)
        url = m.group(2) or m.group(3)
        return f"![{alt}]({rewrite(url)})"

    def html_repl(m: re.Match) -> str:
        url = m.group(1)
        return m.group(0).replace(url, rewrite(url))

    def rewrite_plain_segment(seg: str) -> str:
        seg = MD_IMG_RE.sub(md_repl, seg)
        seg = HTML_IMG_RE.sub(html_repl, seg)
        return seg

    def rewrite_line(line: str) -> str:
        # 跳过行内反引号 `...` 包裹的示例语法
        parts: list[str] = []
        last = 0
        for m in INLINE_CODE_RE.finditer(line):
            if m.start() > last:
                parts.append(rewrite_plain_segment(line[last:m.start()]))
            parts.append(m.group(0))
            last = m.end()
        if last < len(line):
            parts.append(rewrite_plain_segment(line[last:]))
        return "".join(parts)

    out_lines: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in body.splitlines(keepends=True):
        in_fence, fence_char, fence_len, is_fence_line = _update_fence_state(
            line, in_fence, fence_char, fence_len
        )
        if is_fence_line or in_fence:
            out_lines.append(line)
        else:
            out_lines.append(rewrite_line(line))

    return "".join(out_lines), had_failures


def stage_one(
    input_file: Path,
    slug_override: str | None,
    draft: bool,
    dry: bool,
    taken: set[str] | None = None,
    batch: bool = False,
    keep_toc: bool = False,
) -> Path | None:
    if not input_file.is_file():
        log(f"✗ 不是文件: {input_file}")
        return None

    # utf-8-sig 自动剥离 Windows/语雀可能带入的 BOM；统一换行符为 LF
    text = input_file.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    fm, body, _had_fm = parse_front_matter(text)

    # 标题：已有 FM > 代码块之外首个顶层 H1 > 文件名
    title = fm.get("title") if isinstance(fm.get("title"), str) and fm.get("title") else None
    h1_title, body_without_h1 = extract_first_h1(body)
    if not title:
        if h1_title:
            title = h1_title
            body = body_without_h1
        else:
            title = input_file.stem
    elif h1_title and h1_title == title:
        # 已有 FM 标题且正文开头重复写了同名 H1，同样去掉正文中的重复 H1
        body = body_without_h1
    title = str(title)

    # 清理开头多余分割线与手写目录段落
    body = clean_body_structure(body, keep_toc=keep_toc)

    # 日期：已有 FM date > 文件 mtime
    date_str = fm.get("date") if isinstance(fm.get("date"), str) and fm.get("date") else None
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

    # 图片本地化（先落临时目录，成功后原子替换旧 images/，避免断链时误删旧图）。dry-run 绝不落盘。
    if dry:
        new_body = body
    else:
        final_images = dest_dir / "images"
        tmp_images = dest_dir / ".images.tmp"
        if tmp_images.exists():
            shutil.rmtree(tmp_images, ignore_errors=True)

        new_body, had_failures = localize_images(body, input_file.parent, tmp_images)

        if not had_failures:
            if final_images.exists():
                shutil.rmtree(final_images, ignore_errors=True)
            if tmp_images.is_dir():
                tmp_images.rename(final_images)
        else:
            if final_images.is_dir():
                if tmp_images.is_dir():
                    for item in tmp_images.iterdir():
                        shutil.move(str(item), str(final_images / item.name))
                    shutil.rmtree(tmp_images, ignore_errors=True)
                log("    ⚠ 部分图片失败，已保留原有 images/ 目录避免丢失本地缓存")
            elif tmp_images.is_dir():
                tmp_images.rename(final_images)

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
    ap.add_argument("--keep-toc", action="store_true", help="保留文档内手写的『## 目录』段落")
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
            r = stage_one(
                f, None, args.draft, args.dry_run,
                taken=taken, batch=True, keep_toc=args.keep_toc,
            )
            if r:
                staged.append(r)
    else:
        r = stage_one(target, args.slug, args.draft, args.dry_run, keep_toc=args.keep_toc)
        if r:
            staged.append(r)

    if staged and not args.dry_run:
        log(f"\n完成 {len(staged)} 篇。下一步：")
        log("  git add content/ && git commit -m 'post: ...' && git push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
