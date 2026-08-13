#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 content/*.md 导成以 MathJax 为唯一数学排版引擎的 HTML。

正文汉字仍是可换行、可搜索的普通 HTML；坐标、数字、变量、算式、上下标、
分数、量纲、向量和矩阵统一写成 TeX，由 MathJax 4 输出 SVG。插图按 base64
内嵌，因此成书仍是一个 HTML 文件，联网时只需加载固定版本的 MathJax。

  python3 export_html.py vol4 --file 03-space.md
  python3 export_html.py vol4 --all
"""

import argparse
import base64
import glob
import html
import os
import re


HERE = os.path.dirname(os.path.abspath(__file__))
MATHJAX_VERSION = '4.0.0'
MATHJAX_URL = (
    'https://cdn.jsdelivr.net/npm/mathjax@%s/tex-svg.js' % MATHJAX_VERSION
)

# 盒子种类是源稿语义的一部分；颜色由本 HTML 样式统一定义。
BOXES = {'remember', 'dialog', 'task', 'grown', 'key'}
STRONG_RE = re.compile(r'\*\*(.+?)\*\*')
SPECIAL_RE = re.compile(
    r'(`[^`]*`|https?://[^\s<>"“”]+|'
    r'\[\[[^\]]+\]\](?:\^[^^]+\^|[⁻¹ᵀ′]+)*)'
)

# 这些是正文里确实作为一个数学对象使用的多字母记号。普通英文术语（array、
# eigenspace、PageRank、GPU、CT 等）不在这里，仍由正文字体排。
MATH_WORDS = set()

PLAIN_TOKEN_RE = re.compile(
    r'(?P<label>(?<![A-Za-z0-9])[ABC]\d+(?![A-Za-z0-9]))'
    r'|(?P<sub>~[^~]+~)'
    r'|(?P<sup>\^[^^]+\^)'
    r'|(?P<number>\d+(?:\.\d+)?)'
    r'|(?P<word>[A-Za-z]+)'
    r'|(?P<greek>[Σελπ])'
    r'|(?P<super>[⁻¹²³ᵀ]+)'
    r'|(?P<op>[×＝＋−－+*/=·≠≤≥→⟺√±|])'
    r'|(?P<degree>°)'
    r'|(?P<bridge>[()\[\],\s\u3000…–′])'
    r'|(?P<other>.)',
    re.DOTALL,
)


def split_frac(body):
    """[[1/2]] 用斜线分源码字段；[[1|2^n]] 用竖线避开复杂分母。"""
    if '|' in body:
        return [part.strip() for part in body.split('|', 1)]
    if '/' in body:
        return [part.strip() for part in body.split('/', 1)]
    raise SystemExit('分数没有分隔线：[[%s]]' % body)


def matrix_shape(body):
    rows = [row.split(',') for row in body.split(';')]
    widths = {len(row) for row in rows}
    return len(rows), max(widths), len(widths) == 1


def tex_text(value):
    """把量纲里的汉字安全地放进 \text{...}。"""
    replacements = {
        '\\': r'\textbackslash{}', '{': r'\{', '}': r'\}',
        '%': r'\%', '#': r'\#', '&': r'\&', '_': r'\_',
        '^': r'\textasciicircum{}', '~': r'\textasciitilde{}',
    }
    return ''.join(replacements.get(ch, ch) for ch in value)


def tex_mathtext(value):
    """把源码 mathtext/Unicode 规范成 MathJax TeX；已有 \frac 等命令保留。"""
    value = value.strip()
    replacements = (
        ('⟺', r'\Longleftrightarrow '), ('→', r'\to '),
        ('≠', r'\ne '), ('≤', r'\le '), ('≥', r'\ge '),
        ('×', r'\times '), ('·', r'\cdot '), ('±', r'\pm '),
        ('＋', '+'), ('−', '-'), ('－', '-'), ('＝', '='),
        ('⁻¹', r'^{-1}'), ('ᵀ', r'^{\mathsf T}'), ('′', r'^{\prime}'),
        ('ε', r'\varepsilon '), ('λ', r'\lambda '), ('π', r'\pi '),
    )
    for old, new in replacements:
        value = value.replace(old, new)
    return value


def marker_to_tex(body, suffix=''):
    """返回 (TeX, kind, matrix_body_or_None)。"""
    matrix_body = None
    if body.startswith('m:'):
        matrix_body = body[2:]
        rows = [row.split(',') for row in matrix_body.split(';')]
        tex = r'\begin{bmatrix}' + r'\\'.join(
            '&'.join(tex_mathtext(cell) for cell in row) for row in rows
        ) + r'\end{bmatrix}'
        kind = 'matrix'
    else:
        text_fraction = body.startswith('t:')
        if text_fraction:
            body = body[2:]
        num, den = split_frac(body)
        if text_fraction:
            tex = r'\frac{\text{%s}}{\text{%s}}' % (
                tex_text(num), tex_text(den))
            kind = 'dimension-fraction'
        else:
            tex = r'\frac{%s}{%s}' % (
                tex_mathtext(num), tex_mathtext(den))
            kind = 'fraction'
    if suffix:
        tex += tex_from_plain(suffix)
    return tex, kind, matrix_body


def tex_from_plain(value):
    """源码中的普通数学片段（如 (3, 2)、A^2^、3×2）转成 TeX。"""
    out = []
    i = 0
    while i < len(value):
        ch = value[i]
        if ch in '~^':
            end = value.find(ch, i + 1)
            if end < 0:
                # verify_html.py 会把残留标记判为失败；这里也尽早给出位置无关错误。
                raise SystemExit('上下标没有闭合：%s' % value)
            inner = tex_from_plain(value[i + 1:end])
            out.append('_{%s}' % inner if ch == '~' else '^{%s}' % inner)
            i = end + 1
            continue
        if value.startswith('⁻¹', i):
            out.append(r'^{-1}')
            i += 2
            continue
        if ch == 'ᵀ':
            out.append(r'^{\mathsf T}')
        elif ch in '¹²³':
            out.append('^{%s}' % {'¹': '1', '²': '2', '³': '3'}[ch])
        elif ch == '′':
            out.append(r'^{\prime}')
        elif ch == '√':
            m = re.match(r'√\s*([A-Za-z0-9]+)', value[i:])
            if m:
                out.append(r'\sqrt{%s}' % m.group(1))
                i += len(m.group(0))
                continue
            out.append(r'\sqrt{\vphantom{x}}')
        elif value.startswith('det', i) and (
                i == 0 or not value[i - 1].isalpha()) and (
                i + 3 == len(value) or not value[i + 3].isalpha()):
            out.append(r'\operatorname{det}')
            i += 3
            continue
        elif ch == 'Σ':
            out.append(r'\sum ' if value[i + 1:i + 2] == '~' else r'\Sigma ')
        elif ch == 'ε':
            out.append(r'\varepsilon ')
        elif ch == 'λ':
            out.append(r'\lambda ')
        elif ch == 'π':
            out.append(r'\pi ')
        elif ch == '×':
            out.append(r'\times ')
        elif ch == '·':
            out.append(r'\cdot ')
        elif ch == '＝':
            out.append('=')
        elif ch == '＋':
            out.append('+')
        elif ch in '−－–':
            out.append('-')
        elif ch == '≠':
            out.append(r'\ne ')
        elif ch == '≤':
            out.append(r'\le ')
        elif ch == '≥':
            out.append(r'\ge ')
        elif ch == '→':
            out.append(r'\to ')
        elif ch == '⟺':
            out.append(r'\Longleftrightarrow ')
        elif ch == '±':
            out.append(r'\pm ')
        elif ch == '°':
            out.append(r'^{\circ}')
        elif ch == '…':
            out.append(r'\ldots ')
        elif ch == '\u3000':
            out.append(r'\qquad ')
        elif ch.isspace():
            # TeX 会吞普通空格；显式薄空格保留源码里的视觉分组。
            out.append(r'\,')
        elif ch in '&%#{}_$':
            out.append('\\' + ch)
        else:
            out.append(ch)
        i += 1
    return ''.join(out)


def math_span(tex, kind='plain', shape=None):
    classes = ['math-inline']
    attrs = ['data-math="true"', 'data-math-kind="%s"' % kind]
    if shape:
        attrs.append('data-matrix-shape="%s"' % shape)
    attrs.append('data-tex="%s"' % html.escape(tex, quote=True))
    return '<span class="%s" %s>\\(%s\\)</span>' % (
        ' '.join(classes), ' '.join(attrs), html.escape(tex))


def token_is_math(match):
    kind = match.lastgroup
    value = match.group(0)
    if kind in {'number', 'sub', 'sup', 'greek', 'super', 'op', 'degree'}:
        return True
    if kind == 'word':
        return len(value) == 1 or value in MATH_WORDS
    return False


def plain_math_html(text):
    """把普通文本中的数学串送进 MathJax，汉字和英文术语留在 HTML。"""
    matches = list(PLAIN_TOKEN_RE.finditer(text))
    if not matches:
        return ''
    out = []
    run = []
    run_has_math = False

    def flush():
        nonlocal run, run_has_math
        if not run:
            return
        raw = ''.join(m.group(0) for m in run)
        if run_has_math:
            leading = re.match(r'^[\s\u3000]+', raw)
            trailing = re.search(r'[\s\u3000]+$', raw)
            left = leading.group(0) if leading else ''
            right = trailing.group(0) if trailing else ''
            core_end = len(raw) - len(right) if right else len(raw)
            core = raw[len(left):core_end]
            out.append(html.escape(left))
            if core:
                out.append(math_span(tex_from_plain(core)))
            out.append(html.escape(right))
        else:
            out.append(html.escape(raw))
        run = []
        run_has_math = False

    for match in matches:
        kind = match.lastgroup
        if kind == 'label' or kind == 'other' or (
                kind == 'word' and not token_is_math(match)):
            flush()
            out.append(html.escape(match.group(0)))
        else:
            run.append(match)
            run_has_math = run_has_math or token_is_math(match)
    flush()
    return ''.join(out)


def rich(text, where=''):
    """解析粗体和轻标记；所有数学节点最终都是 MathJax TeX。"""
    del where  # 保留调用签名，方便构建错误时重新加精确位置。
    text = re.sub(r'\{\{(.*?)\}\}', r'\1', text)
    def render_special(piece):
        if piece.startswith('`') and piece.endswith('`'):
            return '<code>%s</code>' % html.escape(piece[1:-1])
        if piece.startswith('http://') or piece.startswith('https://'):
            escaped = html.escape(piece, quote=True)
            return '<a href="%s">%s</a>' % (escaped, html.escape(piece))
        marker = re.match(r'^\[\[([^\]]+)\]\](.*)$', piece, re.DOTALL)
        if not marker:
            return plain_math_html(piece)
        body, suffix = marker.group(1), marker.group(2)
        tex, kind, matrix_body = marker_to_tex(body, suffix)
        shape = None
        if matrix_body is not None:
            nr, nc, rectangular = matrix_shape(matrix_body)
            shape = '%dx%d' % (nr, nc) if rectangular else 'irregular'
        return math_span(tex, kind, shape=shape)

    def render_unbold(value):
        parts = []
        for piece in SPECIAL_RE.split(value):
            if piece:
                parts.append(render_special(piece))
        return ''.join(parts)

    out = []
    pos = 0
    for match in STRONG_RE.finditer(text):
        out.append(render_unbold(text[pos:match.start()]))
        out.append('<strong>%s</strong>' % render_unbold(match.group(1)))
        pos = match.end()
    out.append(render_unbold(text[pos:]))
    return ''.join(out)


def img_data_uri(path):
    with open(path, 'rb') as handle:
        return 'data:image/png;base64,' + base64.b64encode(handle.read()).decode()


def alt_text(value):
    value = re.sub(r'\*\*(.+?)\*\*', r'\1', value)
    value = re.sub(r'\[\[m:([^\]]+)\]\]', r'[\1]', value)
    value = re.sub(r'\[\[t:([^|]+)\|([^\]]+)\]\]', r'\1／\2', value)
    value = re.sub(r'\[\[([^\]]+)\]\]', r'\1', value)
    return re.sub(r'[~^]([^~^]+)[~^]', r'\1', value)


def render(lines, figdir, where):
    out = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        loc = '%s:%d' % (where, i + 1)
        if s.startswith('### '):
            out.append('<h3>%s</h3>' % rich(s[4:], loc))
        elif s.startswith('## '):
            out.append('<h2>%s</h2>' % rich(s[3:], loc))
        elif s.startswith('# '):
            out.append('<h1>%s</h1>' % rich(s[2:], loc))
        elif s.startswith('FIG:'):
            spec = s[4:].split('|', 1)
            fname = spec[0].strip()
            caption = spec[1].strip() if len(spec) > 1 else ''
            path = os.path.join(figdir, fname)
            if not os.path.exists(path):
                raise SystemExit('缺图：' + path)
            out.append(
                '<figure><img loading="lazy" alt="%s" src="%s">%s</figure>' % (
                    html.escape(alt_text(caption or fname), quote=True),
                    img_data_uri(path),
                    '<figcaption>%s</figcaption>' % rich(caption, loc)
                    if caption else '',
                )
            )
        elif s.startswith('BOX['):
            match = re.match(r'BOX\[(\w+)\]:\s*(.*?)\s*::\s*(.*)$', s)
            if not match:
                raise SystemExit('盒子写法不对：' + loc)
            kind, title, body = match.group(1), match.group(2), match.group(3)
            if kind not in BOXES:
                raise SystemExit('未知盒子 %s：%s' % (kind, loc))
            parts = ['<aside class="box box-%s">' % kind]
            if title:
                parts.append('<p class="box-t">%s</p>' % rich(title, loc))
            for segment in body.split('//'):
                segment = segment.strip()
                formula_region_4x = segment.startswith('FORMULAREGION4:')
                if formula_region_4x:
                    segment = segment[len('FORMULAREGION4:'):].strip()
                cls = ' class="formula-region-4x"' if formula_region_4x else ''
                parts.append('<p%s>%s</p>' % (
                    cls, rich(segment, loc) if segment else '&nbsp;'))
            parts.append('</aside>')
            out.append(''.join(parts))
        elif s == 'TABLE:':
            rows = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = lines[i].strip().replace(r'\|', '\x00')
                row = re.sub(
                    r'\[\[[^\]]+\]\]',
                    lambda m: m.group(0).replace('|', '\x01'), row)
                rows.append([
                    cell.strip().replace('\x00', '|').replace('\x01', '|')
                    for cell in row.strip('|').split('|')
                ])
                i += 1
            if not rows:
                raise SystemExit('空表格：' + loc)
            head = ''.join('<th>%s</th>' % rich(cell, loc) for cell in rows[0])
            body = ''.join(
                '<tr>%s</tr>' % ''.join(
                    '<td>%s</td>' % rich(cell, loc) for cell in row)
                for row in rows[1:]
            )
            out.append(
                '<div class="table-scroll"><table class="grid">'
                '<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                % (head, body)
            )
            continue
        elif s.startswith('- '):
            items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                item_loc = '%s:%d' % (where, i + 1)
                items.append('<li>%s</li>' % rich(
                    lines[i].strip()[2:], item_loc))
                i += 1
            out.append('<ul>%s</ul>' % ''.join(items))
            continue
        elif s == '---':
            out.append('<p class="sep" aria-hidden="true">· · ·</p>')
        elif s == 'PAGEBREAK':
            out.append('<div class="pagebreak" aria-hidden="true"></div>')
        elif s.startswith('CENTERBIG:'):
            out.append('<p class="center center-big">%s</p>' % rich(
                s[len('CENTERBIG:'):].strip(), loc))
        elif s.startswith('CENTER:'):
            out.append('<p class="center">%s</p>' % rich(
                s[len('CENTER:'):].strip(), loc))
        elif s.startswith('TITLE:'):
            out.append('<p class="booktitle">%s</p>' % rich(
                s[len('TITLE:'):].strip(), loc))
        elif s.startswith('SUB:'):
            out.append('<p class="booksub">%s</p>' % rich(
                s[len('SUB:'):].strip(), loc))
        else:
            out.append('<p>%s</p>' % rich(s, loc))
        i += 1
    return '\n'.join(out)


CSS = r"""
:root{--bg:#fbfaf7;--fg:#222;--navy:#1f3a6e;--grey:#6b7480;--rule:#e3ded3;
 --link:#245e9b}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);
 font-family:"Hiragino Sans GB","Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;
 font-size:17px;line-height:1.95;text-rendering:optimizeLegibility}
article{max-width:46rem;margin:0 auto;padding:2.6rem 1.25rem 5rem}
.chapter{display:flow-root}
.crumb{font-size:.82rem;color:var(--grey);letter-spacing:.04em;margin:0 0 .4rem}
h1{font-size:1.72rem;line-height:1.4;color:var(--navy);margin:2.8rem 0 1.4rem;
 padding-bottom:.7rem;border-bottom:2px solid var(--navy)}
.chapter:first-of-type h1{margin-top:2rem}
h2{font-size:1.24rem;line-height:1.55;color:var(--navy);margin:2.6rem 0 .9rem}
h3{font-size:1.05rem;line-height:1.55;color:var(--navy);margin:1.9rem 0 .7rem;font-weight:600}
p{margin:0 0 1.05rem}
strong{font-weight:700}
a{color:var(--link);text-underline-offset:.14em;overflow-wrap:anywhere}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.9em}
ul{margin:0 0 1.05rem;padding-left:1.4rem}
li{margin:.3rem 0}
.center{text-align:center;color:var(--navy);font-size:1.1rem;margin:1.5rem 0;
 overflow-x:auto;overflow-y:hidden;padding:.25rem 0 .65rem}
.center-big{font-size:1.38rem;margin:2rem 0}
.sep{text-align:center;color:var(--grey);letter-spacing:.5em;margin:1.6rem 0}
.booktitle{text-align:center;font-size:2.05rem;line-height:1.5;color:var(--navy);
 font-weight:700;margin:4.5rem 0 1.4rem}
.booksub{text-align:center;color:var(--grey);min-height:.5rem}
figure{margin:1.7rem 0;text-align:center;break-inside:avoid}
figure img{max-width:100%;height:auto;border-radius:4px}
figcaption{font-size:.86rem;color:var(--grey);line-height:1.65;margin-top:.5rem}
.box{border-left:4px solid;border-radius:6px;padding:.9rem 1.1rem .55rem;
 margin:1.5rem 0;font-size:.97rem;line-height:1.85;break-inside:avoid-page}
.box p{margin:0 0 .5rem}
.box-t{font-weight:700;margin-bottom:.55rem!important}
.formula-region-4x{min-height:4em;display:flex;align-items:center;justify-content:center;
 overflow-x:auto}
.box-remember{background:#dce7f7;border-color:#1f3a6e}.box-remember .box-t{color:#0f2547}
.box-dialog{background:#fbe3d6;border-color:#c05a24}.box-dialog .box-t{color:#8a3d14}
.box-task{background:#fdf0e4;border-color:#c05a24}.box-task .box-t{color:#8a3d14}
.box-grown{background:#edeff2;border-color:#6b7480}.box-grown .box-t{color:#454c55}
.box-key{background:#e3f1e9;border-color:#1e7a50}.box-key .box-t{color:#125437}

/* 全书数学只有这一条渲染路径：TeX -> MathJax SVG。 */
.math-inline{white-space:nowrap}
.math-inline mjx-container[jax="SVG"]{margin-inline:.04em}
.math-inline mjx-container[jax="SVG"] svg{overflow:visible}

.table-scroll{overflow-x:auto;margin:1.4rem 0}
table.grid{border-collapse:collapse;width:100%;font-size:.93rem;line-height:1.75}
table.grid th,table.grid td{border:1px solid var(--rule);padding:.45rem .6rem;
 text-align:left;vertical-align:top}
table.grid th{background:#f1ece1;color:var(--navy)}
.tail{margin-top:3.5rem;padding-top:1rem;border-top:1px solid var(--rule);
 font-size:.8rem;color:var(--grey);line-height:1.7}
.pagebreak{height:0;margin:0;border:0}
.mathjax-note{font-size:.82rem;color:var(--grey);border:1px solid var(--rule);
 border-radius:5px;padding:.55rem .75rem}
@media (max-width:600px){
 body{font-size:16px}article{padding:1.6rem 1rem 3rem}
 .box{padding-inline:.85rem}.center-big{font-size:1.22rem}
}
@media (prefers-color-scheme:dark){
 :root{--bg:#16181c;--fg:#e6e3dc;--navy:#9dbaf0;--grey:#9aa2ad;
  --rule:#333840;--link:#91b9ea}
 .box-remember{background:#1b2740}.box-dialog,.box-task{background:#33231a}
 .box-grown{background:#24272c}.box-key{background:#152a20}
 .box-remember .box-t{color:#a8c4ee}.box-dialog .box-t,.box-task .box-t{color:#e0a077}
 .box-grown .box-t{color:#aab2bd}.box-key .box-t{color:#7fc3a1}
 table.grid th{background:#22262c}figure img{filter:brightness(.92)}
}
@page{size:A4;margin:18mm 16mm 20mm}
@media print{
 :root{--bg:#fff;--fg:#111;--navy:#1f3a6e;--grey:#555;--rule:#bbb}
 body{background:#fff;font-size:10.5pt;line-height:1.75}
 article{max-width:none;padding:0}.crumb{display:none}
 .chapter+.chapter{break-before:page}.pagebreak{break-after:page}
 h1,h2,h3{break-after:avoid}.box,figure,.table-scroll{break-inside:avoid}
 a{color:inherit;text-decoration:none}.tail{display:none}
}
"""


MATHJAX_CONFIG = r"""
window.DaisyMathLayout = {
  finish() {
    document.documentElement.dataset.mathjaxErrors = String(
      document.querySelectorAll('mjx-merror,[data-mjx-error]').length
    );
    document.documentElement.dataset.mathjaxReady = 'true';
  }
};
window.MathJax = {
  tex: {
    inlineMath: [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']],
    processEscapes: true
  },
  svg: {fontCache: 'global'},
  options: {enableMenu: false},
  startup: {
    pageReady() {
      return MathJax.startup.defaultPageReady().then(() => new Promise((resolve) => {
        requestAnimationFrame(() => {
          window.DaisyMathLayout.finish();
          resolve();
        });
      }));
    }
  }
};
"""


PAGE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="generator" content="DaisyProbability export_html.py + MathJax %(mjver)s">
<title>%(title)s</title>
<style>%(css)s</style>
<script>%(mathjax_config)s</script>
<script defer src="%(mathjax_url)s" crossorigin="anonymous"></script>
</head><body><article>
<p class="crumb">%(crumb)s</p>
<noscript><p class="mathjax-note">本书的数学内容需要 JavaScript 才能由 MathJax 排版。</p></noscript>
%(body)s
<p class="tail">%(tail)s</p>
</article></body></html>
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('vol', nargs='?', default='', help='分册目录，如 vol4')
    parser.add_argument('--file', help='只导一篇，如 02-arith.md')
    parser.add_argument('--all', action='store_true', help='导出整册')
    parser.add_argument('-o', '--out', help='输出 HTML 路径')
    args = parser.parse_args()

    book = os.path.join(HERE, args.vol) if args.vol else HERE
    content = os.path.join(book, 'content')
    figdir = os.path.join(book, 'figs')
    title_path = os.path.join(book, 'TITLE')
    booktitle = (
        open(title_path, encoding='utf-8').read().strip()
        if os.path.exists(title_path) else '数学概念笔记'
    )

    if args.file:
        files = [os.path.join(content, os.path.basename(args.file))]
        if not os.path.exists(files[0]):
            raise SystemExit('没有这个文件：' + files[0])
    elif args.all:
        files = sorted(glob.glob(os.path.join(content, '*.md')))
    else:
        raise SystemExit('要么 --file <篇>，要么 --all')
    if not files:
        raise SystemExit('没有找到 content/*.md：' + content)

    chapters = []
    first_heading = None
    for path in files:
        lines = open(path, encoding='utf-8').read().split('\n')
        for line in lines:
            if line.startswith('# '):
                first_heading = first_heading or line[2:].strip()
                break
        source_name = os.path.basename(path)
        chapters.append(
            '<section class="chapter" data-source="%s">\n%s\n</section>' % (
                html.escape(source_name, quote=True),
                render(lines, figdir, source_name),
            )
        )

    title = '%s · %s' % (booktitle, first_heading) if args.file else booktitle
    page = PAGE % {
        'title': html.escape(title),
        'css': CSS,
        'mathjax_config': MATHJAX_CONFIG,
        'mathjax_url': MATHJAX_URL,
        'mjver': MATHJAX_VERSION,
        'crumb': html.escape('《%s》' % booktitle),
        'body': '\n'.join(chapters),
        'tail': html.escape(
            '《%s》— 正文与插图由 content/ 同源生成；'
            '全部数学内容由 MathJax %s 以 SVG 排版。'
            % (booktitle, MATHJAX_VERSION)
        ),
    }
    out = args.out or os.path.join(
        book, 'html', re.sub(r'[\\/]', '_', title) + '.html')
    outdir = os.path.dirname(os.path.abspath(out))
    os.makedirs(outdir, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as handle:
        handle.write(page)
    print('wrote %s  (%.0f KB, MathJax %s)' % (
        out, os.path.getsize(out) / 1024.0, MATHJAX_VERSION))


if __name__ == '__main__':
    main()
