#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 content/*.md（轻标记）编译成一份带插图的 .docx。

标记：
  # 标题            篇（另起一页）
  ## 标题           节
  ### 标题          小节
  FIG: 文件名 | 图注
  BOX[kind]: 标题 :: 正文（正文里用 // 换行）
  TABLE:  紧跟若干 | a | b | 行，首行为表头，空行结束
  - 列表项
  ---                分隔线
  其余非空行 = 正文段落
行内：**粗体**  a~n~ 下标  2^n^ 上标
"""
import os
import re
import glob
import struct
import hashlib
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import sys
HERE = os.path.dirname(os.path.abspath(__file__))
# 第二个参数指定分册目录（默认当前册）；两册共用同一套管线
BOOK = os.path.join(HERE, sys.argv[1]) if len(sys.argv) > 1 else HERE
FIGDIR = os.path.join(BOOK, 'figs')
FRACDIR = os.path.join(BOOK, 'figs', 'frac')
CONTENT = os.path.join(BOOK, 'content')
TITLE = (open(os.path.join(BOOK, 'TITLE'), encoding='utf-8').read().strip()
         if os.path.exists(os.path.join(BOOK, 'TITLE')) else '给小学生讲微积分（上）')
OUTPUT = os.path.join(BOOK, TITLE + '.docx')
IS_VOL2 = os.path.basename(os.path.normpath(BOOK)) == 'vol2'

# 行内分数图片的总高 = 字号 × 这个倍数。分数是上下两层，本来就比一行字高。
FRAC_SCALE = 1.85

NAVY = RGBColor(0x1F, 0x3A, 0x6E)
ORANGE = RGBColor(0xC0, 0x5A, 0x24)
GREEN = RGBColor(0x1E, 0x7A, 0x50)
GREY = RGBColor(0x6B, 0x74, 0x80)
BLACK = RGBColor(0x22, 0x22, 0x22)

CN_FONT = 'Noto Sans SC'
LAT_FONT = 'Noto Sans SC'
VARIABLE_FONT = 'Georgia'

BOXES = {
    'remember': ('DCE7F7', NAVY),      # 必须记住
    'dialog':   ('FBE3D6', ORANGE),    # 希希开口
    'task':     ('FDF0E4', ORANGE),    # 留给蘩蘩 / 练习
    'grown':    ('EDEFF2', GREY),      # 长大以后的写法
    'key':      ('E3F1E9', GREEN),     # 这一章的关键
}


# ---------------------------------------------------------------- helpers
def set_cell_bg(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hexcolor)
    tcPr.append(shd)


def set_cell_border(cell, hexcolor, sz=12, left_only=False):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement('w:tcBorders')
    edges = ['left'] if left_only else ['top', 'left', 'bottom', 'right']
    for edge in ['top', 'left', 'bottom', 'right']:
        el = OxmlElement('w:' + edge)
        if edge in edges:
            el.set(qn('w:val'), 'single')
            el.set(qn('w:sz'), str(sz if edge != 'left' else sz * 3))
            el.set(qn('w:color'), hexcolor)
        else:
            el.set(qn('w:val'), 'nil')
        borders.append(el)
    tcPr.append(borders)


def png_size(path):
    with open(path, 'rb') as f:
        head = f.read(33)
    w, h = struct.unpack('>II', head[16:24])
    return w, h


def style_run(run, size=11, bold=False, color=BLACK, italic=False,
              latin_font=LAT_FONT):
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color
    run.font.name = latin_font
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), CN_FONT)
    rFonts.set(qn('w:ascii'), latin_font)
    rFonts.set(qn('w:hAnsi'), latin_font)


VOL2_X_WORDS = {'x', 'dx', 'xh', 'nx'}


def split_variable_x(text):
    """下册把数学变量 x 单独切成 run；max、convex 等英文词不拆。"""
    if not IS_VOL2 or 'x' not in text:
        return [(text, False)]
    out, cursor = [], 0
    for match in re.finditer(r'[A-Za-z]+', text):
        if match.start() > cursor:
            out.append((text[cursor:match.start()], False))
        word = match.group(0)
        if word in VOL2_X_WORDS:
            for part in re.split(r'(x)', word):
                if part:
                    out.append((part, part == 'x'))
        else:
            out.append((word, False))
        cursor = match.end()
    if cursor < len(text):
        out.append((text[cursor:], False))
    return out


def add_text_runs(par, text, size, bold, color, subscript=False, superscript=False):
    """写普通文字；下册的变量 x 用左右不对称的 Georgia 斜体。"""
    for part, is_variable_x in split_variable_x(text):
        if not part:
            continue
        run = par.add_run(part)
        style_run(run, size, bold, color, italic=is_variable_x,
                  latin_font=VARIABLE_FONT if is_variable_x else LAT_FONT)
        run.font.subscript = subscript
        run.font.superscript = superscript


def set_mathtext_font(plt):
    """分数和矩阵是图片；下册同样让 x 与对称的乘号 × 拉开字形。"""
    if IS_VOL2:
        plt.rcParams['mathtext.fontset'] = 'custom'
        plt.rcParams['mathtext.rm'] = VARIABLE_FONT
        plt.rcParams['mathtext.it'] = VARIABLE_FONT + ':italic'
        plt.rcParams['mathtext.bf'] = VARIABLE_FONT + ':bold'
    else:
        plt.rcParams['mathtext.fontset'] = 'dejavusans'


def frac_png(num, den, color):
    """把分数渲染成图片：分子在上、横线居中、分母在下。

    正文里没法用文字排出上下分列的分数（Unicode 只有 ½⅓ 那几个现成的），
    所以走图片 —— 和原稿公式一样的做法。
    分子分母都是 mathtext 片段，所以 2^n、3\\times 10^n、n+1 这类都能排。
    """
    os.makedirs(FRACDIR, exist_ok=True)
    hexcol = '%02X%02X%02X' % (color[0], color[1], color[2])
    safe = re.sub(r'[^0-9a-zA-Z]+', '_', '%s-%s' % (num, den)).strip('_')[:40]
    tag = hashlib.md5(('%s|%s' % (num, den)).encode()).hexdigest()[:6]
    path = os.path.join(FRACDIR, 'frac-%s-%s-%s.png' % (safe, tag, hexcol))
    if not os.path.exists(path):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        set_mathtext_font(plt)
        fig = plt.figure(figsize=(1.2, 1.2))
        fig.text(0.05, 0.05, r'$\frac{%s}{%s}$' % (num, den),
                 fontsize=46, color='#' + hexcol)
        try:
            fig.savefig(path, dpi=300, transparent=True,
                        bbox_inches='tight', pad_inches=0.012)
        except Exception as e:
            plt.close(fig)
            # 指名道姓：不然只会抛一段 mathtext 堆栈，看不出是哪个分数坏了
            raise SystemExit(
                '分数渲染失败： [[%s|%s]]\n  mathtext 说：%s\n'
                '  提示：分数内部是数学式，不能用正文的 ^n^ 上标写法（要写 ^{n}），'
                '也不要用全角 ＋ 或 U+2212 减号；根号写 \\sqrt{...}。'
                % (num, den, e))
        plt.close(fig)
    return path


def add_frac(par, num, den, size, color):
    path = frac_png(num, den, color)
    w, h = png_size(path)
    height_pt = size * FRAC_SCALE
    run = par.add_run()
    run.add_picture(path, height=Inches(height_pt / 72.0),
                    width=Inches(height_pt / 72.0 * w / float(h)))
    # 行内图片默认坐在基线上 —— 那样分母底边和正文底边齐平，整个分数会往上飘。
    # 把它压下去，让分数线落在数学轴（约基线上方 0.28 em）附近。
    drop_pt = height_pt / 2.0 - size * 0.28
    pos = OxmlElement('w:position')
    pos.set(qn('w:val'), str(int(round(-drop_pt * 2))))   # 单位是半磅
    run._element.get_or_add_rPr().append(pos)


def matrix_png(body, color):
    """[[m:1,0;0,1]] → 带方括号的矩阵图片。行用 ; 分隔，行内元素用 , 分隔。

    mathtext 没有矩阵环境，所以自己排：元素摆进格子，方括号用线画。
    缓存进 figs/frac/ —— 和分数同一个桶，verify 的 [3] 口径不用改。
    """
    os.makedirs(FRACDIR, exist_ok=True)
    hexcol = '%02X%02X%02X' % (color[0], color[1], color[2])
    rows = [[e.strip() for e in r.split(',')] for r in body.split(';')]
    nr, nc = len(rows), max(len(r) for r in rows)
    safe = re.sub(r'[^0-9a-zA-Z]+', '_', body).strip('_')[:40]
    tag = hashlib.md5(body.encode()).hexdigest()[:6]
    path = os.path.join(FRACDIR, 'mat-%s-%s-%s.png' % (safe, tag, hexcol))
    if not os.path.exists(path):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
        set_mathtext_font(plt)
        CW, CH, BR, PAD = 0.62, 0.55, 0.16, 0.10   # 列宽/行高/括号区/边距（英寸）
        W, H = 2 * BR + CW * nc + 0.10, 2 * PAD + CH * nr
        fig = plt.figure(figsize=(W, H))
        try:
            for i, row in enumerate(rows):
                for j, e in enumerate(row):
                    fig.text((BR + 0.05 + (j + 0.5) * CW) / W,
                             (H - PAD - (i + 0.5) * CH) / H,
                             '$%s$' % e, ha='center', va='center',
                             fontsize=30, color='#' + hexcol)
            for x0, tick in ((0.06 / W, 0.11 / W), ((W - 0.06) / W, -0.11 / W)):
                fig.add_artist(Line2D([x0, x0], [0.03, 0.97],
                                      lw=2.4, color='#' + hexcol))
                for yy in (0.03, 0.97):
                    fig.add_artist(Line2D([x0, x0 + tick], [yy, yy],
                                          lw=2.4, color='#' + hexcol))
            fig.savefig(path, dpi=300, transparent=True,
                        bbox_inches='tight', pad_inches=0.012)
        except Exception as e:
            plt.close(fig)
            raise SystemExit('矩阵渲染失败： [[m:%s]]\n  mathtext 说：%s' % (body, e))
        plt.close(fig)
    return path


def add_matrix(par, body, size, color):
    path = matrix_png(body, color)
    nr = len(body.split(';'))
    w, h = png_size(path)
    height_pt = size * FRAC_SCALE * nr / 2.0
    run = par.add_run()
    run.add_picture(path, height=Inches(height_pt / 72.0),
                    width=Inches(height_pt / 72.0 * w / float(h)))
    drop_pt = height_pt / 2.0 - size * 0.28
    pos = OxmlElement('w:position')
    pos.set(qn('w:val'), str(int(round(-drop_pt * 2))))
    run._element.get_or_add_rPr().append(pos)


TOKEN = re.compile(r'(\*\*.+?\*\*|~[^~]+~|\^[^^]+\^|\[\[[^\]]+\]\])')


def split_frac(body):
    """[[1/2]] 简写数字分数；[[1|2^n]] 通式，竖线分隔，两边都是 mathtext。"""
    if '|' in body:
        num, den = body.split('|', 1)
    else:
        num, den = body.split('/', 1)
    return num.strip(), den.strip()


def add_rich(par, text, size=11, color=BLACK, bold_all=False):
    """解析 **粗体** / ~下标~ / ^上标^ 并写入段落。

    粗体必须**递归**解析：否则 `**s~n~ ＝ 1/2^n^**` 会被整块吞成一个 run，
    里面的上下标标记原样留在纸面上。
    """
    text = text.replace('{{', '').replace('}}', '')   # 转义标记只对转换脚本有意义
    for piece in TOKEN.split(text):
        if not piece:
            continue
        if piece.startswith('**') and piece.endswith('**') and len(piece) > 4:
            add_rich(par, piece[2:-2], size, color, bold_all=True)
        elif piece.startswith('[[') and piece.endswith(']]'):
            body = piece[2:-2]
            if body.startswith('m:'):
                add_matrix(par, body[2:], size, color)
            else:
                num, den = split_frac(body)
                add_frac(par, num, den, size, color)
        elif piece.startswith('~') and piece.endswith('~'):
            add_text_runs(par, piece[1:-1], size, bold_all, color, subscript=True)
        elif piece.startswith('^') and piece.endswith('^'):
            add_text_runs(par, piece[1:-1], size, bold_all, color, superscript=True)
        else:
            add_text_runs(par, piece, size, bold_all, color)


# 行距（2026-08-03 用户两次说"略微减少一点、显得紧凑一些"，分两档下调。
# 第一档 1.5→1.4 他没看出来，第二档收到 1.3：
#   正文 1.5→1.4→1.3、盒子正文与列表 1.45→1.38→1.28、
#   盒子标题 1.3→1.25→1.18、表格 1.25→1.2→1.12、图注 1.2→1.15
# 改完务必拆开 docx 数一遍 w:line 核对（240×行距）——第一档就漏改过 bullet()）
#
# 段间距（同日第三步，用户"那就收段间距"）：正文段后 8→6、盒子标题段前 6→4、
# 盒子末段段后 6→4、盒子与表格后面那个空段 4→3。
# **还没动的杠杆**（下次要更紧就从这儿收）：节标题段前 16、小节标题段前 10、
# 图注段后 12、分隔线段后 14 —— 这四个是眼下最大的几块留白。
def para(doc, text='', size=11, color=BLACK, space_after=6, space_before=0,
         align=None, indent=0, line=1.3, bold_all=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing = line
    if indent:
        pf.left_indent = Cm(indent)
    if align:
        p.alignment = align
    if text:
        add_rich(p, text, size, color, bold_all)
    return p


# ---------------------------------------------------------------- blocks
def heading(doc, level, text):
    if level == 1:
        p = doc.add_paragraph()
        p.paragraph_format.page_break_before = True
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(0)
        add_rich(p, text, 19, NAVY, bold_all=True)
        rule = doc.add_paragraph()
        rule.paragraph_format.space_after = Pt(14)
        pPr = rule._p.get_or_add_pPr()
        bdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single'); bottom.set(qn('w:sz'), '8')
        bottom.set(qn('w:space'), '1'); bottom.set(qn('w:color'), '1F3A6E')
        bdr.append(bottom); pPr.append(bdr)
    elif level == 2:
        para(doc, text, 14.5, NAVY, space_after=6, space_before=16, bold_all=True)
    else:
        para(doc, text, 12, NAVY, space_after=4, space_before=10, bold_all=True)


def figure(doc, fname, caption):
    path = os.path.join(FIGDIR, fname)
    if not os.path.exists(path):
        raise SystemExit('missing figure: ' + fname)
    w, h = png_size(path)
    width_in = min(5.9, w / 200.0)
    if (h / 200.0) * (width_in / (w / 200.0)) > 3.7:
        width_in = 3.7 * (w / float(h))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(path, width=Inches(width_in))
    if caption:
        para(doc, caption, 9.5, GREY, space_after=12,
             align=WD_ALIGN_PARAGRAPH.CENTER, line=1.15)


def box(doc, kind, title, body_lines):
    fill, color = BOXES.get(kind, BOXES['remember'])
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_bg(cell, fill)
    set_cell_border(cell, ''.join('%02X' % c for c in (color[0], color[1], color[2]))
                    if isinstance(color, tuple) else '%02X%02X%02X' % (color[0], color[1], color[2]),
                    left_only=True)
    cell.paragraphs[0]._p.getparent().remove(cell.paragraphs[0]._p)
    if title:
        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.line_spacing = 1.18
        add_rich(p, title, 11, color, bold_all=True)
    for i, line in enumerate(body_lines):
        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(4 if i == len(body_lines) - 1 else 3)
        p.paragraph_format.line_spacing = 1.28
        add_rich(p, line, 10.5, BLACK)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)


def table(doc, rows):
    header, body = rows[0], rows[1:]
    tbl = doc.add_table(rows=len(rows), cols=len(header))
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, txt in enumerate(header):
        c = tbl.cell(0, j)
        set_cell_bg(c, 'DCE7F7')
        c.paragraphs[0].paragraph_format.space_after = Pt(2)
        c.paragraphs[0].paragraph_format.space_before = Pt(2)
        add_rich(c.paragraphs[0], txt, 10, NAVY, bold_all=True)
    for i, row in enumerate(body, start=1):
        for j, txt in enumerate(row):
            c = tbl.cell(i, j)
            c.paragraphs[0].paragraph_format.space_after = Pt(2)
            c.paragraphs[0].paragraph_format.space_before = Pt(2)
            c.paragraphs[0].paragraph_format.line_spacing = 1.12
            add_rich(c.paragraphs[0], txt, 10, BLACK)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)


def bullet(doc, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.28
    add_rich(p, text, 11, BLACK)


# ---------------------------------------------------------------- parser
def build():
    # 每次重建都清空分数图缓存：否则改过命名/配色以后，旧文件会留在盘上，
    # 让"媒体文件数 ＝ 插图 ＋ 分数图"这条校验失去意义。
    if os.path.isdir(FRACDIR):
        for f in os.listdir(FRACDIR):
            if f.endswith('.png'):
                os.remove(os.path.join(FRACDIR, f))

    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.2)
    sec.left_margin = sec.right_margin = Cm(2.4)

    files = sorted(glob.glob(os.path.join(CONTENT, '*.md')))
    if not files:
        raise SystemExit('no content files in ' + CONTENT)

    for path in files:
        with open(path, encoding='utf-8') as f:
            lines = f.read().split('\n')
        i = 0
        while i < len(lines):
            raw = lines[i]
            line = raw.rstrip()
            s = line.strip()
            if not s:
                i += 1; continue

            if s.startswith('### '):
                heading(doc, 3, s[4:])
            elif s.startswith('## '):
                heading(doc, 2, s[3:])
            elif s.startswith('# '):
                heading(doc, 1, s[2:])
            elif s.startswith('FIG:'):
                spec = s[4:].split('|')
                figure(doc, spec[0].strip(),
                       spec[1].strip() if len(spec) > 1 else '')
            elif s.startswith('BOX['):
                m = re.match(r'BOX\[(\w+)\]:\s*(.*?)\s*::\s*(.*)$', s)
                kind, title, body = m.group(1), m.group(2), m.group(3)
                box(doc, kind, title, [b.strip() for b in body.split('//')])
            elif s == 'TABLE:':
                rows = []
                i += 1
                while i < len(lines) and lines[i].strip().startswith('|'):
                    # 拆列前先把两种"不是分隔符的竖线"藏起来：
                    #   \|        —— 手写转义
                    #   [[a|b]]   —— 通式分数标记，里面的竖线是分子分母分隔符
                    row = lines[i].strip().replace(r'\|', '\x00')
                    row = re.sub(r'\[\[[^\]]+\]\]',
                                 lambda m: m.group(0).replace('|', '\x01'), row)
                    cells = [c.strip().replace('\x00', '|').replace('\x01', '|')
                             for c in row.strip('|').split('|')]
                    rows.append(cells)
                    i += 1
                table(doc, rows)
                continue
            elif s.startswith('- '):
                bullet(doc, s[2:])
            elif s == '---':
                para(doc, '· · ·', 12, GREY, align=WD_ALIGN_PARAGRAPH.CENTER,
                     space_before=6, space_after=6)
            elif s.startswith('CENTER:'):
                para(doc, s[7:].strip(), 12, NAVY,
                     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)
            elif s.startswith('TITLE:'):
                para(doc, s[6:].strip(), 26, NAVY,
                     align=WD_ALIGN_PARAGRAPH.CENTER, space_before=90,
                     space_after=10, bold_all=True)
            elif s.startswith('SUB:'):
                para(doc, s[4:].strip(), 13, GREY,
                     align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
            else:
                para(doc, s)
            i += 1

    doc.save(OUTPUT)
    print('wrote', OUTPUT)
    print('paragraphs:', len(doc.paragraphs), ' tables:', len(doc.tables))


if __name__ == '__main__':
    build()
