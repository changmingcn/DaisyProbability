#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交叉引用**语义**对账：查"指到了一个存在、但东西已经不在那儿的地方"。

verify_docx.py 的 [3.8]/[3.9]/[3.91]/[3.92]/[3.93] 只能查"目标存不存在"。
真正咬人的那一类它查不出来——2026-08-01 把「不先确认存在，会出人命的」从第二篇搬到
第五篇，第四篇蓝盒里"那就是**第二篇** 1＋2＋4＋8 那个笑话"立刻成了悬空指向，而
[3.9] 一声不吭：第二篇确实存在，只是那个笑话已经不在里面了。

办法：把引用句里**带引号或加粗的那句话**当成"承诺"，拿去它所指的小节里找。
  在那一节里找到       → ok
  只在那一篇别的节找到 → 节号可疑
  只在本册别处找到     → 篇号可疑
  哪儿都找不到         → 高度可疑（多半是搬过家或改过写法）

三档都可能是误报（换了说法、拆了词），所以本脚本**只报嫌疑、不判死刑**，
输出是给人过目的。真确认是错的，就回 verify_docx.py 加一条能自动失败的检查。

  python3 audit_refs.py            # 三册全查
  python3 audit_refs.py --vol vol2 # 只查一册
  python3 audit_refs.py --all      # 连 ok 的也打印
"""
import os
import re
import sys
import glob
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
CN = '一二三四五六七八九十'
VOLS = [('vol1', ''), ('vol2', 'vol2'), ('vol3', 'vol3'), ('vol4', 'vol4')]
VOLNAME = {'vol1': '第一册', 'vol2': '第二册', 'vol3': '第三册', 'vol4': '第四册'}
NAME2VOL = {'第一册': 'vol1', '第二册': 'vol2', '第三册': 'vol3', '第四册': 'vol4'}


def norm(s):
    """抹掉标记与所有空白，统一引号——比对的是"说了什么"，不是"怎么排的"。"""
    s = re.sub(r'\[\[m:[^\]]*\]\]', '', s)
    s = re.sub(r'\[\[([^\]]+)\]\]', lambda m: m.group(1).replace('|', '/'), s)
    s = s.replace('**', '').replace('//', '').replace('~', '').replace('^', '')
    s = re.sub(r'[「」『』“”"\'‘’]', '"', s)
    s = re.sub(r'[，。、；：！？,.;:!?（）()《》—…·"]', '', s)
    s = re.sub(r'\s+', '', s)
    return s


def load(vol, sub):
    """一册 → {篇名: {'title':…, 'file':…, 'secs': {节序号: 正文}, 'body': 全文}}"""
    content = os.path.join(HERE, sub, 'content') if sub else os.path.join(HERE, 'content')
    book, loose = {}, []
    for f in sorted(glob.glob(os.path.join(content, '*.md'))):
        body = open(f, encoding='utf-8').read()
        m = re.search(r'(?m)^# (第[一二三四五六七八九十]+篇)(.*)$', body)
        if not m:
            loose.append((os.path.basename(f), body))
            continue
        secs, cur, buf = {}, None, []
        for line in body.split('\n'):
            h = re.match(r'^## ([一二三四五六七八九十零]+)、(.*)$', line)
            if h:
                if cur:
                    secs[cur] = '\n'.join(buf)
                cur, buf = h.group(1), [line]
            else:
                buf.append(line)
        if cur:
            secs[cur] = '\n'.join(buf)
        book[m.group(1)] = {'title': m.group(2).strip(), 'file': os.path.basename(f),
                            'secs': secs, 'body': body}
    return book, loose


BOOKS = {}
LOOSE = {}
for v, sub in VOLS:
    BOOKS[v], LOOSE[v] = load(v, sub)
ALLTEXT = {v: norm('\n'.join(d['body'] for d in BOOKS[v].values())
                   + '\n'.join(b for _, b in LOOSE[v])) for v in BOOKS}

# 引用：可带册前缀、可带节号
REF = re.compile(r'(?:(第[一二三]册)\s*)?(第[一二三四五六七八九十]+篇)'
                 r'(?:第([一二三四五六七八九十]+)节)?')
BARE = re.compile(r'(?<![篇册])第([一二三四五六七八九十]+)节')

# 从引用句里挑"可对账的承诺"：**只认引号里的话**。
# 加粗试过，全是噪音——加粗是本句自己的强调，不是对目标那一节的转述。
TOKEN = re.compile(r'“([^”]{4,40})”|「([^」]{4,40})」|"([^"]{4,40})"')
# 这些词太通用，拿去比对必然命中，报出来只是噪音
STOP = {'必须记住', '留给姐姐', '长大以后', '这一篇', '这一册', '我们', '妹妹', '姐姐'}


def sentence_at(line, pos):
    """取引用所在的那一小句（按中文句读和盒子换行切）。"""
    left = max((line.rfind(c, 0, pos) for c in '。；！？//'), default=-1)
    right = min([p for p in (line.find(c, pos) for c in '。；！？//') if p != -1]
                or [len(line)])
    return line[left + 1:right]


def locate(tok, vol, chap, sec, srcvol, srcchap, srcline):
    """这句承诺，在目标那儿吗？返回 (档次, 说明)。

    两个坑，都踩过才知道：
    ① **自我命中**——引用句里作者自己加粗的话，当然出现在"本篇"里。第一版没排除
       引用方所在的那一篇，572 句里几乎全被判成"篇号可疑"，全是这一个原因。
    ② **引用串当承诺**——「第五篇第五节」这种被引号括起来的引用本身不是承诺，要滤掉。
    """
    t = norm(tok)
    if len(t) < 4:
        return 'skip', ''
    src = norm(srcline)
    cut = lambda x: norm(x).replace(src, '')   # 把引用句本身挖掉，否则永远自我命中
    book = BOOKS[vol]
    if chap in book:
        d = book[chap]
        if sec and sec in d['secs']:
            if t in cut(d['secs'][sec]):
                return 'ok', ''
            if t in cut(d['body']):
                hit = [s for s, b in d['secs'].items() if t in cut(b)]
                return 'sec', '这句其实在%s第%s节' % (chap, '、第'.join(hit) or '?')
        elif t in cut(d['body']):
            return 'ok', ''
    # 找它到底在哪儿：跳过引用方自己那一篇，否则命中的是引用句本身
    for c, d in book.items():
        if c == chap or (vol == srcvol and c == srcchap):
            continue
        if t in cut(d['body']):
            return 'chap', '这句其实在%s%s（%s）' % (VOLNAME[vol], c, d['title'][:14])
    for v2 in BOOKS:
        if v2 != vol and t in ALLTEXT[v2].replace(src, ''):
            return 'vol', '这句其实在%s' % VOLNAME[v2]
    if t in ALLTEXT[vol].replace(src, ''):
        return 'ok', ''            # 在附录/前言等无篇号的地方
    return 'gone', '全套书里找不到这句话'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vol', help='只查一册：vol1/vol2/vol3/vol4')
    ap.add_argument('--all', action='store_true', help='连 ok 的也打印')
    a = ap.parse_args()

    rank = {'gone': 0, 'chap': 1, 'vol': 1, 'sec': 2}
    found, nref, ntok = [], 0, 0
    for vol, sub in VOLS:
        if a.vol and vol != a.vol:
            continue
        content = os.path.join(HERE, sub, 'content') if sub else os.path.join(HERE, 'content')
        for f in sorted(glob.glob(os.path.join(content, '*.md'))):
            body = open(f, encoding='utf-8').read()
            own = re.search(r'(?m)^# (第[一二三四五六七八九十]+篇)', body)
            own = own.group(1) if own else None
            for ln, line in enumerate(body.split('\n'), 1):
                refs = [(m.start(), m.group(1), m.group(2), m.group(3))
                        for m in REF.finditer(line)]
                refs += [(m.start(), None, own, m.group(1))
                         for m in BARE.finditer(line) if own]
                sticky = None          # 册前缀在一行内黏住：后文省略册名时沿用它
                for pos, volpfx, chap, sec in sorted(refs):
                    if not chap:
                        continue
                    nref += 1
                    if volpfx:
                        sticky = volpfx
                    tvol = NAME2VOL.get(volpfx or sticky, vol)
                    s = sentence_at(line, pos)
                    for m in TOKEN.finditer(s):
                        tok = next(g for g in m.groups() if g)
                        if tok in STOP or not re.search(r'[一-鿿0-9]', tok):
                            continue
                        # 引用串本身不是承诺：「第五篇第五节」「第一册第二篇」都要滤掉
                        if re.fullmatch(r'[^一-鿿]*(第[一二三]册)?(第[一二三四五六七八九十]+篇)?'
                                        r'(第[一二三四五六七八九十]+节)?[^一-鿿]*', tok):
                            continue
                        ntok += 1
                        lvl, why = locate(tok, tvol, chap, sec, vol, own, line)
                        if lvl == 'skip':
                            continue
                        if lvl != 'ok' or a.all:
                            found.append((rank.get(lvl, 3), lvl, VOLNAME[vol],
                                          os.path.basename(f), ln,
                                          (volpfx or '') + chap + ('第%s节' % sec if sec else ''),
                                          tok, why))
    print('扫了 %d 处引用、%d 句可对账的承诺\n' % (nref, ntok))
    label = {'gone': '✗ 全书找不到', 'chap': '⚠ 篇号可疑', 'vol': '⚠ 册号可疑',
             'sec': '⚠ 节号可疑', 'ok': '  ok'}
    for r, lvl, v, f, ln, target, tok, why in sorted(found):
        print('%s  %s %s:%d' % (label[lvl], v, f, ln))
        print('      指向 %s，说那里有：「%s」' % (target, tok))
        if why:
            print('      %s' % why)
    n = len([x for x in found if x[1] != 'ok'])
    print('\n嫌疑 %d 处（三档都可能是误报：换了说法、拆了词、或引用的是隔壁那句）' % n)


if __name__ == '__main__':
    main()
