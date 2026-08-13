#!/bin/bash
# Project-local build and delivery pipeline. Its scope comes only from project.conf.

set -euo pipefail
cd "$(dirname "$0")" || exit 1
ROOT="$PWD"
CONFIG="$ROOT/project.conf"
[ -f "$CONFIG" ] || { echo "✗ missing project.conf" >&2; exit 1; }
# shellcheck source=/dev/null
. "$CONFIG"

LOGDIR="$ROOT/.build-logs"
mkdir -p "$LOGDIR"
AGENTS="$ROOT/manuals"
RCLONE="$HOME/.local/bin/rclone"

die() { echo "✗ $*" >&2; exit 1; }
say() { echo; echo "──── $* ────"; }

usage() {
  cat <<EOF
Usage:
  ./publish.sh                 build and verify only $PROJECT_LABEL; do not upload
  ./publish.sh --vol VOL       build one volume owned by this project
  ./publish.sh --upload        build, verify, package, and upload only this project
  ./publish.sh --relink        restore only the $MANUAL_NAME agent hard link
  ./publish.sh --help          show this help

This project publishes raw HTML and never generates Google Docs, DOCX, or PDF files.
EOF
}

check_manual_link() {
  local src="$AGENTS/$MANUAL_NAME.md"
  local agent="$HOME/.claude/agents/$MANUAL_NAME.md"
  [ -e "$src" ] || die "missing manual: manuals/$MANUAL_NAME.md"
  if [ ! -e "$agent" ]; then
    ln "$src" "$agent" || die "cannot create agent hard link"
    echo "  ℹ $MANUAL_NAME agent entry was missing and has been relinked"
    return
  fi
  [ "$agent" -ef "$src" ] && return
  if diff -q "$agent" "$src" >/dev/null; then
    rm -f "$agent" && ln "$src" "$agent" || die "cannot relink $MANUAL_NAME"
    echo "  ℹ $MANUAL_NAME hard link had split with identical content; relinked"
    return
  fi
  die "$MANUAL_NAME agent entry and repository manual differ. Compare them before running ./publish.sh --relink."
}

relink_manual() {
  local src="$AGENTS/$MANUAL_NAME.md"
  local agent="$HOME/.claude/agents/$MANUAL_NAME.md"
  [ -e "$src" ] || die "missing manual: manuals/$MANUAL_NAME.md"
  if [ -e "$agent" ] && [ "$agent" -ef "$src" ]; then
    echo "✓ $MANUAL_NAME is already linked to this repository"
    return
  fi
  rm -f "$agent" && ln "$src" "$agent" || die "cannot relink $MANUAL_NAME"
  echo "✓ $MANUAL_NAME now points only to $ROOT"
}

run_book_tool() {
  local tool="$1" dir="$2"
  if [ -n "$dir" ]; then
    python3 "$tool" "$dir"
  else
    python3 "$tool"
  fi
}

build_one() {
  local vol="$1" dir="$2" part="$3"
  local figs="${dir:+$dir/}figs.py"
  local verify_log="$LOGDIR/verify-content-$vol.log"
  local html_log="$LOGDIR/html-$vol.log"
  local sections_log="$LOGDIR/sections-$vol.log"
  local refs_log="$LOGDIR/refs-$vol.log"

  say "$vol"
  python3 "$figs" >/dev/null || die "$vol image generation failed"
  if run_book_tool verify_content.py "$dir" >"$verify_log" 2>&1; then
    grep -E "WARN" "$verify_log" || true
    echo "  ✓ $vol source-content verification passed ($(grep -c PASS "$verify_log") PASS)"
  else
    grep -E "FAIL" "$verify_log" || true
    die "$vol source-content verification failed; see $verify_log"
  fi
  if python3 audit_sections.py --vol "$vol" >"$sections_log" 2>&1; then
    echo "  ✓ $vol section-reference audit passed"
  else
    cat "$sections_log"
    die "$vol section-reference audit failed"
  fi
  if python3 audit_refs.py --vol "$vol" >"$refs_log" 2>&1; then
    echo "  ✓ $vol semantic-reference audit completed"
  else
    cat "$refs_log"
    die "$vol semantic-reference audit failed"
  fi
  run_book_tool export_manuscript.py "$dir" >/dev/null || die "$vol manuscript export failed"
  if [ -n "$dir" ]; then
    python3 export_html.py "$dir" --all >/dev/null || die "$vol HTML build failed"
    python3 verify_html.py "$dir" >"$html_log" 2>&1 || {
      grep -E "FAIL" "$html_log" || true
      die "$vol HTML verification failed; see $html_log"
    }
  else
    python3 export_html.py --all >/dev/null || die "$vol HTML build failed"
    python3 verify_html.py >"$html_log" 2>&1 || {
      grep -E "FAIL" "$html_log" || true
      die "$vol HTML verification failed; see $html_log"
    }
  fi
  echo "  ✓ $vol MathJax HTML verification passed ($(grep -c '^PASS ' "$html_log") PASS)"
  [ -n "$part" ] || die "$vol has no manuscript label in project.conf"
}

build_selected_volume() {
  local wanted="$1" spec vol dir part
  for spec in "${VOLS[@]}"; do
    IFS='|' read -r vol dir part <<<"$spec"
    if [ "$vol" = "$wanted" ]; then
      build_one "$vol" "$dir" "$part"
      return
    fi
  done
  die "$wanted is outside $PROJECT_NAME; allowed volumes: $ALLOWED_VOLS"
}

build_project() {
  local spec vol dir part
  check_manual_link
  for spec in "${VOLS[@]}"; do
    IFS='|' read -r vol dir part <<<"$spec"
    build_one "$vol" "$dir" "$part"
  done
}

package_sources() {
  say "package $PROJECT_NAME sources"
  COPYFILE_DISABLE=1 tar -cf - "${SOURCE_FILES[@]}" | gzip -n >"$TARBALL" || die "source package failed"
  echo "  ✓ $TARBALL ($(tar -tzf "$TARBALL" | grep -c .) entries)"
}

verify_delivery_items() {
  local item src total="${#DRIVE_ITEMS[@]}" missing=0
  say "$PROJECT_NAME delivery set"
  for item in "${DRIVE_ITEMS[@]}"; do
    IFS='|' read -r src _ _ <<<"$item"
    [ -f "$src" ] || { echo "  ✗ missing $src"; missing=1; }
  done
  [ "$missing" -eq 0 ] || die "delivery set is incomplete"
  echo "  ✓ $total project-local delivery items present"
}

check_remote_raw() {
  local src="$1" dst="$2" local_md5 remote_md5
  local_md5="$(md5 -q "$src" 2>/dev/null || md5sum "$src" | cut -d' ' -f1)" \
    || die "cannot hash $src"
  remote_md5="$("$RCLONE" lsjson "Gdrive:$dst" --drive-root-folder-id="$DRIVE_ID" \
    --stat --hash | python3 -c 'import json,sys; print(json.load(sys.stdin).get("Hashes",{}).get("md5",""))')" \
    || die "cannot re-read Drive hash for $dst"
  [ -n "$remote_md5" ] && [ "$remote_md5" = "$local_md5" ] \
    || die "$dst md5 mismatch after upload"
  echo "  ✓ $dst md5 verified"
}

upload_project() {
  local item src dst kind total="${#DRIVE_ITEMS[@]}" uploaded=0
  [ -x "$RCLONE" ] || die "rclone not found at $RCLONE"

  say "upload only $PROJECT_NAME"
  trap '[ "${uploaded:-0}" -gt 0 ] && [ "${uploaded:-0}" -lt "${total:-0}" ] && echo "⚠ uploaded ${uploaded}/${total} items; rerun this project upload to finish" >&2' EXIT
  for item in "${DRIVE_ITEMS[@]}"; do
    IFS='|' read -r src dst kind <<<"$item"
    [ "$kind" = "raw" ] || die "unsupported delivery kind: $kind"
    if "$RCLONE" copyto "$src" "Gdrive:$dst" --drive-root-folder-id="$DRIVE_ID"; then
      uploaded=$((uploaded + 1))
      echo "  ✓ $dst"
    else
      echo "  ✗ $dst"
    fi
  done
  [ "$uploaded" -eq "$total" ] || die "uploaded only $uploaded/$total project items"

  say "Drive byte verification"
  for item in "${DRIVE_ITEMS[@]}"; do
    IFS='|' read -r src dst kind <<<"$item"
    check_remote_raw "$src" "$dst"
  done
  trap - EXIT
  echo; echo "✓ uploaded $PROJECT_NAME only; no sibling project was built or uploaded"
}

publish_web() {
  [ -n "${WEB_SRC:-}" ] || die "$PROJECT_NAME has no web asset"
  [ -n "${WEB_CHECK:-}" ] || die "WEB_CHECK is missing from project.conf"
  say "web asset verification"
  python3 "$WEB_CHECK" "$WEB_SRC" || die "web asset verification failed"
  if [ "${2:-}" = "--check-only" ]; then
    echo; echo "✓ checked locally; not uploaded"
    return
  fi
  [ -x "$RCLONE" ] || die "rclone not found at $RCLONE"
  "$RCLONE" copyto "$WEB_SRC" "Gdrive:$WEB_DRIVE" --drive-root-folder-id="$DRIVE_ID" || die "Drive web upload failed"
  local local_md5 online_md5 tmp
  local_md5="$(md5 -q "$WEB_SRC" 2>/dev/null || md5sum "$WEB_SRC" | cut -d' ' -f1)"
  scp -q "$WEB_SRC" "$WEB_HOST:$WEB_PATH/.index.html.new" || die "web scp failed"
  ssh "$WEB_HOST" "set -e; cd '$WEB_PATH'; NEW=\$(md5sum .index.html.new | cut -d' ' -f1); [ \"\$NEW\" = '$local_md5' ]; mkdir -p /var/backups/book; chmod 700 /var/backups/book; [ -f index.html ] && cp -a index.html /var/backups/book/index.html.bak-\$(date +%Y%m%d-%H%M%S); chmod 644 .index.html.new; mv -f .index.html.new index.html" || die "web deployment failed"
  tmp="$(mktemp -t daisy-web)" || die "cannot create web check file"
  curl -sS -m 30 -o "$tmp" "$WEB_URL" || die "cannot read deployed web page"
  online_md5="$(md5 -q "$tmp" 2>/dev/null || md5sum "$tmp" | cut -d' ' -f1)"
  rm -f "$tmp"
  [ "$online_md5" = "$local_md5" ] || die "deployed web page differs from local source"
  echo "✓ web asset deployed and byte-verified at $WEB_URL"
}

case "${1:-}" in
  "")
    build_project
    package_sources
    verify_delivery_items
    echo; echo "✓ $PROJECT_NAME is green locally; Drive was not touched"
    ;;
  --vol)
    [ -n "${2:-}" ] || die "--vol needs one of: $ALLOWED_VOLS"
    check_manual_link
    build_selected_volume "$2"
    echo; echo "✓ $2 completed locally; Drive was not touched"
    ;;
  --upload)
    build_project
    package_sources
    verify_delivery_items
    upload_project
    ;;
  --relink)
    relink_manual
    ;;
  --docx|--pdf|--deliver)
    die "$1 is retired: this project now produces raw HTML and never creates Google Docs, DOCX, or PDF"
    ;;
  --web)
    publish_web "$@"
    ;;
  -h|--help)
    usage
    ;;
  *)
    usage >&2
    die "unknown option: $1"
    ;;
esac
