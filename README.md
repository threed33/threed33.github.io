# threed33.github.io

基于 [Hugo](https://gohugo.io/) + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 构建的个人静态技术博客，支持 GitHub Pages 自动发布与云服务器 `rsync` 同步。内容主要从[语雀](https://www.yuque.com/)导出。

## 目录结构

```text
.
├── archetypes/default.md          # hugo new 的文章模板
├── assets/css/extended/
│   └── custom.css                 # ★ 扩展样式表（Hugo Pipes 自动合并、压缩、指纹化）
├── content/
│   ├── posts/                     # ← 文章目录（Page Bundle: <slug>/index.md + images/）
│   ├── about.md                   # 关于页（/about/）
│   ├── archives.md                # 归档页（/archives/，layout: archives）
│   └── search.md                  # 搜索页（/search/，layout: search）
├── layouts/_partials/
│   ├── toc.html                   # 响应式目录（宽屏左侧常驻 + 窄屏顶部可折叠）
│   ├── post_meta.html             # 文章元信息（发布/更新日期、阅读时长、字数、分类徽标）
│   ├── extend_head.html           # Head 扩展钩子说明
│   └── extend_footer.html         # 左侧常驻目录双向滚动高亮（rAF scroll-spy）
├── scripts/stage.py               # ★ 语雀 Markdown → Hugo Page Bundle 预处理脚本
├── themes/PaperMod/               # 主题（git submodule，零侵入）
├── .github/workflows/
│   ├── deploy.yml                 # push → 构建 → GitHub Pages
│   └── deploy-cloud.yml           # 手动触发 → 构建 → rsync 同步到云服务器
├── hugo.toml                      # 站点全局配置
└── inbox/                         # 本地暂存区（导出的 md 丢这里，已 gitignore）
```

## 发新文章

### 主流程：从语雀导出

```bash
# 1. 语雀导出 md，丢进 inbox/
mkdir -p inbox && mv ~/Downloads/笔记.md inbox/

# 2. stage：补 front matter + 结构清洗 + 图片本地化
./scripts/stage.py inbox/笔记.md
#   批量：./scripts/stage.py inbox/
#   试跑：./scripts/stage.py inbox/笔记.md -n
#   草稿：./scripts/stage.py inbox/笔记.md --draft

# 3. push，CI 自动构建发布
git add content/ && git commit -m "post: 笔记" && git push
```

`stage.py` 自动完成四件事：
1. **补全 Front Matter**：`title` 取正文代码块外的首个一级标题，`date` 取文件修改时间（`Asia/Shanghai`）。
2. **清理冗余结构**：移除用于提取标题的首个 `# H1` 及其下方的孤立分割线 `---`，并自动剔除语雀内手写的 `## 目录` 列表（避免与站点左侧常驻目录重复；如需保留可加 `--keep-toc`）。
3. **图片本地化与去重**：远程图（语雀 CDN 等，内置 `Referer` 防盗链重试与类型校验）下载到文章目录 `images/`，本地 `assets/` 图复制进来，链接改写为相对路径；同一篇内相同图片 URL 自动去重复用。
4. **安全兜底**：失败的图片保留原链接并打印告警，绝不静默丢图。

### 从零写

```bash
hugo new content posts/新文章/index.md   # 用模板创建，默认 draft: true
# 编辑后把 draft 改成 false
git add content/ && git commit -m "post: 新文章" && git push
```

## 本地预览

```bash
hugo server -D   # -D 包含草稿；浏览器访问 http://localhost:1313
```

> 没装 Hugo？macOS `brew install hugo`；Windows/Linux 从 [gohugo.io](https://gohugo.io/installation/) 下载 **extended** 版。CI 会自动安装，本地装不装都不影响发布。

## 部署

- **GitHub Pages**：push 到 `main` 即自动构建并部署（`.github/workflows/deploy.yml`）。
- **云服务器**：在仓库 `Settings → Secrets and variables → Actions` 配置好 `CLOUD_*` 密钥后，在 Actions 页面手动触发 `Deploy to Cloud (rsync)`（`.github/workflows/deploy-cloud.yml`）。

## 主题升级与切换

所有自定义样式均位于 `assets/css/extended/custom.css`，布局扩展仅覆写 `layouts/_partials/` 下的轻量级钩子，未直接改动 `themes/PaperMod` 子模块：

```bash
# 升级 PaperMod 到最新上游版本
git -C themes/PaperMod fetch origin
git -C themes/PaperMod checkout origin/master
git add themes/PaperMod && git commit -m "chore: update PaperMod submodule"
```
