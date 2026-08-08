#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对生成的 docx 做可失败的结构检查。任何一项 FAIL 都说明编译出了问题。"""
import os
import re
import sys
import glob
import zipfile
from docx import Document

import sys
HERE = os.path.dirname(os.path.abspath(__file__))
# 第二个参数指定分册目录（默认当前册）；两册共用同一套管线
BOOK = os.path.join(HERE, sys.argv[1]) if len(sys.argv) > 1 else HERE
IS_VOL2 = os.path.basename(os.path.normpath(BOOK)) == 'vol2'
TITLE = (open(os.path.join(BOOK, 'TITLE'), encoding='utf-8').read().strip()
        if os.path.exists(os.path.join(BOOK, 'TITLE')) else '给小学生讲微积分（上）')
DOCX = os.path.join(BOOK, TITLE + '.docx')
CONTENT = os.path.join(BOOK, 'content')
FIGDIR = os.path.join(BOOK, 'figs')

fails, warns = [], []


def check(cond, msg):
    (print('  PASS  ' + msg) if cond else (fails.append(msg), print('  FAIL  ' + msg)))


doc = Document(DOCX)

# ---- 1. 残留标记：解析失败的确凿信号
LEFTOVER = re.compile(r'\*\*|(?<!\w)~|\^|^FIG:|^BOX\[|^TABLE:|^CENTER:|^TITLE:|^SUB:')
bad = []
def walk_paragraphs():
    for p in doc.paragraphs:
        yield p
    for t in doc.tables:
        for row in t.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    yield p

for p in walk_paragraphs():
    if LEFTOVER.search(p.text):
        bad.append(p.text[:70])
print('\n[1] 残留标记')
check(not bad, '正文中没有未解析的标记 (%d 处)' % len(bad))
for b in bad[:10]:
    print('        ->', b)

# ---- 2. 上下标真的生效了
def vert_count(attr):
    if not IS_VOL2:
        return sum(1 for p in walk_paragraphs() for r in p.runs if getattr(r.font, attr))
    # 下册的上标 n−1 会按字体拆成 Georgia 的 n 与正体的 −1；它们仍是同一个上标。
    # 因此按每段里连续的上下标组计数，而不是把字体切换误算成新的标记。
    total = 0
    for p in walk_paragraphs():
        active = False
        for r in p.runs:
            current = bool(getattr(r.font, attr))
            if current and not active:
                total += 1
            active = current
    return total


subs = vert_count('subscript')
sups = vert_count('superscript')
# 和源文件对账。注意 [[...]] 里的 ^ 是 mathtext（画进分数图里），不产生 docx 上标。
SKIP_SPAN = re.compile(r'\[\[[^\]]+\]\]|\{\{.*?\}\}')
src_sub = src_sup = 0
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    body = SKIP_SPAN.sub('', open(f, encoding='utf-8').read())
    src_sub += len(re.findall(r'~[^~\n]+~', body))
    src_sup += len(re.findall(r'\^[^^\n]+\^', body))
print('\n[2] 上下标')
unit = '组' if IS_VOL2 else 'run'
check(subs == src_sub, '下标%s %d ＝ 源文件 ~…~ 标记 %d' % (unit, subs, src_sub))
check(sups == src_sup, '上标%s %d ＝ 源文件 ^…^ 标记 %d（其余已并入分数图）'
      % (unit, sups, src_sup))

# ---- 3. 插图：源文件里引用的每一张都被嵌进去了
refs = []
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    for line in open(f, encoding='utf-8'):
        m = re.match(r'\s*FIG:\s*([^|]+)', line)
        if m:
            refs.append(m.group(1).strip())
with zipfile.ZipFile(DOCX) as z:
    embedded = [n for n in z.namelist() if n.startswith('word/media/')]
fracs = []
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    # [[1/2]] 数字简写，[[1|2^n]] 通式 —— 两种都要数
    fracs += re.findall(r'\[\[([^\]]+)\]\]', open(f, encoding='utf-8').read())

print('\n[3] 插图与行内分数')
# 同一张图被引用多次时，docx 只存一份媒体文件 —— 放置次数和唯一文件数要分开算
check(len(doc.inline_shapes) == len(refs) + len(fracs),
      '内嵌图片总数 %d ＝ 插图 %d ＋ 行内分数 %d'
      % (len(doc.inline_shapes), len(refs), len(fracs)))
# 分数图按 (分子, 分母, 颜色) 缓存：同一个分数在正文(黑)和居中行(藏青)是两个文件
frac_files = [f for f in os.listdir(os.path.join(FIGDIR, 'frac'))
              if f.endswith('.png')] if os.path.isdir(os.path.join(FIGDIR, 'frac')) else []
check(len(embedded) == len(set(refs)) + len(frac_files),
      '媒体文件 %d ＝ 去重插图 %d ＋ 分数图文件 %d（同一分数按颜色分别缓存）'
      % (len(embedded), len(set(refs)), len(frac_files)))
print('        分数出现 %d 次，%d 种：%s' %
      (len(fracs), len(set(fracs)), '、'.join(sorted(set(fracs)))))
missing = [r for r in refs if not os.path.exists(os.path.join(FIGDIR, r))]
check(not missing, '所有被引用的图都存在于 figs/ (%s)' % (missing or '无缺失'))
unused = sorted(f for f in set(os.listdir(FIGDIR)) - set(refs) if f.endswith('.png'))
if unused:
    warns.append('未被引用的图: %s' % ', '.join(unused))

# ---- 3.5 平面外字符：Google Docs 转换时会变乱码
nonbmp = []
for p in walk_paragraphs():
    for ch in p.text:
        if ord(ch) > 0xFFFF:
            nonbmp.append((ch, hex(ord(ch)), p.text[:40]))
print('\n[3.5] 字符安全')
check(not nonbmp, '没有 BMP 平面外字符（会在 Docs 转换时变乱码）(%d 处)' % len(nonbmp))
for ch, cp, ctx in nonbmp[:5]:
    print('        ->', repr(ch), cp, ctx)

# ---- 3.8 名词表的"在哪"必须兑现：附录说某个词出自某一篇，那一篇就得真的讲过它
# 篇名→正文，从文件里现扫。**不能写死文件名**：写死以后换一册就全都匹配不上，
# 这条检查会静悄悄地空转，"零悬空"变成假通过。
bodies = {}
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    body = open(f, encoding='utf-8').read()
    m = re.search(r'(?m)^# (第[一二三四五六七八九十]+篇)', body)
    if m:
        bodies[m.group(1)] = body
dangling = []
appendix = next((f for f in sorted(glob.glob(os.path.join(CONTENT, '*.md')))
                 if '# 附录 B' in open(f, encoding='utf-8').read()), None)
if appendix:
    in_glossary = False
    for line in open(appendix, encoding='utf-8'):
        if line.startswith('# 附录 B'):
            in_glossary = True
        elif line.startswith('# 附录 C'):
            in_glossary = False
        elif in_glossary and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) < 3 or cells[0] in ('词',):
                continue
            term, where = cells[0], cells[-1]
            if where not in bodies:
                continue
            # 词条可能写成「上界 / 下界」或「完备（没有洞）」——拆开、并剥掉括号注释
            bare = re.sub(r'[（(][^）)]*[）)]', '', term)
            variants = [t.strip() for t in re.split(r'[/、]', bare) if t.strip()]
            if not any(v in bodies[where] for v in variants):
                dangling.append('%s —— 名词表说在%s，但那一篇正文里没出现' % (term, where))
print('\n[3.8] 名词表交叉引用')
check(not dangling, '名词表里每个词都在它标注的那一篇出现过 (%d 处悬空)' % len(dangling))
for d in dangling:
    print('        ->', d)

# ---- 3.9 "第X篇第Y节"必须真的存在（拆分/改序以后最容易失效的就是这个）
CN = '一二三四五六七八九十'
chapters = {}            # 篇名 -> 该篇的小节序号集合
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    body = open(f, encoding='utf-8').read()
    m = re.search(r'(?m)^# (第[一二三四五六七八九十]+篇)', body)
    if m:
        chapters[m.group(1)] = set(re.findall(r'(?m)^## ([一二三四五六七八九十零]+)、', body))
bad_refs = []
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    text = open(f, encoding='utf-8').read()
    for m in re.finditer(r'(第[一二三四五六七八九十]+篇)第([一二三四五六七八九十]+)节', text):
        # 跨册引用（"第一册第二篇第六节"）说的是另一册的小节，本册无从校验 —— 必须豁免。
        # 由来（2026-08-01 第二册拆篇）：这条以前一直"通过"，纯属巧合——当时本册第二篇
        # 恰好也有第六节。拆篇后本册第二篇只剩三节，它立刻误报。[3.92]/[3.93] 早就做了
        # 跨册豁免，只有这里漏了。**先判断哪一边过期**：稿子没错，是检查漏了一种情形。
        if re.search(r'[一二两上下本]册.{0,4}$', text[:m.start()]):
            continue
        ch, sec = m.group(1), m.group(2)
        if ch not in chapters:
            bad_refs.append('%s: 引用了不存在的 %s' % (os.path.basename(f), ch))
        elif sec not in chapters[ch]:
            bad_refs.append('%s: %s第%s节 不存在（该篇只有 %s）'
                            % (os.path.basename(f), ch, sec,
                               '、'.join(sorted(chapters[ch], key=lambda c: CN.index(c)))))
print('\n[3.9] 章节交叉引用')
check(not bad_refs, '所有"第X篇第Y节"都指向真实存在的小节 (%d 处失效)' % len(bad_refs))
for b in sorted(set(bad_refs)):
    print('        ->', b)

# ---- 3.91 不带篇名的"第X节"，指的是本篇的小节，必须真的存在
#   由来（2026-07-31 全册审查）：第五篇小练习(6)写"（第四节反例一就是）"，
#   可第五篇第四节没有"反例一"，全册都没有。[3.9] 的正则要求带篇名，裸引用整个漏过去了。
#   注意这条只能验"存在"，验不了"指对了没有"——同一批里还有一处
#   第五篇裸写"第二节 √2"、实指第三篇第二节，那种得靠人读。
bare = []
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    body = open(f, encoding='utf-8').read()
    m = re.search(r'(?m)^# (第[一二三四五六七八九十]+篇)', body)
    if not m:
        continue                      # 前言/附录没有"本篇"，裸引用无从校验
    own = m.group(1)
    secs = set(re.findall(r'(?m)^## ([一二三四五六七八九十零]+)、', body))
    for ln, line in enumerate(body.split('\n'), 1):
        for mm in re.finditer(r'(?<!篇)第([一二三四五六七八九十]+)节', line):
            if mm.group(1) not in secs:
                bare.append('%s:%d  裸引用"第%s节"，但%s没有这一节（只有 %s）'
                            % (os.path.basename(f), ln, mm.group(1), own,
                               '、'.join(sorted(secs, key=lambda c: CN.index(c)))))
print('\n[3.91] 裸"第X节"引用')
check(not bare, '不带篇名的"第X节"都指向本篇真实存在的小节 (%d 处失效)' % len(bare))
for b in bare[:8]:
    print('        ->', b)

# ---- 3.92 一篇不许引用自己："第四篇还会用"出现在第四篇里，就是改序时漏改的残留
#   表格行（以 | 开头）例外：那是按篇索引的总表，指向自己是正常的。
selfref = []
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    body = open(f, encoding='utf-8').read()
    m = re.search(r'(?m)^# (第[一二三四五六七八九十]+篇)', body)
    if not m:
        continue
    own = m.group(1)
    for ln, line in enumerate(body.split('\n'), 1):
        if ln == 1 or line.lstrip().startswith('|'):
            continue
        for mm in re.finditer(own, line):
            # "第一册第五篇" 是跨册引用，不是自指 —— 第二册的第五篇这样写完全正常
            if re.search(r'[一二两上下本]册$', line[:mm.start()]):
                continue
            selfref.append('%s:%d  %s 引用了自己：…%s…'
                           % (os.path.basename(f), ln, own,
                              line[max(0, mm.start() - 20):mm.end() + 26].strip()))
# ---- 3.93 具名的"例X／反例X"必须真的被定义过（定义 = 出现在某个小节标题里）
#   由来（2026-07-31 全册审查）：第五篇小练习(6)引用"第四节反例一"，全册根本没有"反例一"
#   这种东西。[3.91] 抓不到它（第五篇确实有第四节），只有按名字对账才抓得到。
#   跨册引用（"第一册第四篇例一"）不算本册未定义。
named, defined = [], set()
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    body = open(f, encoding='utf-8').read()
    for h in re.findall(r'(?m)^#{1,3} .*', body):
        for mm in re.finditer(r'(?:反例|例)[一二三四五六七八九十]', h):
            defined.add(mm.group(0))
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        # 同一行里只要有一次带"第X册"的引用，这一行后面再裸提同一个名字就是它的延续
        crossvol = {mm.group(1) for mm in
                    re.finditer(r'[一二两上下本]册.{0,8}?((?:反例|例)[一二三四五六七八九十])', line)}
        for mm in re.finditer(r'(?:反例|例)[一二三四五六七八九十]', line):
            if mm.group(0) in crossvol:
                continue             # 跨册引用，定义在另一册
            if mm.group(0) not in defined:
                named.append('%s:%d  引用了"%s"，可全册没有哪个小节标题定义过它'
                             % (os.path.basename(f), ln, mm.group(0)))
print('\n[3.93] 具名例子必须存在')
check(not named, '每个被引用的"例X／反例X"都在小节标题里定义过 (%d 处悬空)' % len(named))
for b in named[:8]:
    print('        ->', b)

# ---- 3.94 自变量必须是 a：x 只有在符号总表里登记过，才允许在正文露面
#   由来（2026-07-31 第二册审查）：第三篇有 7 处 2xh/3xh/4xh，是 x→a 全局替换的残留；
#   "2xh" 里 x 根本没有定义。第一册的 x 是合法的（第五篇构造出来的那个数），
#   区别就在于第一册的附录 A 给 x 立了词条，第二册没有 —— 按这个判据分册自适应，
#   不写死文件名；这里只查自变量是否在本册符号表登记过。
x_declared = False
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    for line in open(f, encoding='utf-8'):
        if line.strip().startswith('|') and 'x' in line.strip('|').split('|')[0]:
            x_declared = True
strayx = []
if not x_declared:
    for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
        for ln, line in enumerate(open(f, encoding='utf-8'), 1):
            if 'BOX[grown]' in line:
                continue
            # 插图文件名是**代码标识符**，不是正文：fig-14-halving-max.png 里的 x
            # 被当成"a 写成了 x"报了一次假警（2026-08-01）。同一条教训在图文件
            # 那边也栽过——全局替换必须分开处理"内容"和"标识符"，检查同理。
            probe = re.sub(r'(?m)^\s*FIG:\s*\S+', 'FIG:', line)
            if 'x' in probe:
                strayx.append('%s:%d  出现了 x，可符号总表里没有 x —— 是不是 a 写成了 x？…%s…'
                              % (os.path.basename(f), ln,
                                 probe[max(0, probe.find('x') - 18):probe.find('x') + 18].strip()))
print('\n[3.94] 自变量残留')
check(not strayx, 'x 要么在符号总表里登记过，要么只出现在"长大以后"盒子里 (%d 处)'
      % len(strayx))
for b in strayx[:8]:
    print('        ->', b)

print('\n[3.92] 自指的篇引用')
check(not selfref, '没有"某篇引用它自己"的残留 (%d 处)' % len(selfref))
for b in selfref[:8]:
    print('        ->', b)

# ---- 3.945 第二册自变量已于 08-07 全册改回 x（用户定：大家习惯 dx；数字挨 x 省乘号）
#   反向抓残留的独立 a（"2ah"这类字母连写的 a 由第二遍替换处理过，这里连它一起抓）。
#   FIG 文件名是标识符不是正文，照 [3.94] 的老规矩剥掉再查。只对 vol2 生效。
if BOOK.rstrip(os.sep).endswith('vol2'):
    straya = []
    for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
        for ln, line in enumerate(open(f, encoding='utf-8'), 1):
            probe = re.sub(r'(?m)^\s*FIG:\s*\S+', 'FIG:', line)
            for m in re.finditer(r'(?<![A-Za-z])a(?![A-Za-z])|(?<![A-Za-z])a(?=h)', probe):
                straya.append('%s:%d  …%s…' % (os.path.basename(f), ln,
                              probe[max(0, m.start() - 10):m.end() + 10].strip()))
    print('\n[3.945] 第二册自变量残留 a')
    check(not straya, '正文没有残留的自变量 a (%d 处)' % len(straya))
    for xx in straya[:8]:
        print('        ->', xx)

# ---- 3.95 公式里不许夹中文：符号和汉字不能用 ＝ ／ ≤ 直接连起来
#   反面教材（用户 2026-07-31 指出）："不到 ε 的一半 ＋ ε 的一半 ＝ ε"、"低估 ≤ 真面积"。
#   汉字要么先命名成符号，要么把整句写成句子（不带关系符）。
CJK = r'[\u4e00-\u9fff]'
MIXED = re.compile(CJK + r'\s*[＝＜＞≤≥]|[＝＜＞≤≥]\s*' + CJK)
QUOTE = re.compile("[" + "".join(map(chr, [34, 39, 0x201c, 0x201d, 0x300c, 0x300d, 0x2018, 0x2019])) + "]")
mixed = []
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        for m in MIXED.finditer(line):
            ctx = line[max(0, m.start() - 8):m.end() + 8]
            if QUOTE.search(ctx):        # 在谈论符号本身（"＜"会退化成"≤"），不算
                continue
            mixed.append('%s:%d  …%s…' % (os.path.basename(f), ln, ctx.strip()))
print('\n[3.95] 公式里不夹中文')
check(not mixed, '没有"汉字 ＝ 符号"式的混写 (%d 处)' % len(mixed))
for x in mixed[:8]:
    print('        ->', x)

# ---- 3.96 搬家哨兵：引用旁的公式串，必须在被引的那一篇里真的出现
#   由来（2026-08-01）：把绿盒「不先确认存在，会出人命的」从第二篇搬到第五篇第五节，
#   第四篇蓝盒里"那就是**第二篇** 1 ＋ 2 ＋ 4 ＋ 8 那个笑话"当场成了悬空指向——
#   而 [3.9] 一声不吭：第二篇确实存在，只是那个笑话已经不在里面了。这一类是搬家的必然
#   副作用，靠人 grep 依赖捞出来的，捞漏一次就烂在书里。
#   **为什么只查公式串**：正文换说法是常事（"最高点存在"写成"最高点真的存在"），
#   拿正文比对会淹在误报里（试过：25 处嫌疑只有 1 处真错）。公式串不会被换说法，
#   所以这条几乎不误报。能换说法的那一大类，交给 audit_refs.py 人工过目。
FORMULA = re.compile(r'\d[\d\s]*(?:[＋－×÷]\s*\d[\d\s]*){2,}')
bodies = {}
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    b = open(f, encoding='utf-8').read()
    m = re.search(r'(?m)^# (第[一二三四五六七八九十]+篇)', b)
    if m:
        bodies[m.group(1)] = re.sub(r'\s+', '', b)
stale = []
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    own = None
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        m = re.match(r'^# (第[一二三四五六七八九十]+篇)', line)
        if m:
            own = m.group(1)
        for fm in FORMULA.finditer(line):
            expr = re.sub(r'\s+', '', fm.group(0))
            for cm in re.finditer(r'(第[一二三四五六七八九十]+篇)', line):
                ch = cm.group(1)
                # 跨册引用查不了；指向本篇的不算引用（公式就在眼前）
                if ch == own or re.search(r'[一二三两上下本]册\s*$', line[:cm.start()]):
                    continue
                if ch in bodies and expr not in bodies[ch]:
                    stale.append('%s:%d  说"%s"在%s里，可%s里没有这个式子'
                                 % (os.path.basename(f), ln, fm.group(0).strip(), ch, ch))
print('\n[3.96] 搬家哨兵：引用旁的公式串')
check(not stale, '每个"第X篇 <公式>"的公式都在那一篇里出现过 (%d 处悬空)' % len(stale))
for x in sorted(set(stale))[:8]:
    print('        ->', x)

# ---- 3.97 极限要用极限的语言说，不许"它很小所以不管它"
#   用户 2026-07-31："'一趋于 0 就没了'应该改成极限的语言，比如'考虑等式左右两边的极限'"。
HANDWAVE = ['就没了', '可以不管', '忽略不计', '不必理会', '小到可以扔']
waves = []
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        for w in HANDWAVE:
            if w in line:
                waves.append('%s:%d  %s（"%s"）'
                             % (os.path.basename(f), ln, line.strip()[:46], w))
print('\n[3.97] 极限的说法')
check(not waves, '没有"它很小所以不管"式的挥手 (%d 处)' % len(waves))
for x in waves[:6]:
    print('        ->', x)

# ---- 3.98 分数内部不许出现正文的 ~下标~（mathtext 不认，会渲染成一个空格）
badfrac = []
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        for m in re.finditer(r'\[\[[^\]]+\]\]', line):
            if '~' in m.group(0):
                badfrac.append('%s:%d  %s（分数里要写 _{n}，不是 ~n~）'
                               % (os.path.basename(f), ln, m.group(0)))
print('\n[3.98] 分数内部的写法')
check(not badfrac, '分数里没有正文用的 ~下标~ (%d 处)' % len(badfrac))
for x in badfrac[:5]:
    print('        ->', x)

# ---- 3.985 正文里不许有裸的斜杠分数（体例：分数一律上下排 [[分子|分母]]）
#   由来（2026-08-06，用户挑错）：第二篇 B4 写成"1／1、2／1、2、3／1、2、3、4／……"，
#   那里的 ／ 本意是**分组分隔符**，可孩子只会读成分数。四道闸一道都查不到它：
#   [3.95] 只管 ＝＜＞≤≥ 那几个关系符；slash_fractions.py 是**白名单**逐条替换
#   （1/2^n^、p/q……），没列进去的一律不碰，全角 ／ 更是从来不在名单里。
#   **只查"两侧都是数字"**是有意收窄的：全树扫过，附录的 `A1–A4 / B1–B4`（分组）、
#   字母斜杠和 `vol4/figs.py`（路径）都不该由这条数字分数闸误报；
#   而它们两侧都不是数字。这样零误报——宁可窄，也不装一条会喊狼来了的闸。
SLASHNUM = re.compile(r'[0-9]\s*[／/]\s*[0-9]')
SLASHSKIP = re.compile(r'(\[\[[^\]]*\]\]|\{\{.*?\}\}|//)')   # 已转换的分数、保护区、盒内换行
badslash = []
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        if line.lstrip().startswith('BOX[grown]'):     # 「长大以后」允许课本写法
            continue
        bare = SLASHSKIP.sub(' ', line)
        for m in SLASHNUM.finditer(bare):
            badslash.append('%s:%d  …%s…（分数要写成 [[分子|分母]]；只是分隔符就别用斜杠）'
                            % (os.path.basename(f), ln,
                               bare[max(0, m.start() - 12):m.end() + 12].strip()))
print('\n[3.985] 裸的斜杠分数')
check(not badslash, '正文里没有"数字 / 数字"式的裸斜杠 (%d 处)' % len(badslash))
for x in badslash[:5]:
    print('        ->', x)

# ---- 3.9855 第二册不用除号：凡是除法都排成真正的上下分数
#   2026-08-08 用户在第 48 页挑出：外层已经有分数线，分子里却又写“2 ÷ x_n”，
#   视觉上成了“分数线上还有除号”。这不只是嵌套分数的问题；同一册若一会儿写 ÷、
#   一会儿写上下分数，孩子会把同一个关系读成两套动作。因此第二册所有可见的 ÷ 一律禁用。
divsignbad = []
if BOOK.rstrip(os.sep).endswith('vol2'):
    for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
        for ln, line in enumerate(open(f, encoding='utf-8'), 1):
            if '÷' in line:
                divsignbad.append('%s:%d  %s' %
                                  (os.path.basename(f), ln, line.strip()[:72]))
    print('\n[3.9855] 第二册不用除号')
    check(not divsignbad, '所有除法都用上下分数线，不写 ÷ (%d 处)' % len(divsignbad))
    for x in divsignbad[:8]:
        print('        ->', x)

# ---- 3.986 第二册不许再用“导函数”这个名称
#   2026-08-07 最终口径：求导是 f → f′ 的操作；f′(x) 是某一点的导数（一个数）；
#   微分 dx → dy＝f′(x)dx 才是局部线性替身。f′ 仍然是函数，但不另称“导函数”。
termbad = []
if BOOK.rstrip(os.sep).endswith('vol2'):
    for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
        base = os.path.basename(f)
        for ln, line in enumerate(open(f, encoding='utf-8'), 1):
            if '导函数' in line:
                termbad.append('%s:%d  “导函数”（应分成求导操作、点值导数和微分）' % (base, ln))
    print('\n[3.986] 第二册术语口径（导数/求导/微分）')
    check(not termbad, '没有使用“导函数”这个名称 (%d 处)' % len(termbad))
    for x in termbad[:8]:
        print('        ->', x)

# ---- 3.987 第二册以 dy＝f′(p)dx 为主，分数式只在指定位置出现
#   2026-08-07 用户放松旧禁令：第五篇可用 dy/dx 解释两把 1-形式尺的倍率；
#   2026-08-08 第十篇先把 d²y/dx² 当作 f″(x) 的常见写法；
#   第十一篇借双入口直尺解释 d²f/(dx)²，并以加速度作一次回声；附录 A 收录。
#   裸斜杠仍禁，其他篇也不得让莱布尼兹式悄悄蔓延。
DIFFQUOT_BOX = re.compile(r'\[\[\s*d[^\]|]*\|\s*\(?d[^\]]*\]\]')
DIFFQUOT_BARE = re.compile(r'\bd[^\s/|]{0,12}\s*/\s*d[^\s/|]{1,12}')
diffquotbad = []
diffquot_seen = {}
diffquot_allowed = {
    '05-differential.md': {'[[dy|dx]]'},
    '10-shape.md': {'[[d^{2}y|dx^{2}]]'},
    '11-area.md': {'[[d^{2}f|(dx)^{2}]]', '[[d^{2}s|(dt)^{2}]]'},
    '14-appendix.md': {'[[dy|dx]]', '[[d^{2}y|dx^{2}]]'},
}
if BOOK.rstrip(os.sep).endswith('vol2'):
    for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
        base = os.path.basename(f)
        for ln, line in enumerate(open(f, encoding='utf-8'), 1):
            for m in DIFFQUOT_BOX.finditer(line):
                token = re.sub(r'\s+', '', m.group(0))
                diffquot_seen.setdefault(base, set()).add(token)
                if token not in diffquot_allowed.get(base, set()):
                    diffquotbad.append('%s:%d  %s（不在受控白名单）'
                                        % (base, ln, m.group(0)))
            for m in DIFFQUOT_BARE.finditer(line):
                diffquotbad.append('%s:%d  %s（必须用上下排记号，且只在指定篇解释）'
                                    % (base, ln, m.group(0)))
    for base, required in diffquot_allowed.items():
        missing = required - diffquot_seen.get(base, set())
        for token in sorted(missing):
            diffquotbad.append('%s  缺少应有的受控记号 %s' % (base, token))
    print('\n[3.987] 第二册微分记号')
    check(not diffquotbad, '分数式只在第五、十、十一篇和附录出现指定记号 (%d 处越界/缺失)' % len(diffquotbad))
    for x in diffquotbad[:8]:
        print('        ->', x)

# ---- 3.99 接招的必须是姐姐，不能是"我们"
#   由来（用户 2026-07-31）："妹妹发问、提出 ε，姐姐接招、给出 N 或 δ，这个在后来没有
#   得到完整执行，好些地方变成了妹妹发问、我们回答。"查下来 50 处，连第一篇那个
#   奠基的对话框都写着"妹妹出招，我们接招"，和前言承诺的"姐姐接招"直接打架。
#   两条判据（都只认**接招动作**，不碰作者叙述的"我们"）：
#     (a) 对话框里只要妹妹开口，应答方就不许是"我们"——纯结构，不会误报；
#     (b) 一行里同时谈着 ε/δ/关口/N，而"我们"后面紧跟回答/找/给/取/挑/掰这类接招动词。
#   注意：这条检查只管 ∃ 位。"我们来看一队数""我们不能完成无穷次计算""我们规定"
#   这类作者带读者的说法是合法的，故意不抓。
role_bad = []
for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        if line.lstrip().startswith('BOX[dialog]') and '**妹妹：**' in line \
                and '**我们：**' in line:
            role_bad.append('%s:%d  对话框里妹妹出招，接招的却是"我们"（应为姐姐）'
                            % (os.path.basename(f), ln))
        if not re.search(r'ε|δ|关口|N~|\bN\b', line):
            continue
        for m in re.finditer(r'我们', line):
            after = line[m.end():m.end() + 12]
            v = re.search(r'回答|找|给|取|挑|掰', after)
            if v and not re.search(r'[。；]|//', after[:v.start()]):
                role_bad.append('%s:%d  "我们%s…"——接招的动作应该归姐姐'
                                % (os.path.basename(f), ln, after[:v.end()]))
print('\n[3.99] 接招的是姐姐不是"我们"')
check(not role_bad, '妹妹出招以后，接招的都是姐姐 (%d 处写成了"我们")' % len(role_bad))
for b in role_bad[:8]:
    print('        ->', b)

# ---- 4. 盒子与表格
print('\n[4] 盒子与表格')
box_ct = sum(1 for f in sorted(glob.glob(os.path.join(CONTENT, '*.md')))
             for line in open(f, encoding='utf-8') if line.strip().startswith('BOX['))
tbl_ct = sum(1 for f in sorted(glob.glob(os.path.join(CONTENT, '*.md')))
             for line in open(f, encoding='utf-8') if line.strip() == 'TABLE:')
check(len(doc.tables) == box_ct + tbl_ct,
      '盒子 %d + 表格 %d = %d，docx 中表格数 %d' %
      (box_ct, tbl_ct, box_ct + tbl_ct, len(doc.tables)))

# ---- 5. 每篇都有标题
print('\n[5] 篇章')
h1 = [p.text for p in doc.paragraphs if p.paragraph_format.page_break_before]
check(len(h1) >= 3, '一级标题（另起一页）%d 个' % len(h1))
for t in h1:
    print('        ·', t)

# ---- 6. 字数
words = sum(len(p.text) for p in walk_paragraphs())
print('\n[6] 篇幅')
print('        正文字符数 ≈ %d' % words)

print('\n' + '=' * 46)
for w in warns:
    print('  WARN  ' + w)
if fails:
    print('  %d 项 FAIL' % len(fails))
    sys.exit(1)
print('  全部通过')
