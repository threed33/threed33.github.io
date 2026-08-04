---
title: "博客上线了"
date: 2026-08-04
draft: false
description: "第一篇日志 —— 这是什么、怎么发新文章、语雀 md 怎么搬过来。"
tags: ["公告", "建站"]
categories: ["随笔"]
ShowToc: true
TocOpen: true
---

博客搭好了。这篇同时是个「使用说明」。

## 这是什么

一个静态博客：Hugo 生成页面，PaperMod 主题，托管在 GitHub Pages。每篇文章右侧有大纲，顶部有搜索、归档、标签。

## 怎么发新文章

推荐两种方式：

**1. 从语雀导出（主流程）**

```bash
# 把导出的 md 暂存到 inbox/，然后：
./scripts/stage.py inbox/我的笔记.md
# → 自动生成 content/posts/我的笔记/index.md
#   补好 front matter，图片下载到本地、链接改写好

git add content/ && git commit -m "post: 我的笔记" && git push
# → GitHub Actions 自动构建 → 几十秒后 threed33.github.io 更新
```

`stage.py` 也可以直接吃一个目录，批量处理里面所有 `.md`：

```bash
./scripts/stage.py inbox/
```

**2. 从零写**

```bash
hugo new posts/新文章/index.md   # 用 archetypes/default.md 模板
# 编辑 content/posts/新文章/index.md，写完把 draft 改成 false
```

## 关于语雀导出

语雀导出的 md 有两个坑，`stage.py` 都帮你处理了：

- **没有 Hugo 需要的 front matter**：脚本会自动补 `title`（取正文第一个一级标题）、`date`（取文件修改时间）等。
- **图片是语雀 CDN 链接（会过期失效）**：脚本会把远程图片下载到文章目录、改写成相对路径；如果是从桌面客户端导出的本地 `assets/` 图片，也会一起搬进来。

然后 `git push`，剩下的交给 CI。

## 接下来

- [ ] 搬一批语雀笔记过来
- [ ] （以后）部署到云服务器
- [ ] （可选）开 giscus 评论
