---
title: "关于"
date: 2026-08-04
draft: false
description: "关于 threed33 与本站架构"
ShowToc: false
ShowReadingTime: false
ShowWordCount: false
hideMeta: true
---

你好，我是 **threed33**。这里用于整理和沉淀日常学习笔记、网络安全与攻防实践总结。

### 站点架构

- **生成器与主题**：基于 [Hugo](https://gohugo.io/) + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 构建，通过 `assets/css/extended/custom.css` 与轻量级 Partial 模板定制了宽屏左侧常驻目录、吸顶导航与中英文排版细节。
- **内容工作流**：日常在 [语雀](https://www.yuque.com/) 记录笔记，导出 Markdown 后经仓库内置的 `scripts/stage.py` 自动补全 Front Matter、清理冗余目录并将远程 CDN 图片本地化为 Hugo Page Bundle。
- **自动部署**：推送至 `main` 分支后由 GitHub Actions 自动构建发布至 GitHub Pages，并支持通过 `rsync` 增量同步至云服务器。

### 链接

- **GitHub**：[@threed33](https://github.com/threed33)
- **RSS 订阅**：[/index.xml](/index.xml)
