#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把正文里的斜杠写法分数（1/2^n^、p/q、1/(n+1)……）改写成 [[分子|分母]] 标记。

汉字分数由 cn_fractions.py 处理；这个脚本管的是另一类：**分母带指数或字母**的，
比如 1/2^n^ —— 它们从来没被转换过，一直是斜杠形式。
两个脚本都跳过 {{}} 保护区，也都不碰已经转换好的 [[...]]。
"""
import glob
import re
import sys

# 顺序要紧：长的、特殊的排前面（1/10000 必须排在 1/100 前面）
RULES = [
    ('1 /（3 × 10^n^）', r'[[1|3\times 10^n]]'),
    ('1/2^n+1^',         '[[1|2^{n+1}]]'),
    ('1/2^N^',           '[[1|2^N]]'),
    ('1/2^M^',           '[[1|2^M]]'),
    ('1/2^n^',           '[[1|2^n]]'),
    ('1/10^N^',          '[[1|10^N]]'),
    ('1/10^n^',          '[[1|10^n]]'),
    ('4/10^n^',          '[[4|10^n]]'),
    ('1/(n+1)',          '[[1|n+1]]'),
    ('p/q',              '[[p|q]]'),
    ('1/10000000',       '[[1/10000000]]'),
    ('1/10000',          '[[1/10000]]'),
    ('1/100',            '[[1/100]]'),
]

SKIP = re.compile(r'(\[\[[^\]]*\]\]|\{\{.*?\}\})')   # 已转换的 / 受保护的，一律不动


LOOKUP = dict(RULES)
# 必须**单遍**替换：串行套用规则时，后一条会啃掉前一条刚生成的结果
# （1/10000 → [[1/10000]]，接着 1/100 规则又在里面命中 → [[[[1/100]]00]]）。
# 合并成一个最长优先的正则，每个位置只被消费一次。
ONE_PASS = re.compile('|'.join(re.escape(src) for src, _ in RULES))


def convert(text, counts):
    def repl(m):
        src = m.group(0)
        counts[src] = counts.get(src, 0) + 1
        return LOOKUP[src]

    out = []
    for part in SKIP.split(text):
        if part.startswith('[[') or part.startswith('{{'):
            out.append(part)          # 已转换的 / 受保护的，不动
        else:
            out.append(ONE_PASS.sub(repl, part))
    return ''.join(out)


def main():
    counts = {}
    for path in sorted(glob.glob('content/*.md')):
        src = open(path, encoding='utf-8').read()
        out = convert(src, counts)
        if out != src:
            open(path, 'w', encoding='utf-8').write(out)
    total = sum(counts.values())
    print('转换了 %d 处：' % total)
    for src, _ in RULES:
        if counts.get(src):
            print('   %-18s x%d' % (src, counts[src]))
    # 复查：保护区外还有没有漏网的斜杠分数
    leftover = []
    pat = re.compile(r'[0-9a-zA-Z]\s*/\s*[0-9a-zA-Z（(]')
    for path in sorted(glob.glob('content/*.md')):
        for ln, line in enumerate(open(path, encoding='utf-8'), 1):
            for part in SKIP.split(line):
                if part.startswith('[[') or part.startswith('{{'):
                    continue
                if pat.search(part):
                    leftover.append('%s:%d  %s' % (path, ln, part.strip()[:60]))
    print('\n保护区外剩余斜杠写法: %d' % len(leftover))
    for s in leftover:
        print('   ', s)
    return 0 if not leftover else 1


if __name__ == '__main__':
    sys.exit(main())
