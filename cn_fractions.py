#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把正文里的「X分之Y」汉字分数改写成 [[Y/X]] 标记（编译时渲染成上下分列的分数图）。

注意读法：**X分之Y ＝ Y/X**，分母在前、分子在后。这个顺序反了就全错，
所以脚本会把每一条映射打出来，必须肉眼过一遍。
"""
import glob
import re
import sys

DIGIT = {'零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5,
         '六': 6, '七': 7, '八': 8, '九': 9}
UNIT = {'十': 10, '百': 100, '千': 1000, '万': 10000}


def parse_cn(s):
    """解析中文数字，如 二十七 -> 27，一百 -> 100，十六 -> 16。"""
    total, section, number = 0, 0, 0
    for ch in s:
        if ch in DIGIT:
            number = DIGIT[ch]
        elif ch in UNIT:
            u = UNIT[ch]
            if u == 10000:
                section = (section + number) * u
                total += section
                section = number = 0
            else:
                if number == 0:
                    number = 1          # 「十六」＝16，不是「零十六」
                section += number * u
                number = 0
        else:
            raise ValueError('未知汉字数字: ' + ch)
    return total + section + number


PAT = re.compile(r'([零一二两三四五六七八九十百千万]+)分之([零一二两三四五六七八九十百千万]+)')


KEEP = re.compile(r'(\{\{.*?\}\})')


def convert(text, audit):
    """转换 X分之Y，但 {{...}} 里的原样保留。

    有些地方汉字写法是**故意的**——比如附录 A「怎么念」那一栏写的是读音
    （念作"二分之一的 n 次方"），换成分数图就自相矛盾了。手工改回来会在
    下次重跑时再次被吃掉，所以这里做成机制：包在 {{}} 里的一律不动。
    """
    def repl(m):
        den = parse_cn(m.group(1))     # 「分之」前面是分母
        num = parse_cn(m.group(2))     # 后面是分子
        audit.setdefault(m.group(0), '%d/%d' % (num, den))
        return '[[%d/%d]]' % (num, den)

    parts = KEEP.split(text)
    return ''.join(p if p.startswith('{{') else PAT.sub(repl, p) for p in parts)


def main():
    audit, changed = {}, 0
    for path in sorted(glob.glob('content/*.md')):
        src = open(path, encoding='utf-8').read()
        out = convert(src, audit)
        if out != src:
            open(path, 'w', encoding='utf-8').write(out)
            changed += 1
    print('改写文件数:', changed)
    print('\n映射表（请逐条核对，X分之Y ＝ Y/X）:')
    for k in sorted(audit, key=lambda s: (len(s), s)):
        print('   %-12s ->  %s' % (k, audit[k]))
    # 剩余的只应该是 {{}} 保护起来的那些
    left = unprotected = 0
    for p in glob.glob('content/*.md'):
        for part in KEEP.split(open(p, encoding='utf-8').read()):
            hits = len(PAT.findall(part))
            left += hits
            if not part.startswith('{{'):
                unprotected += hits
    print('\n剩余汉字写法: %d（其中 %d 处在 {{}} 保护外）' % (left, unprotected))
    return 0 if unprotected == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
