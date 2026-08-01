# 数学概念笔记 · 源码树（本机为准）

**2026-08-01 起，这里是唯一的源头。** 以前源码只存在 Drive 的 tar 包里，每次改都要
先下载、改完再打包上传；现在反过来：**在这里改、在这里构建，只有需要交付时才推 Drive。**

## 目录

```
content/          第一册《不能做完无穷，怎么谈论无穷》
vol2/content/     第二册《变化有多快，面积有多大》（十一篇）
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
python3 vol3/figs.py            # 改了图才需要跑
python3 build_docx.py vol3
python3 verify_docx.py vol3     # 必须全绿
python3 export_manuscript.py vol3
```

第一册不带参数（`python3 build_docx.py`），第二册用 `vol2`，第三册用 `vol3`。

## 交付（只在需要时做）

```bash
ID=1omcMKl3BdXlDWnWOOJnRPdBHuuSmcvkG
R=~/.local/bin/rclone
cd ~/math-notes
tar czf /tmp/mn-src.tar.gz content vol2/content vol2/figs.py vol2/TITLE \
    vol3/content vol3/figs.py vol3/TITLE vol3/assets \
    build_docx.py cn_fractions.py export_manuscript.py figs.py \
    restructure.py slash_fractions.py verify_docx.py
$R copyto "vol3/给小学生讲线性代数.docx" "Gdrive:给小学生讲线性代数.docx" \
    --drive-root-folder-id=$ID --drive-import-formats docx
$R copyto "数学概念笔记-第三册-稿件.md" "Gdrive:数学概念笔记-第三册-稿件.md" \
    --drive-root-folder-id=$ID
$R copyto /tmp/mn-src.tar.gz "Gdrive:数学概念笔记-构建源码.tar.gz" --drive-root-folder-id=$ID
```

**校验不过就不许上传**：写成 `if python3 verify_docx.py vol3 >/dev/null; then <上传>; fi`，
别用 `&&` 接 `grep`（那样 grep 成功也会放行，出过一次事故）。

## 手册

- `~/.claude/agents/DaisyCalculus.md` —— 第一、二册
- `~/.claude/agents/DaisyAlgebra.md` —— 第三册

两份都在 Drive「Claude」有同名副本，**改完记得同步**。
