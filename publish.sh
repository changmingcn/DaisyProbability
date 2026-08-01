#!/bin/bash
# 《数学概念笔记》三册 —— 本机构建与交付管线
#
#   ./publish.sh            重建 + 校验 + 打包（**不碰 Drive**，日常改稿用这个）
#   ./publish.sh --upload   上面全做完，再把九件一起推到 Drive
#   ./publish.sh --vol vol2 只重建校验某一册（不打包、不上传）
#
# 权威源是本机 ~/math-notes。Drive 只是交付镜像，改完不必每次都推。
#
# 三条写进脚本的规矩，都是被真事故逼出来的：
#   1. 生成图 → 构建 → 校验必须串行。曾经并发跑，校验读到写了一半的 docx，
#      字数读数漂了 37 个字，白查半小时。
#   2. 校验不过就不许上传。曾经写成 `verify | grep && 上传`，grep 成功让上传照跑。
#      这里一律用 if 判真退出码，且上传前重跑一次全量校验。
#   3. 九件一起推。曾经 Doc 传了、喂 AI 的稿件.md 还是旧的，两边分叉。

set -u
cd "$(dirname "$0")" || exit 1
ROOT="$PWD"
LOGDIR="$ROOT/.build-logs"; mkdir -p "$LOGDIR"
AGENTS="$HOME/.claude/agents"
RCLONE="$HOME/.local/bin/rclone"
DRIVE_ID=1omcMKl3BdXlDWnWOOJnRPdBHuuSmcvkG
TARBALL="数学概念笔记-构建源码.tar.gz"

# 分册：目录参数 | docx 所在目录 | 稿件后缀
VOLS=("::上部分" "vol2:vol2:下部分" "vol3:vol3:第三册")

die() { echo "✗ $*" >&2; exit 1; }
say() { echo; echo "──── $* ────"; }

# ---------- 一册：生成图 → 构建 → 校验（严格串行） ----------
build_one() {
  local dir="$1" sub="$2"
  local figs="${dir:+$dir/}figs.py"
  say "${dir:-vol1}"
  python3 "$figs" >/dev/null || die "${dir:-vol1} 插图生成失败"
  python3 build_docx.py $dir  >/dev/null || die "${dir:-vol1} 构建失败"
  if python3 verify_docx.py $dir > "$LOGDIR/verify-${dir:-vol1}.log" 2>&1; then
    grep -E "WARN" "$LOGDIR/verify-${dir:-vol1}.log"
    echo "  ✓ ${dir:-vol1} 校验通过（$(grep -c PASS "$LOGDIR/verify-${dir:-vol1}.log") 项 PASS）"
  else
    grep -E "FAIL" "$LOGDIR/verify-${dir:-vol1}.log"
    die "${dir:-vol1} 校验未通过 —— 完整日志 $LOGDIR/verify-${dir:-vol1}.log"
  fi
  python3 export_manuscript.py $dir >/dev/null || die "${dir:-vol1} 稿件导出失败"
}

# ---------- 只跑一册 ----------
if [ "${1:-}" = "--vol" ]; then
  case "${2:-}" in
    vol1|"") build_one "" "上部分" ;;
    vol2)    build_one vol2 "下部分" ;;
    vol3)    build_one vol3 "第三册" ;;
    *) die "未知分册 ${2:-}（可用：vol1 vol2 vol3）" ;;
  esac
  echo; echo "✓ 单册完成（未打包、未上传）"; exit 0
fi

# ---------- 三册全量 ----------
for v in "${VOLS[@]}"; do
  IFS=: read -r dir _ sub <<< "$v"
  build_one "$dir" "$sub"
done

# ---------- 打包源码（只装源文件，不装 figs/ 和 docx 产物） ----------
say "打包源码"
FILES=(build_docx.py cn_fractions.py export_manuscript.py figs.py restructure.py
       slash_fractions.py verify_docx.py publish.sh
       content/*.md
       vol2/TITLE vol2/figs.py vol2/content/*.md
       vol3/TITLE vol3/figs.py vol3/assets/rabbit.png vol3/content/*.md)
COPYFILE_DISABLE=1 tar -czf "$TARBALL" "${FILES[@]}" || die "打包失败"
echo "  ✓ ${TARBALL}（$(tar -tzf "$TARBALL" | grep -c . ) 项，$(du -h "$TARBALL" | cut -f1)）"

# ---------- 九件清单 ----------
ITEMS=(
  "不能做完无穷，怎么谈论无穷.docx|不能做完无穷，怎么谈论无穷.docx|docx"
  "vol2/变化有多快，面积有多大.docx|变化有多快，面积有多大.docx|docx"
  "vol3/给小学生讲线性代数.docx|给小学生讲线性代数.docx|docx"
  "数学概念笔记-上部分-稿件.md|数学概念笔记-上部分-稿件.md|raw"
  "数学概念笔记-下部分-稿件.md|数学概念笔记-下部分-稿件.md|raw"
  "数学概念笔记-第三册-稿件.md|数学概念笔记-第三册-稿件.md|raw"
  "$TARBALL|$TARBALL|raw"
  "$AGENTS/DaisyCalculus.md|DaisyCalculus.md|raw"
  "$AGENTS/DaisyAlgebra.md|DaisyAlgebra.md|raw"
)

say "九件齐否"
missing=0
for it in "${ITEMS[@]}"; do
  IFS='|' read -r src _ _ <<< "$it"
  [ -f "$src" ] || { echo "  ✗ 缺 $src"; missing=1; }
done
[ $missing -eq 0 ] || die "九件不齐，拒绝上传"
echo "  ✓ 九件齐（三册 Doc ＋ 三份稿件 ＋ 源码包 ＋ 两本手册）"

if [ "${1:-}" != "--upload" ]; then
  echo
  echo "✓ 本机全绿。未上传 Drive（要上传：./publish.sh --upload）"
  exit 0
fi

# ---------- 上传：先重跑一遍全量校验，再推 ----------
say "上传前复验"
for v in "${VOLS[@]}"; do
  IFS=: read -r dir _ _ <<< "$v"
  if python3 verify_docx.py $dir >/dev/null 2>&1; then
    echo "  ✓ ${dir:-vol1}"
  else
    die "${dir:-vol1} 复验未通过，中止上传"
  fi
done

say "推 Drive（九件）"
n=0
for it in "${ITEMS[@]}"; do
  IFS='|' read -r src dst kind <<< "$it"
  extra=()
  [ "$kind" = "docx" ] && extra=(--drive-import-formats docx)
  if "$RCLONE" copyto "$src" "Gdrive:$dst" \
        --drive-root-folder-id="$DRIVE_ID" "${extra[@]}"; then
    n=$((n+1)); echo "  ✓ $dst"
  else
    echo "  ✗ $dst"
  fi
done
echo
[ "$n" -eq 9 ] && echo "✓ 九件全部上传" || die "只上传了 $n/9 件 —— Drive 现在是分叉状态，务必补齐"
