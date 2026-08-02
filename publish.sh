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
# 两本手册的权威副本在仓库里（manuals/），~/.claude/agents/ 下是**硬链接**到同一个文件。
# 以前手册在 git 之外，两个会话各自整篇写回，覆盖了不留痕迹——收进仓库就看得见了。
#
# 为什么用硬链接不用软链接：agents 目录里必须是货真价实的文件，
# Claude Code 认不认软链接没法在会话里验（agent 列表是启动时缓存的），不赌。
# 硬链接唯一的破绽是 git 重建文件会断开（checkout / stash / merge 动到 manuals/ 时），
# 下面这道检查就是为它准备的：断了就中止，别再无声分叉一次。
AGENTS="$ROOT/manuals"
check_manual_links() {
  local n a
  for n in DaisyCalculus DaisyAlgebra; do
    a="$HOME/.claude/agents/$n.md"
    [ -e "$AGENTS/$n.md" ] || die "手册不见了：manuals/$n.md"
    [ -e "$a" ] || die "$a 不见了，重建：ln $AGENTS/$n.md $a"
    [ "$a" -ef "$AGENTS/$n.md" ] || die \
"$a 和 manuals/$n.md 已经不是同一个文件了（多半是 git 重建过 manuals/）。
   先 diff 看两边差什么、合并好，再重建硬链：rm $a && ln $AGENTS/$n.md $a"
  done
}
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
check_manual_links
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

# 别用 extra=() 数组攒参数：macOS 自带 bash 3.2 在 set -u 下，
# 展开空数组 "${extra[@]}" 会当成未定义变量直接把脚本打死。
# 08-01 就是这么崩的：前三件 docx 数组非空所以过了，第四件稿件.md 一到就死，
# 而且死得比下面 n -eq 9 那道网还早，"只传了 3/9"根本没打印出来。
push_one() {
  if [ "$3" = docx ]; then
    "$RCLONE" copyto "$1" "Gdrive:$2" --drive-root-folder-id="$DRIVE_ID" --drive-import-formats docx
  else
    "$RCLONE" copyto "$1" "Gdrive:$2" --drive-root-folder-id="$DRIVE_ID"
  fi
}

# 上面那次教训：安全网只挂在正常出口上，是拦不住半路暴毙的。这个 trap 挂在所有出口。
n=0
trap '[ "${n:-0}" -gt 0 ] && [ "${n:-0}" -lt 9 ] && echo "
⚠ 只推上去 $n/9 件，Drive 现在是分叉的 —— 重跑 ./publish.sh --upload 补齐" >&2' EXIT

for it in "${ITEMS[@]}"; do
  IFS='|' read -r src dst kind <<< "$it"
  if push_one "$src" "$dst" "$kind"; then
    n=$((n+1)); echo "  ✓ $dst"
  else
    echo "  ✗ $dst"
  fi
done
echo
[ "$n" -eq 9 ] && echo "✓ 九件全部上传" || die "只上传了 $n/9 件 —— Drive 现在是分叉状态，务必补齐"
