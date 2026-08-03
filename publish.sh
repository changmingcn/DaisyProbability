#!/bin/bash
# 《数学概念笔记》四册 —— 本机构建与交付管线
#
#   ./publish.sh            重建 + 校验 + 打包（**不碰 Drive**，日常改稿用这个）
#   ./publish.sh --upload   上面全做完，再把十二件一起推到 Drive
#   ./publish.sh --vol vol2 只重建校验某一册（不打包、不上传）
#
# 权威源是本机 ~/math-notes。Drive 只是交付镜像，改完不必每次都推。
#
# 三条写进脚本的规矩，都是被真事故逼出来的：
#   1. 生成图 → 构建 → 校验必须串行。曾经并发跑，校验读到写了一半的 docx，
#      字数读数漂了 37 个字，白查半小时。
#   2. 校验不过就不许上传。曾经写成 `verify | grep && 上传`，grep 成功让上传照跑。
#      这里一律用 if 判真退出码，且上传前重跑一次全量校验。
#   3. 十二件一起推。曾经 Doc 传了、喂 AI 的稿件.md 还是旧的，两边分叉。

set -u
cd "$(dirname "$0")" || exit 1
ROOT="$PWD"
LOGDIR="$ROOT/.build-logs"; mkdir -p "$LOGDIR"
# 跑管线的会话一定看得见这一行——并发覆盖就是这么发生的
[ -f "$ROOT/并发会话必读.md" ] && echo "ℹ 另一个 Claude 会话可能也在这棵树上：先读 ~/math-notes/并发会话必读.md"
# 三本手册的权威副本在仓库里（manuals/），~/.claude/agents/ 下是**硬链接**到同一个文件。
# 以前手册在 git 之外，两个会话各自整篇写回，覆盖了不留痕迹——收进仓库就看得见了。
#
# 为什么用硬链接不用软链接：agents 目录里必须是货真价实的文件，
# Claude Code 认不认软链接没法在会话里验（agent 列表是启动时缓存的），不赌。
# 硬链接唯一的破绽是 git 重建文件会断开（checkout / stash / merge 动到 manuals/ 时），
# 下面这道检查就是为它准备的：断了就中止，别再无声分叉一次。
AGENTS="$ROOT/manuals"

# die/say 必须定义在任何会调用它们的分支之前 —— --relink 走的是立即执行的分支，
# 定义放在下面的话，一走到报错路径就是 "die: command not found"。
die() { echo "✗ $*" >&2; exit 1; }
say() { echo; echo "──── $* ────"; }
# ⚠ Claude Code 的 Edit/Write 是"写临时文件再改名"，**每改一次手册就断一次硬链接**。
# 而改手册的规矩正是"只用 Edit 改局部"——所以断链是常态，不是异常。
# 光报错会让这道闸变成每次都要人工处理的路障，于是分两种情形：
#   两边内容相同 → 说明只是文件被重建过（git checkout / 改完又改回），直接重连；
#   两边内容不同 → 才是真危险（一边的改动会被另一边盖掉），打出 diff 摘要并中止。
check_manual_links() {
  local n a
  for n in DaisyCalculus DaisyAlgebra DaisyProbability; do
    a="$HOME/.claude/agents/$n.md"
    [ -e "$AGENTS/$n.md" ] || die "手册不见了：manuals/$n.md"
    [ -e "$a" ] || { ln "$AGENTS/$n.md" "$a" && echo "  ℹ ${n}：agents/ 那份不见了，已从 manuals/ 重连"; continue; }
    [ "$a" -ef "$AGENTS/$n.md" ] && continue
    if diff -q "$a" "$AGENTS/$n.md" >/dev/null; then
      rm "$a" && ln "$AGENTS/$n.md" "$a"
      echo "  ℹ ${n}：硬链接断过但两边内容一致，已重连"
    else
      echo "  ⚠ $n 两边内容不一致（$(diff "$a" "$AGENTS/$n.md" | grep -c '^[<>]') 行不同）：" >&2
      diff "$a" "$AGENTS/$n.md" | head -6 >&2
      die "${n}：agents/ 与 manuals/ 已分叉，别让任何一边被无声盖掉。
   看全文差异：diff $a $AGENTS/$n.md
   若 manuals/ 那份对（常见：你刚用 Edit 改了它）：./publish.sh --relink
   若 agents/ 那份对：先把它的内容 Edit 进 manuals/，再 ./publish.sh --relink"
    fi
  done
}

# 认定 manuals/ 为准，强制重连（agents/ 那份会被丢弃）
if [ "${1:-}" = "--relink" ]; then
  for n in DaisyCalculus DaisyAlgebra DaisyProbability; do
    a="$HOME/.claude/agents/$n.md"
    [ -e "$AGENTS/$n.md" ] || die "手册不见了：manuals/$n.md"
    if [ -e "$a" ] && [ "$a" -ef "$AGENTS/$n.md" ]; then echo "  ✓ $n 本来就是同一个文件"; continue; fi
    rm -f "$a" && ln "$AGENTS/$n.md" "$a" && echo "  ✓ $n 已按 manuals/ 重连"
  done
  exit 0
fi
RCLONE="$HOME/.local/bin/rclone"
DRIVE_ID=1omcMKl3BdXlDWnWOOJnRPdBHuuSmcvkG
TARBALL="数学概念笔记-构建源码.tar.gz"

# 分册：目录参数 | docx 所在目录 | 稿件后缀
VOLS=("::上部分" "vol2:vol2:下部分" "vol3:vol3:第三册" "vol4:vol4:第四册")

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
  # 节号对账：`第X篇第Y节` 指到的那一节，真的在讲被引的那个词吗？
  # （2026-08-03 加。起因：第四篇 C7 把"第三篇第六节的上确界"写成了第五节，
  #   audit_refs 抓不到——它只查引号里的承诺，那个词是加粗的。）
  local sv="${dir:-vol1}"
  if ! python3 audit_sections.py --vol "$sv" > "$LOGDIR/sections-$sv.log" 2>&1; then
    grep -E "^\s*\[S" "$LOGDIR/sections-$sv.log"
    die "$sv 节号对账未通过 —— 完整日志 $LOGDIR/sections-$sv.log"
  fi
  echo "  ✓ $sv 节号对账通过（$(sed -n '1s/.*：\([0-9]*\) 处.*/\1/p' "$LOGDIR/sections-$sv.log") 处引用）"
  python3 export_manuscript.py $dir >/dev/null || die "${dir:-vol1} 稿件导出失败"
}

# ---------- 只跑一册 ----------
if [ "${1:-}" = "--vol" ]; then
  case "${2:-}" in
    vol1|"") build_one "" "上部分" ;;
    vol2)    build_one vol2 "下部分" ;;
    vol3)    build_one vol3 "第三册" ;;
    vol4)    build_one vol4 "第四册" ;;
    *) die "未知分册 ${2:-}（可用：vol1 vol2 vol3 vol4）" ;;
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
# ⚠ 加了新脚本记得回来加一行：08-01 加 export_html.py／audit_refs.py 时忘了，
#   包照样"成功"、件数照样对得上，交付出去的源码包却缺工具（打包不会因为漏文件而报错）。
FILES=(build_docx.py cn_fractions.py export_manuscript.py figs.py restructure.py
       slash_fractions.py verify_docx.py publish.sh export_html.py audit_refs.py
       audit_sections.py
       TITLE content/*.md
       vol2/TITLE vol2/figs.py vol2/content/*.md
       vol3/TITLE vol3/figs.py vol3/assets/rabbit.png vol3/content/*.md
       vol4/TITLE vol4/figs.py vol4/content/*.md)
# gzip -n 不能省：tar -czf 会把当前时间写进 gzip 头，同样的源码连打两次哈希都不一样，
# "Drive 和本机是否一致"就没法用 md5 核对了（两个会话的协作全靠这条核对）。
# -n 去掉时间戳后，内容不变则字节不变。COPYFILE_DISABLE=1 挡 macOS 的 ._ 附加文件。
COPYFILE_DISABLE=1 tar -cf - "${FILES[@]}" | gzip -n > "$TARBALL" || die "打包失败"
echo "  ✓ ${TARBALL}（$(tar -tzf "$TARBALL" | grep -c . ) 项，$(du -h "$TARBALL" | cut -f1)）"

# ---------- 交付清单（十二件）----------
# 2026-08-01 起交付件不再散在 Drive「Claude」根目录，统一收进 Claude/数学概念笔记/ 下的四个子目录。
# DRIVE_ID 仍是 Claude 文件夹（rclone 的 root 就是它），所以 dst 写成相对路径 数学概念笔记/NN-…/文件名。
# ⚠ 改这里的目录名，Drive 上就会多出一个新目录、旧的留在原地不动（rclone 按路径认文件，不按 id）——
#   要改名，先在 Drive 上把目录挪好，再改这张表，然后跑一次 --upload 核对没有多出副本。
D1=数学概念笔记/01-三册成书
D2=数学概念笔记/02-三份稿件
D3=数学概念笔记/03-交接手册
D4=数学概念笔记/04-构建源码
ITEMS=(
  "给小学生讲微积分（上）.docx|$D1/给小学生讲微积分（上）.docx|docx"
  "vol2/给小学生讲微积分（下）.docx|$D1/给小学生讲微积分（下）.docx|docx"
  "vol3/给小学生讲线性代数.docx|$D1/给小学生讲线性代数.docx|docx"
  "vol4/给小学生讲概率论.docx|$D1/给小学生讲概率论.docx|docx"
  "数学概念笔记-上部分-稿件.md|$D2/数学概念笔记-上部分-稿件.md|raw"
  "数学概念笔记-下部分-稿件.md|$D2/数学概念笔记-下部分-稿件.md|raw"
  "数学概念笔记-第三册-稿件.md|$D2/数学概念笔记-第三册-稿件.md|raw"
  "数学概念笔记-第四册-稿件.md|$D2/数学概念笔记-第四册-稿件.md|raw"
  "$TARBALL|$D4/$TARBALL|raw"
  "$AGENTS/DaisyCalculus.md|$D3/DaisyCalculus.md|raw"
  "$AGENTS/DaisyAlgebra.md|$D3/DaisyAlgebra.md|raw"
  "$AGENTS/DaisyProbability.md|$D3/DaisyProbability.md|raw"
)

say "十二件齐否"
missing=0
for it in "${ITEMS[@]}"; do
  IFS='|' read -r src _ _ <<< "$it"
  [ -f "$src" ] || { echo "  ✗ 缺 $src"; missing=1; }
done
[ $missing -eq 0 ] || die "十二件不齐，拒绝上传"
echo "  ✓ 十二件齐（四册 Doc ＋ 四份稿件 ＋ 源码包 ＋ 三本手册）"

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

say "推 Drive（十二件）"

# 别用 extra=() 数组攒参数：macOS 自带 bash 3.2 在 set -u 下，
# 展开空数组 "${extra[@]}" 会当成未定义变量直接把脚本打死。
# 08-01 就是这么崩的：前三件 docx 数组非空所以过了，第四件稿件.md 一到就死，
# 而且死得比下面 n -eq 12 那道网还早，"只传了 3/12"根本没打印出来。
push_one() {
  if [ "$3" = docx ]; then
    "$RCLONE" copyto "$1" "Gdrive:$2" --drive-root-folder-id="$DRIVE_ID" --drive-import-formats docx
  else
    "$RCLONE" copyto "$1" "Gdrive:$2" --drive-root-folder-id="$DRIVE_ID"
  fi
}

# 上面那次教训：安全网只挂在正常出口上，是拦不住半路暴毙的。这个 trap 挂在所有出口。
n=0
trap '[ "${n:-0}" -gt 0 ] && [ "${n:-0}" -lt 12 ] && echo "
⚠ 只推上去 $n/12 件，Drive 现在是分叉的 —— 重跑 ./publish.sh --upload 补齐" >&2' EXIT

for it in "${ITEMS[@]}"; do
  IFS='|' read -r src dst kind <<< "$it"
  if push_one "$src" "$dst" "$kind"; then
    n=$((n+1)); echo "  ✓ $dst"
  else
    echo "  ✗ $dst"
  fi
done
echo
[ "$n" -eq 12 ] && echo "✓ 十二件全部上传" || die "只上传了 $n/12 件 —— Drive 现在是分叉状态，务必补齐"
