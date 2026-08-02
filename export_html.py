#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 content/*.md 导成自包含的 HTML（单篇或整册）。

和 build_docx.py 同源同标记：**粗** ~下标~ ^上标^ [[分数]] [[m:矩阵]]，
块级 # / ## / ### / FIG: / BOX[...] / TABLE: / CENTER: / - / ---。
之所以不从 Doc 里往外拷：Doc 一拷出来，橙蓝灰三种盒子、上下排的分数、
下标和插图全丢，只剩一堆散字。从源码渲染才和 Doc 是同一份内容。

  python3 export_html.py            --file 02-cauchy.md      # 第一册某一篇
  python3 export_html.py vol2 --all                          # 整册
输出默认落在 <册>/html/ 下。图片按 base64 内嵌，单文件可直接发人。
"""
import os
import re
import sys
import glob
import html
import base64
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))

# 盒子：填充色、描边/标题色。取值与 build_docx.py 的 BOXES 一一对应，改一边要改两边。
BOXES = {
    'remember': ('#DCE7F7', '#1F3A6E', '#0F2547'),   # 蓝：必须记住
    'dialog':   ('#FBE3D6', '#C05A24', '#8A3D14'),   # 橙：对话
    'task':     ('#FDF0E4', '#C05A24', '#8A3D14'),   # 橙：留给姐姐妹妹
    'grown':    ('#EDEFF2', '#6B7480', '#454C55'),   # 灰：长大以后
    'key':      ('#E3F1E9', '#1E7A50', '#125437'),   # 绿：这一章的关键
}

TOKEN = re.compile(r'(\*\*.+?\*\*|~[^~]+~|\^[^^]+\^|\[\[[^\]]+\]\])')

# 分数内部是 mathtext。这里只认书里真用到的那几种写法，遇到没见过的就当场报错，
# 绝不静悄悄渲染成别的东西 —— 下标写成 ~n~ 被静默吞掉那次，就是这么丢的。
MATH_CMD = {'times': '×', 'cdot': '·', 'pm': '±', 'le': '≤', 'ge': '≥',
            'neq': '≠', 'approx': '≈', 'ldots': '……', 'dots': '……'}


def mathtext_to_html(s, where=''):
    """mathtext 片段 → HTML：^{n} 和 ^n 变上标，_{n} 变下标，\\sqrt{} 变根号。"""
    out, i, s = [], 0, s.strip()
    while i < len(s):
        c = s[i]
        if c in '^_':
            tag = 'sup' if c == '^' else 'sub'
            i += 1
            if i < len(s) and s[i] == '{':
                j = s.find('}', i)
                if j < 0:
                    raise SystemExit('分数里的花括号没闭合：%s（%s）' % (s, where))
                inner, i = s[i + 1:j], j + 1
            elif i < len(s):
                inner, i = s[i], i + 1
            else:
                raise SystemExit('分数里 %s 后面没东西：%s（%s）' % (c, s, where))
            out.append('<%s>%s</%s>' % (tag, mathtext_to_html(inner, where), tag))
        elif c == '\\':
            m = re.match(r'\\([a-zA-Z]+)', s[i:])
            if not m:
                raise SystemExit('分数里认不出的反斜杠：%s（%s）' % (s, where))
            name = m.group(1)
            i += len(m.group(0))
            if name == 'sqrt':
                if i < len(s) and s[i] == '{':
                    j = s.find('}', i)
                    inner, i = s[i + 1:j], j + 1
                else:
                    inner, i = s[i], i + 1
                out.append('<span class="sqrt">%s</span>'
                           % mathtext_to_html(inner, where))
            elif name in MATH_CMD:
                out.append(MATH_CMD[name])
            else:
                raise SystemExit(
                    '分数里没见过的 mathtext 命令 \\%s：%s（%s）\n'
                    '  要么在 export_html.py 的 MATH_CMD 里加一条，要么换个写法。'
                    % (name, s, where))
        elif c == '{' or c == '}':
            i += 1                      # 纯分组括号，HTML 里不需要
        else:
            out.append(html.escape(c))
            i += 1
    return ''.join(out)


def split_frac(body):
    """[[1/2]] 数字分数；[[1|2^n]] 通式，竖线分隔。与 build_docx.split_frac 同规则。"""
    num, den = body.split('|', 1) if '|' in body else body.split('/', 1)
    return num.strip(), den.strip()


def frac_html(body, where=''):
    num, den = split_frac(body)
    return ('<span class="frac"><span class="num">%s</span>'
            '<span class="den">%s</span></span>'
            % (mathtext_to_html(num, where), mathtext_to_html(den, where)))


def matrix_html(body, where=''):
    rows = [[mathtext_to_html(c, where) for c in r.split(',')]
            for r in body.split(';')]
    cells = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r)
                    for r in rows)
    return ('<span class="mat"><span class="brk">[</span>'
            '<table>%s</table><span class="brk">]</span></span>' % cells)


def rich(text, where=''):
    """行内标记 → HTML。粗体递归解析（**s~n~** 里的下标不能被吞掉）。"""
    text = text.replace('{{', '').replace('}}', '')
    out = []
    for piece in TOKEN.split(text):
        if not piece:
            continue
        if piece.startswith('**') and piece.endswith('**') and len(piece) > 4:
            out.append('<strong>%s</strong>' % rich(piece[2:-2], where))
        elif piece.startswith('[[') and piece.endswith(']]'):
            body = piece[2:-2]
            out.append(matrix_html(body[2:], where) if body.startswith('m:')
                       else frac_html(body, where))
        elif piece.startswith('~') and piece.endswith('~'):
            out.append('<sub>%s</sub>' % html.escape(piece[1:-1]))
        elif piece.startswith('^') and piece.endswith('^'):
            out.append('<sup>%s</sup>' % html.escape(piece[1:-1]))
        else:
            out.append(html.escape(piece))
    return ''.join(out)


def img_data_uri(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()


def render(lines, figdir, where):
    out, i = [], 0
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
            spec = s[4:].split('|')
            fname = spec[0].strip()
            cap = spec[1].strip() if len(spec) > 1 else ''
            path = os.path.join(figdir, fname)
            if not os.path.exists(path):
                raise SystemExit('缺图：' + path)
            out.append('<figure><img alt="%s" src="%s">%s</figure>'
                       % (html.escape(cap or fname), img_data_uri(path),
                          '<figcaption>%s</figcaption>' % rich(cap, loc) if cap else ''))
        elif s.startswith('BOX['):
            m = re.match(r'BOX\[(\w+)\]:\s*(.*?)\s*::\s*(.*)$', s)
            if not m:
                raise SystemExit('盒子写法不对：' + loc)
            kind, title, body = m.group(1), m.group(2), m.group(3)
            fill, edge, tcol = BOXES.get(kind, BOXES['remember'])
            parts = ['<div class="box box-%s">' % kind]
            if title:
                parts.append('<p class="box-t">%s</p>' % rich(title, loc))
            for seg in body.split('//'):
                seg = seg.strip()
                parts.append('<p>%s</p>' % (rich(seg, loc) if seg else '&nbsp;'))
            parts.append('</div>')
            out.append(''.join(parts))
        elif s == 'TABLE:':
            rows, i = [], i + 1
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = lines[i].strip().replace(r'\|', '\x00')
                row = re.sub(r'\[\[[^\]]+\]\]',
                             lambda m: m.group(0).replace('|', '\x01'), row)
                rows.append([c.strip().replace('\x00', '|').replace('\x01', '|')
                             for c in row.strip('|').split('|')])
                i += 1
            head = ''.join('<th>%s</th>' % rich(c, loc) for c in rows[0])
            body = ''.join('<tr>%s</tr>'
                           % ''.join('<td>%s</td>' % rich(c, loc) for c in r)
                           for r in rows[1:])
            out.append('<table class="grid"><thead><tr>%s</tr></thead>'
                       '<tbody>%s</tbody></table>' % (head, body))
            continue
        elif s.startswith('- '):
            items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                items.append('<li>%s</li>' % rich(lines[i].strip()[2:], loc))
                i += 1
            out.append('<ul>%s</ul>' % ''.join(items))
            continue
        elif s == '---':
            out.append('<p class="sep">· · ·</p>')
        elif s.startswith('CENTER:'):
            out.append('<p class="center">%s</p>' % rich(s[7:].strip(), loc))
        elif s.startswith('TITLE:'):
            out.append('<p class="booktitle">%s</p>' % rich(s[6:].strip(), loc))
        elif s.startswith('SUB:'):
            out.append('<p class="booksub">%s</p>' % rich(s[4:].strip(), loc))
        else:
            out.append('<p>%s</p>' % rich(s, loc))
        i += 1
    return '\n'.join(out)


CSS = """
:root{--bg:#fbfaf7;--fg:#222;--navy:#1F3A6E;--grey:#6B7480;--rule:#e3ded3;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
 font-family:"Hiragino Sans GB","Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;
 font-size:17px;line-height:1.95;}
article{max-width:44rem;margin:0 auto;padding:2.6rem 1.25rem 5rem;}
.crumb{font-size:.82rem;color:var(--grey);letter-spacing:.04em;margin:0 0 .4rem;}
h1{font-size:1.72rem;line-height:1.4;color:var(--navy);margin:.2rem 0 1.4rem;
 padding-bottom:.7rem;border-bottom:2px solid var(--navy);}
h2{font-size:1.24rem;color:var(--navy);margin:2.6rem 0 .9rem;}
h3{font-size:1.05rem;color:var(--navy);margin:1.9rem 0 .7rem;font-weight:600;}
p{margin:0 0 1.05rem;}
strong{font-weight:700;}
ul{margin:0 0 1.05rem;padding-left:1.4rem;} li{margin:.3rem 0;}
.center{text-align:center;color:var(--navy);font-size:1.1rem;margin:1.5rem 0;}
.sep{text-align:center;color:var(--grey);letter-spacing:.5em;margin:1.6rem 0;}
.booktitle{text-align:center;font-size:1.9rem;color:var(--navy);font-weight:700;}
.booksub{text-align:center;color:var(--grey);}
figure{margin:1.7rem 0;text-align:center;}
figure img{max-width:100%;height:auto;border-radius:4px;}
figcaption{font-size:.86rem;color:var(--grey);line-height:1.6;margin-top:.5rem;}
.box{border-left:4px solid;border-radius:6px;padding:.9rem 1.1rem .55rem;
 margin:1.5rem 0;font-size:.97rem;line-height:1.85;}
.box p{margin:0 0 .5rem;} .box-t{font-weight:700;margin-bottom:.55rem !important;}
.box-remember{background:#DCE7F7;border-color:#1F3A6E;} .box-remember .box-t{color:#0F2547;}
.box-dialog{background:#FBE3D6;border-color:#C05A24;}   .box-dialog .box-t{color:#8A3D14;}
.box-task{background:#FDF0E4;border-color:#C05A24;}     .box-task .box-t{color:#8A3D14;}
.box-grown{background:#EDEFF2;border-color:#6B7480;}    .box-grown .box-t{color:#454C55;}
.box-key{background:#E3F1E9;border-color:#1E7A50;}      .box-key .box-t{color:#125437;}
.frac{display:inline-flex;flex-direction:column;align-items:center;
 vertical-align:-0.52em;margin:0 .18em;line-height:1.15;font-size:.86em;}
.frac .num{padding:0 .28em;}
.frac .den{padding:0 .28em;border-top:1.4px solid currentColor;}
sub,sup{font-size:.72em;line-height:0;}
.sqrt{border-top:1.2px solid currentColor;padding:0 .12em;}
.sqrt::before{content:"√";border-top:none;margin-left:-.1em;}
.mat{display:inline-flex;align-items:center;vertical-align:middle;font-size:.9em;}
.mat .brk{font-size:2.1em;font-weight:300;line-height:1;}
.mat table{border:none;margin:0 .12em;} .mat td{padding:0 .3em;text-align:center;border:none;}
table.grid{border-collapse:collapse;width:100%;margin:1.4rem 0;font-size:.93rem;}
table.grid th,table.grid td{border:1px solid var(--rule);padding:.45rem .6rem;
 text-align:left;vertical-align:top;}
table.grid th{background:#f1ece1;color:var(--navy);}
.tail{margin-top:3.5rem;padding-top:1rem;border-top:1px solid var(--rule);
 font-size:.8rem;color:var(--grey);line-height:1.7;}
.scroll{overflow-x:auto;}
@media (max-width:600px){body{font-size:16px}article{padding:1.6rem 1rem 3rem}}
@media (prefers-color-scheme:dark){
 :root{--bg:#16181c;--fg:#e6e3dc;--navy:#9dbaf0;--grey:#9aa2ad;--rule:#333840;}
 .box-remember{background:#1b2740;} .box-dialog,.box-task{background:#33231a;}
 .box-grown{background:#24272c;} .box-key{background:#152a20;}
 .box-remember .box-t{color:#a8c4ee;} .box-dialog .box-t,.box-task .box-t{color:#e0a077;}
 .box-grown .box-t{color:#aab2bd;} .box-key .box-t{color:#7fc3a1;}
 table.grid th{background:#22262c;}
 figure img{filter:brightness(.92);}
}
@media print{body{background:#fff}.box{break-inside:avoid}figure{break-inside:avoid}}
"""

PAGE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title><style>%(css)s</style></head>
<body><article>
<p class="crumb">%(crumb)s</p>
%(body)s
<p class="tail">%(tail)s</p>
</article></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('vol', nargs='?', default='', help='分册目录，如 vol2；省略＝第一册')
    ap.add_argument('--file', help='只导一篇，如 02-cauchy.md')
    ap.add_argument('--all', action='store_true', help='整册')
    ap.add_argument('-o', '--out', help='输出路径')
    a = ap.parse_args()

    book = os.path.join(HERE, a.vol) if a.vol else HERE
    content, figdir = os.path.join(book, 'content'), os.path.join(book, 'figs')
    tpath = os.path.join(book, 'TITLE')
    booktitle = (open(tpath, encoding='utf-8').read().strip()
                 if os.path.exists(tpath) else '不能做完无穷，怎么谈论无穷')

    if a.file:
        files = [os.path.join(content, os.path.basename(a.file))]
        if not os.path.exists(files[0]):
            raise SystemExit('没有这个文件：' + files[0])
    elif a.all:
        files = sorted(glob.glob(os.path.join(content, '*.md')))
    else:
        raise SystemExit('要么 --file <篇>，要么 --all')

    body, first = [], None
    for p in files:
        lines = open(p, encoding='utf-8').read().split('\n')
        for ln in lines:
            if ln.startswith('# '):
                first = first or ln[2:].strip()
                break
        body.append(render(lines, figdir, os.path.basename(p)))

    title = ('%s · %s' % (booktitle, first)) if a.file else booktitle
    page = PAGE % {
        'title': html.escape(title),
        'css': CSS,
        'crumb': html.escape('《%s》' % booktitle),
        'body': '\n'.join(body),
        'tail': html.escape(
            '《数学概念笔记》第一册' if not a.vol else '《数学概念笔记》'
        ) + ' — 由 export_html.py 从 content/ 源码直接渲染，与同名 Google Doc 同源同内容。',
    }
    out = a.out or os.path.join(book, 'html', re.sub(r'[\\/]', '_', title) + '.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(page)
    print('wrote %s  (%.0f KB)' % (out, os.path.getsize(out) / 1024.0))


if __name__ == '__main__':
    main()
