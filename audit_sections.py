#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交叉引用的**节号**对账：`第X篇第Y节` 指到的那一节，真的在讲被引的那个词吗？

来历（2026-08-03）：第四篇 C7 写着「第三篇第五节认识了**上确界**」——错的，
上确界在第三篇第六节，第五节是「比大小怎么办」。`audit_refs.py` 抓不到这一类：
它只查**引号里的承诺**，而这里被引的词是加粗的。全册 41 处节号引用里只有这一处
对不上，但同类错在加内容时还会再出现，所以做成一道会 FAIL 的闸。

两道检查：

  [S1] 存在性 —— 指到的篇、节存在吗？（写错篇号、删了一节忘了改引用）
  [S2] 走错门 —— 紧挨着引用的那个加粗词，**在目标篇里找得到、却不在你指的
       那一节**。这时才报：说明这个词是真的、也定位得了，只是节号指错了。

  [S2] 这条判据是试出来的。先试过"加粗词必须出现在目标小节里"，19 处误报——
  因为体例规定**转述也用加粗**（"列个方程""又出现了""最容易上手"都是转述，
  正文里当然找不到原词）。加上"这个词在本篇别处找得到"这一条，才把转述滤掉：
  转述在整篇里都找不到，走错门的术语只在隔壁那一节找得到。

用法：
    python3 audit_sections.py            # 四册全查
    python3 audit_sections.py --vol vol4 # 只查一册（vol1 就是仓库根）

退出码非 0 ＝ 有 FAIL，publish.sh 会当场中止。
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
VOLS = ('vol1', 'vol2', 'vol3', 'vol4')
CN = '零一二三四五六七八九十'

# 引用形如「第三篇第五节」。前面紧挨着「册」的（第一册第二篇第三节）指的是别的册，
# 本脚本只做册内对账，跳过它们。
REF = re.compile(r'第([一二三四五六七八九十]+)篇第([一二三四五六七八九十]+)节')
H1 = re.compile(r'(?m)^#\s*第([一二三四五六七八九十]+)篇')
H2 = re.compile(r'(?m)^##\s*([一二三四五六七八九十]+)、(.*)$')
BOLD = re.compile(r'\*\*([^*]{1,40})\*\*')
PUNCT = re.compile(r'[，。：；、？！""''（）\s\d]')


def cn2int(s):
    if s == '十':
        return 10
    if len(s) == 2 and s[0] == '十':
        return 10 + CN.index(s[1])
    if len(s) == 2 and s[1] == '十':
        return CN.index(s[0]) * 10
    if len(s) == 1:
        return CN.index(s)
    return -1


def content_dir(vol):
    return os.path.join(ROOT, 'content') if vol == 'vol1' \
        else os.path.join(ROOT, vol, 'content')


def load(vol):
    """返回 {篇号: (标题, {节号: (节标题, 节正文)})}，以及文件清单。"""
    d = content_dir(vol)
    if not os.path.isdir(d):
        return None, []
    books, files = {}, sorted(
        os.path.join(d, f) for f in os.listdir(d) if f.endswith('.md'))
    for path in files:
        text = open(path, encoding='utf-8').read()
        m = H1.search(text)
        if not m:
            continue                       # 开篇、尾声、附录、封面页不编篇号
        no = cn2int(m.group(1))
        heads = list(H2.finditer(text))
        secs = {}
        for i, h in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            secs[cn2int(h.group(1))] = (h.group(2).strip(), text[h.start():end])
        books[no] = (os.path.basename(path), secs)
    return books, files


def sentence_around(text, pos, with_offset=False):
    """取引用所在的那一句（按中文句读和盒子分隔符 // 切）。"""
    left = max(text.rfind(c, 0, pos) for c in ('。', '；', '//', '\n', '？', '！'))
    right = min((r for r in (text.find(c, pos) for c in
                             ('。', '；', '//', '\n', '？', '！')) if r != -1),
                default=len(text))
    start = left + 1
    return (text[start:right], start) if with_offset else text[start:right]


def audit(vol, verbose=False):
    books, files = load(vol)
    if books is None:
        return 0, 0, []
    refs = fails = 0
    reports = []
    for path in files:
        text = open(path, encoding='utf-8').read()
        for m in REF.finditer(text):
            if '册' in text[max(0, m.start() - 3):m.start()]:
                continue                   # 跨册引用，本脚本不管
            refs += 1
            p, s = cn2int(m.group(1)), cn2int(m.group(2))
            where = '%s:%d' % (os.path.basename(path),
                               text.count('\n', 0, m.start()) + 1)
            if p not in books:
                fails += 1
                reports.append('[S1] %s  第%s篇不存在 —— %s'
                               % (where, m.group(1), m.group(0)))
                continue
            secs = books[p][1]
            if s not in secs:
                fails += 1
                reports.append('[S1] %s  %s 没有第%s节（共 %d 节）'
                               % (where, m.group(0), m.group(2), len(secs)))
                continue
            title, body = secs[s]
            # 只看**紧挨着**引用的加粗词（前后 12 字内），且**不许跨分句**——
            # 盒子里的 // 隔开的是两句话，跨过去就会把上一句的词捞进来（试出来的）
            sent, off = sentence_around(text, m.start(), with_offset=True)
            rel = m.start() - off
            near = sent[max(0, rel - 12):rel + (m.end() - m.start()) + 12]
            terms = [t for t in BOLD.findall(near)
                     if len(t) <= 6 and not PUNCT.search(t)
                     and '篇' not in t and '节' not in t]
            wrong = []
            for t in terms:
                if t in body:
                    continue                       # 指对了
                elsewhere = sorted(k for k, (_, b) in secs.items() if t in b)
                if elsewhere:                      # 本篇找得到，只是不在这一节
                    wrong.append((t, elsewhere))
            if wrong:
                fails += 1
                for t, el in wrong:
                    reports.append(
                        '[S2] %s  %s 是「%s」，可「%s」在第%s节，不在这一节\n'
                        '        句子：%s'
                        % (where, m.group(0), title, t,
                           '、'.join(CN[k] for k in el),
                           sentence_around(text, m.start()).strip()))
            elif verbose:
                reports.append('  ok  %s  %s -> %s' % (where, m.group(0), title))
    return refs, fails, reports


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vol', choices=VOLS)
    ap.add_argument('-v', '--verbose', action='store_true')
    args = ap.parse_args()
    total_refs = total_fails = 0
    for vol in ([args.vol] if args.vol else VOLS):
        refs, fails, reports = audit(vol, args.verbose)
        total_refs += refs
        total_fails += fails
        print('%s：%d 处册内节号引用，%d 处对不上' % (vol, refs, fails))
        for r in reports:
            print('   ', r)
    print()
    if total_fails:
        print('✗ 节号对账 FAIL：%d 处（共 %d 处引用）' % (total_fails, total_refs))
        return 1
    print('✓ 节号对账通过（%d 处引用全部指对）' % total_refs)
    return 0


if __name__ == '__main__':
    sys.exit(main())
