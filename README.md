# threed33.github.io

Hugo + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 静态博客，托管在 GitHub Pages。内容主要从[语雀](https://www.yuque.com/)导出。

## 目录结构

```
.
├── archetypes/default.md     # hugo new 的文章模板
├── content/
│   ├── posts/                # ← 文章都在这里（page bundle: <slug>/index.md）
│   ├── about.md
│   ├── archives.md           # 归档页（layout: archives）
│   └── search.md             # 搜索页（layout: search）
├── scripts/stage.py          # ★ 语雀 md → Hugo 内容 的暂存脚本
├── themes/PaperMod/          # 主题（git submodule）
├── .github/workflows/
│   ├── deploy.yml            # push → 构建 → GitHub Pages
│   └── deploy-cloud.yml      # （以后）构建 → rsync 到云服务器
├── hugo.toml                 # 站点配置
└── inbox/                    # 本地暂存区（导出的 md 丢这里，已 gitignore）
```

## 发新文章

### 主流程：从语雀导出

```bash
# 1. 语雀导出 md，丢进 inbox/
mkdir -p inbox && mv ~/Downloads/笔记.md inbox/

# 2. stage：补 front matter + 图片本地化
./scripts/stage.py inbox/笔记.md
#   批量：./scripts/stage.py inbox/
#   试跑：./scripts/stage.py inbox/笔记.md -n
#   草稿：./scripts/stage.py inbox/笔记.md --draft

# 3. push，CI 自动构建发布
git add content/ && git commit -m "post: 笔记" && git push
```

`stage.py` 做的事：
- **补 front matter**：`title` 取正文第一个 `#`，`date` 取文件修改时间；没有就自动生成。
- **图片本地化**：远程图（语雀 CDN 等）下载到文章目录 `images/`，本地 `assets/` 图复制进来，链接改写为相对路径 —— 不再依赖会过期的 CDN。
- 失败的图片会**保留原链接并告警**，不会静默丢图。

### 从零写

```bash
hugo new posts/新文章/index.md   # 用模板，draft: true
# 编辑后把 draft 改成 false
git add . && git commit -m "post: 新文章" && git push
```

## 本地预览

```bash
hugo server -D   # -D 包含草稿；浏览器开 http://localhost:1313
```

> 没装 Hugo？macOS `brew install hugo`；Windows/WSL 从 [gohugo.io](https://gohugo.io/installation/) 下 extended 版。CI 会自己装，本地装不装都不影响发布。

## 部署

- **GitHub Pages**：push 到 `main` 即自动部署（`.github/workflows/deploy.yml`）。
- **云服务器**（以后）：配好仓库 Settings → Secrets 里的 `CLOUD_*`，手动触发 `deploy-cloud.yml`（rsync 同一份产物）。

## 切换主题

content 都是标准 markdown，换主题零迁移成本。PaperMod → DoIt/Stack 等，先 `git submodule add` 新主题再改 `hugo.toml` 的 `theme` 即可。
