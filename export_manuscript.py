#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 content/*.md 的轻标记展开成一份干净的、可以直接读的 Markdown 稿件。

    python3 export_manuscript.py            # 第一册 -> 数学概念笔记-上部分-稿件.md
    python3 export_manuscript.py vol2       # 第二册

用途：给人读、或者喂给别的工具（比如让 AI 照着做动画）。**不参与 docx 构建**，
所以这里可以放心用 docx 里不许用的字符。标题层级整体下沉一级：TITLE 占 #，
篇占 ##，节占 ###，小节占 ####。
"""
import os
import re
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.join(HERE, sys.argv[1]) if len(sys.argv) > 1 else HERE
TITLE_FILE = os.path.join(BOOK, 'TITLE')
DEFAULT_TITLE = '给小学生讲微积分（上）'
BOOK_TITLE = (open(TITLE_FILE, encoding='utf-8').read().strip()
              if os.path.exists(TITLE_FILE) else DEFAULT_TITLE)
CONTENT = os.path.join(BOOK, 'content')
# 按分册映射，不能写死"有参数即下部分"——vol3 曾差点覆盖第二册的稿件
PART = ({'vol2': '下部分', 'vol3': '第三册', 'vol4': '第四册'}.get(sys.argv[1], sys.argv[1])
        if len(sys.argv) > 1 else '上部分')
OUT = os.path.join(HERE, '数学概念笔记-%s-稿件.md' % PART)

BOX_LABEL = {
    'remember': '必须记住（蓝盒子）',
    'key':      '要点（绿盒子）',
    'task':     '留给姐姐妹妹 · 习题（橙盒子）',
    'dialog':   '对话（橙盒子）',
    'grown':    '长大以后的写法（灰盒子）',
}

# mathtext -> 给人看的写法
MATH = [
    (r'\\varepsilon', 'ε'), (r'\\times', '×'), (r'\\cdot', '·'),
    (r'\\sqrt\{([^}]*)\}', r'√(\1)'), (r'\\frac', '/'),
]


def demath(s):
    for pat, rep in MATH:
        s = re.sub(pat, rep, s)
    s = re.sub(r'\s*×\s*', ' × ', s)          # "3\times 10^n" -> "3 × 10^n"
    s = re.sub(r'_\{([^}]*)\}', lambda m: '_' + brace(m.group(1)), s)
    s = re.sub(r'\^\{([^}]*)\}', lambda m: '^' + brace(m.group(1)), s)
    return s.strip()


def brace(t):
    """单字符下/上标直接跟着写，多字符加花括号，免得歧义。"""
    return t if len(t) == 1 else '{%s}' % t


def frac(inner):
    """[[1/2]] 或 [[1|2^n]] -> 1/2、1/2^n；分子分母里有运算就加括号。"""
    inner = demath(inner)
    parts = inner.split('|') if '|' in inner else inner.split('/', 1)
    if len(parts) != 2:
        return inner
    out = []
    for p in parts:
        p = p.strip()
        out.append('(%s)' % p if re.search(r'[ ＋+×÷−-]', p) else p)
    return '%s/%s' % (out[0], out[1])


def inline(s):
    s = re.sub(r'\{\{(.*?)\}\}', r'\1', s)
    # 必须先把 [[…]] 整段藏起来再处理上下标：分数内部的 ^ 是 mathtext，
    # 不是正文的 ^上标^ 标记。不藏的话，两个分数里的 ^ 会被跨段配成一对，
    # 把 "1/10^n …… 1/(3×10^n)" 毁成 "1/10^{n …… 10}n"。
    spans = []

    def hide(m):
        spans.append(m.group(1))
        return '\x02%d\x03' % (len(spans) - 1)

    s = re.sub(r'\[\[([^\]]+)\]\]', hide, s)
    s = re.sub(r'~([^~\n]+)~', lambda m: '_' + brace(m.group(1)), s)
    s = re.sub(r'\^([^^\n]+)\^', lambda m: '^' + brace(m.group(1)), s)
    s = re.sub(r'\x02(\d+)\x03', lambda m: frac(spans[int(m.group(1))]), s)
    return s.replace(r'\|', '|')


def emit(out, text=''):
    out.append(text)


def convert(path, out):
    lines = open(path, encoding='utf-8').read().split('\n')
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue

        if s.startswith('### '):
            emit(out, '#### ' + inline(s[4:]));  emit(out)
        elif s.startswith('## '):
            emit(out, '### ' + inline(s[3:]));   emit(out)
        elif s.startswith('# '):
            emit(out, '## ' + inline(s[2:]));    emit(out)
        elif s.startswith('TITLE:'):
            emit(out, '# ' + inline(s[6:].strip())); emit(out)
        elif s.startswith('SUB:'):
            sub = s[4:].strip()
            if sub:
                emit(out, '*%s*' % inline(sub)); emit(out)
        elif s.startswith('FIG:'):
            spec = s[4:].split('|')
            name = spec[0].strip()
            cap = inline(spec[1].strip()) if len(spec) > 1 else ''
            emit(out, '![%s](figs/%s)' % (cap, name))
            emit(out, '*〔插图 `%s`〕%s*' % (name, cap))
            emit(out)
        elif s.startswith('BOX['):
            m = re.match(r'BOX\[(\w+)\]:\s*(.*?)\s*::\s*(.*)$', s)
            kind, title, body = m.group(1), m.group(2), m.group(3)
            emit(out, '> **〔%s〕%s**' % (BOX_LABEL.get(kind, kind), inline(title)))
            emit(out, '>')
            for b in body.split('//'):
                b = b.strip()
                emit(out, '> ' + inline(b) if b else '>')
            emit(out)
        elif s == 'TABLE:':
            rows = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = lines[i].strip().replace(r'\|', '\x00')
                row = re.sub(r'\[\[[^\]]+\]\]',
                             lambda m: m.group(0).replace('|', '\x01'), row)
                cells = [c.strip().replace('\x00', r'\|').replace('\x01', '|')
                         for c in row.strip('|').split('|')]
                rows.append([inline(c) for c in cells])
                i += 1
            if rows:
                emit(out, '| ' + ' | '.join(rows[0]) + ' |')
                emit(out, '|' + '---|' * len(rows[0]))
                for r in rows[1:]:
                    r = (r + [''] * len(rows[0]))[:len(rows[0])]
                    emit(out, '| ' + ' | '.join(r) + ' |')
                emit(out)
            continue
        elif s.startswith('- '):
            emit(out, '- ' + inline(s[2:]))
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ''
            if not nxt.startswith('- '):
                emit(out)
        elif s == '---':
            emit(out, '* * *'); emit(out)
        elif s.startswith('CENTER:'):
            emit(out, '> ' + inline(s[7:].strip())); emit(out)
        else:
            emit(out, inline(s)); emit(out)
        i += 1


def main():
    out = []
    for f in sorted(glob.glob(os.path.join(CONTENT, '*.md'))):
        convert(f, out)
    text = '\n'.join(out)
    text = re.sub(r'\n{3,}', '\n\n', text).strip() + '\n'
    open(OUT, 'w', encoding='utf-8').write(text)
    print('wrote', OUT)
    print('  %d 行，%d 字符' % (text.count('\n') + 1, len(text)))
    leftover = [l for l in text.split('\n')
                if re.search(r'\[\[|\]\]|^FIG:|^BOX\[|^TABLE:|^CENTER:|^TITLE:|^SUB:|~|\^\w+\^', l)]
    print('  残留标记：%d 行' % len(leftover))
    for l in leftover[:5]:
        print('    ->', l[:90])
    # 上下标的花括号必须配平 —— 跨段配对那个 bug 就是靠这条看出来的
    bad = [l for l in text.split('\n') if l.count('{') != l.count('}')]
    print('  花括号不配平：%d 行' % len(bad))
    for l in bad[:5]:
        print('    ->', l[:90])
    if leftover or bad:
        sys.exit(1)


if __name__ == '__main__':
    main()
