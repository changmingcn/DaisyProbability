# 数学概念笔记 · 源码树（本机为准）

> **另一个 Claude 会话可能同时在这棵树上干活——动手前先读 `并发会话必读.md`。**

**2026-08-01 起，这里是唯一的源头。** 以前源码只存在 Drive 的 tar 包里，每次改都要
先下载、改完再打包上传；现在反过来：**在这里改、在这里构建，只有需要交付时才推 Drive。**

## 目录

```
content/          第一册《给小学生讲微积分（上）》（副题：不能做完无穷，怎么谈论无穷）
vol2/content/     第二册《给小学生讲微积分（下）》（副题：变化有多快，面积有多大；十一篇）
vol3/content/     第三册《给小学生讲线性代数》（十篇）
vol3/assets/      第三册用的兔子插画（用户本人画的）
figs.py           第一册插图
vol2/figs.py      第二册插图
vol3/figs.py      第三册插图
build_docx.py     轻标记 → docx
verify_docx.py    17 项校验（任何 FAIL 都不许交付）
export_manuscript.py  轻标记 → 干净 Markdown 稿件
```

## 改一册的标准流程

```bash
cd ~/math-notes
./publish.sh --vol vol3         # vol1 / vol2 / vol3
```

一条命令按顺序做四件事：`figs.py` 生成图 → `build_docx.py` 编译 → `verify_docx.py` 校验
→ `export_manuscript.py` 导稿件。**这四步必须串行**：build 只消费图不生成图（图不在就报
`missing figure`），verify 只读 docx 不构建；并发跑过一次，校验读到写了一半的 docx，
字数读数漂了 37 个字。

手工跑也行：`python3 vol3/figs.py`、`python3 build_docx.py vol3`、`python3 verify_docx.py vol3`、
`python3 export_manuscript.py vol3`。第一册不带参数，第二册用 `vol2`。

## 交付（只在需要时做）

```bash
./publish.sh                    # 三册全量重建 + 校验 + 打包，不碰 Drive
./publish.sh --upload           # 复验全绿才推，九件一起
```

**一次交付＝九件**：三册 Doc ＋ 三份稿件.md ＋ 源码包 ＋ 两本手册。少一件就分叉——
07-31 出过一次"Doc 传了、喂 AI 的稿件.md 还是旧的"。`--upload` 会自己点数，不到九件当场中止。

**校验不过就不许上传**，脚本里用的是 `if python3 verify_docx.py …; then <上传>; fi`；
别用 `&&` 接 `grep`（grep 成功也会放行，出过一次事故）。

## 版本

本目录是 git 库，回滚不用再去 Drive 找 tar：`git diff` 看改了什么，`git checkout -- <文件>` 退回。
生成产物（`figs/`、`*.docx`、稿件.md、源码 tar）都在 `.gitignore` 里，不入库。

## 手册

- `~/.claude/agents/DaisyCalculus.md` —— 第一、二册
- `~/.claude/agents/DaisyAlgebra.md` —— 第三册

**这两个路径是权威副本**（agent 定义必须放在那儿才能加载），Drive 上的是镜像；
`publish.sh --upload` 会从那里读取并一起推。
