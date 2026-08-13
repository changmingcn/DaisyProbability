#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查成书 HTML 的结构与 MathJax 覆盖。

浏览器视觉验收仍由真实 Chromium 做；本脚本是可重复的构建闸，保证源码里的
数学标记没有退回 CSS 仿画、PNG、sub/sup 或未转换的普通文本。
"""

import argparse
import glob
import html
from html.parser import HTMLParser
import os
import re
import sys


HERE = os.path.dirname(os.path.abspath(__file__))


class BookHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.math_nodes = []
        self.outside_math = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        is_math = tag == 'span' and data.get('data-math') == 'true'
        ignored = tag in {'script', 'style', 'noscript'} or 'tail' in (
            data.get('class') or '').split()
        inherited_math = self.stack[-1][2] if self.stack else False
        inherited_ignore = self.stack[-1][3] if self.stack else False
        self.stack.append((tag, is_math, inherited_math or is_math,
                           inherited_ignore or ignored))
        if is_math:
            self.math_nodes.append(data)

    def handle_startendtag(self, tag, attrs):
        # img/meta/link 没有要检查的文本；不把它们留在栈上。
        return

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        in_math = self.stack[-1][2] if self.stack else False
        ignored = self.stack[-1][3] if self.stack else False
        if not in_math and not ignored:
            self.outside_math.append(data)


def count(pattern, value):
    return len(re.findall(pattern, value, re.DOTALL | re.MULTILINE))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('vol', nargs='?', default='', help='分册目录，如 vol4')
    parser.add_argument('-i', '--input', help='另行指定成书 HTML')
    args = parser.parse_args()

    book = os.path.join(HERE, args.vol) if args.vol else HERE
    title_path = os.path.join(book, 'TITLE')
    title = (open(title_path, encoding='utf-8').read().strip()
             if os.path.exists(title_path) else '数学概念笔记')
    output = args.input or os.path.join(book, 'html', title + '.html')
    content_files = sorted(glob.glob(os.path.join(book, 'content', '*.md')))
    failures = []
    passes = []

    def check(condition, label, detail=''):
        if condition:
            passes.append(label)
        else:
            failures.append('%s%s' % (label, ': ' + detail if detail else ''))

    check(os.path.isfile(output), '成书 HTML 已生成', output)
    check(bool(content_files), '找到了本册 content/*.md')
    if failures:
        for item in failures:
            print('FAIL', item)
        return 1

    source = '\n'.join(open(path, encoding='utf-8').read()
                       for path in content_files)
    page = open(output, encoding='utf-8').read()
    body = page.split('<body>', 1)[1] if '<body>' in page else ''
    parsed = BookHTMLParser()
    parsed.feed(page)

    source_matrix = count(r'\[\[m:[^\]]+\]\]', source)
    source_dimension = count(r'\[\[t:[^\]]+\]\]', source)
    source_fraction = count(r'\[\[(?![mt]:)[^\]]+\]\]', source)
    html_matrix = sum(n.get('data-math-kind') == 'matrix'
                      for n in parsed.math_nodes)
    html_dimension = sum(n.get('data-math-kind') == 'dimension-fraction'
                         for n in parsed.math_nodes)
    html_fraction = sum(n.get('data-math-kind') == 'fraction'
                        for n in parsed.math_nodes)

    check('mathjax@4.0.0/tex-svg.js' in page,
          'MathJax 4.0.0 SVG 引擎已固定版本')
    check(len(parsed.math_nodes) > source_matrix + source_dimension + source_fraction,
          '普通坐标、数字、变量和算式也进入 MathJax')
    check(html_matrix == source_matrix, '矩阵标记逐一进入 MathJax',
          '%d != %d' % (html_matrix, source_matrix))
    check(html_dimension == source_dimension, '量纲分数逐一进入 MathJax',
          '%d != %d' % (html_dimension, source_dimension))
    check(html_fraction == source_fraction, '普通分数逐一进入 MathJax',
          '%d != %d' % (html_fraction, source_fraction))
    check(body.count('\\(') == len(parsed.math_nodes),
          '每个数学节点都有 MathJax 起始定界符')
    check(body.count('\\)') == len(parsed.math_nodes),
          '每个数学节点都有 MathJax 结束定界符')
    check(all(node.get('data-tex') for node in parsed.math_nodes),
          '每个数学节点保留可审计 TeX')

    check('[[' not in body and ']]' not in body, '没有未转换的双括号标记')
    outside = ''.join(parsed.outside_math)
    check(not re.search(r'~[^~]+~|\^[^^]+\^', outside),
          '没有未转换的上下标轻标记')
    check('<sub' not in body and '<sup' not in body,
          '上下标没有退回 HTML sub/sup')
    check(not re.search(r'class="(?:frac|mat)(?:\s|\")', body),
          '没有 CSS 仿画分数或矩阵')
    check('data:image/png;base64,' in body and '<figure>' in body,
          '正文插图仍内嵌在单文件 HTML')
    check(count(r'<figure>', body) == count(r'^FIG:', source),
          '插图数与源码一致')
    check(count(r'class="chapter"', body) == len(content_files),
          '所有内容文件都进入成书')
    check(count(r'class="pagebreak"', body) == count(r'^PAGEBREAK$', source),
          '显式分页标记全部保留')
    check(count(r'class="center center-big"', body) == count(r'^CENTERBIG:', source),
          '居中大公式标记全部保留')

    # 运算符、希腊字母、坐标和普通数字都必须位于 data-math 节点。
    check(not re.search(r'[×＝＋−－=·≠≤≥→⟺√±°Σελπ⁻¹²³ᵀ′]', outside),
          '数学运算符与特殊符号没有落在 MathJax 外')
    check(not re.search(r'\([+\-−]?[A-Za-z0-9]+\s*,', outside),
          '坐标写法没有落在 MathJax 外')
    number_check = re.sub(
        r'(?<![A-Za-z0-9])[ABC]\d+(?![A-Za-z0-9])', '', outside)
    check(not re.search(r'\d', number_check),
          '正文数字没有落在 MathJax 外（习题编号除外）')

    # \text{中文} 是量纲的正式 TeX；除此之外，数学 TeX 不应吞进中文标点。
    bad_tex = []
    for node in parsed.math_nodes:
        tex = html.unescape(node.get('data-tex', ''))
        without_text = re.sub(r'\\text\{[^{}]*\}', '', tex)
        if re.search(r'[\u3400-\u9fff，；：。！？、]', without_text):
            bad_tex.append(tex)
    check(not bad_tex, 'MathJax 只在量纲 \\text{} 中承载汉字',
          bad_tex[0] if bad_tex else '')
    check(
        all(marker not in page for marker in (
            'math-drop-mixed', '--math-drop', 'data-drop-ratio',
            'translateY(var(--math-drop')),
        '方阵和列向量使用 MathJax 正常基线，没有自定义下移')

    for label in passes:
        print('PASS', label)
    if failures:
        for item in failures:
            print('FAIL', item)
        print('%d PASS / %d FAIL' % (len(passes), len(failures)))
        return 1
    print('%d PASS / 0 FAIL — %d MathJax 节点' % (
        len(passes), len(parsed.math_nodes)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
