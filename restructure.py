#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把原第三篇拆成三篇：实数 / ε–N 工具箱 / 八大定理。

拆的依据是"每篇一件事"，不是长度：
  第三篇 数是什么      —— 循环小数、不循环小数、实数约定、比大小、上确界、完备
  第四篇 语言有多好用  —— ε–N 的四个（新增第五个）例子＋两个常备动作
  第五篇 八种说法      —— 点集词汇（邻域/开闭集/区间套/开覆盖）＋八大定理
"""
import re
import os

C = 'content'


def blocks(text):
    """按 '## ' 切块，返回 (前言, [(标题, 正文), ...])"""
    parts = re.split(r'(?m)^(## .+)$', text)
    return parts[0], [(parts[i], parts[i + 1]) for i in range(1, len(parts), 2)]


def subblocks(body):
    """按 '### ' 切小节，返回 (小节前的引子, [(标题, 正文), ...])"""
    parts = re.split(r'(?m)^(### .+)$', body)
    return parts[0], [(parts[i], parts[i + 1]) for i in range(1, len(parts), 2)]


src = open(os.path.join(C, '03-reals.md'), encoding='utf-8').read()
head, secs = blocks(src)
S = {t: b for t, b in secs}


def get(prefix):
    for t, b in secs:
        if t.startswith('## ' + prefix):
            return t, b
    raise KeyError(prefix)


_, s1 = get('一、')
_, s2 = get('二、')
_, s3 = get('三、')
_, s4 = get('四、')
_, s5 = get('五、')      # ε–N 好用
_, s6 = get('六、')      # 够用的几个词
_, s7 = get('七、')      # 没有洞
_, s8 = get('八、')      # 习题
_, sg = get('长大以后的写法')

# ---- 拆 §六：前四个词归第三篇（关于数），后四个归第五篇（点集词汇）
lead6, subs6 = subblocks(s6)
num_words = [x for x in subs6 if x[0].startswith('### 上界') or x[0].startswith('### 上确界')]
set_words = [x for x in subs6 if x not in num_words]
assert len(num_words) == 2 and len(set_words) == 4, (len(num_words), len(set_words))

# ---- 拆 §五：四个例子，各自升级为第四篇的一节
lead5, subs5 = subblocks(s5)
assert len(subs5) == 4, len(subs5)

CN = '一二三四五六七八九'


def renum(subs, start=0):
    """### 例一（热身）：… → ## 一、例一（热身）：…"""
    out = []
    for k, (title, body) in enumerate(subs):
        name = title[4:].strip()
        out.append('## %s、%s\n%s' % (CN[start + k], name, body))
    return ''.join(out)


# ================================================================ 第三篇
ch3 = head + get('一、')[0] + s1 \
    + get('二、')[0] + s2 \
    + get('三、')[0] + s3 \
    + get('四、')[0] + s4 \
    + '## 五、说清"最大"不够用：上界与上确界\n' \
    + '\n第六节要问"数轴上有没有洞"，第五篇要用八种说法回答它。在那之前，先把**关于数的次序**的几个词说清楚。\n' \
    + ''.join(t + b for t, b in num_words) \
    + '## 六、"数轴上没有洞"到底在说什么' + s7 \
    + '## 七、习题\n' + '__EX3__\n' \
    + '## 长大以后的写法\n' + '__GROWN3__\n'

# ================================================================ 第四篇
ch4 = '''# 第四篇　ε–N 这套语言，到底有多好用

CENTER: 直观负责发现，ε–N 负责证明

第三篇第二节，我们用 ε–N 证明了 1.4，1.41，1.414…… 收敛到 √2。那不是一次孤零零的表演。

到这里为止，ε–N 已经替我们干了不少活：

- **第一篇**：证明 0.333… 就是 [[1/3]]。
- **第二篇**：证明那队部分和满足柯西条件；还证明了那队混起来的数**没有**极限。
- **第三篇**：证明那队小数收敛到 √2，并且它的平方**确实**是 2。

每一次都是同一个套路：**直观先看出现象，ε–N 负责把它钉死。**

这一篇集中做五个例子。请注意：**每一个的开头都是一句"这还用说吗"的话**——然后我们把它翻译成"不管希希怎么挑剔，我都能回答"。

''' + renum(subs5, 0) + '''## 五、例五：有极限的队伍，一定被困住

**直观：**一队数既然都奔向同一个地方，当然不会跑得漫无边际。

这句话下一篇要用，所以现在把它证掉。

BOX[key]: ε–N 证明 :: 设这队数奔向 L。// 这一次**我们自己挑 ε**——就取 ε ＝ 1。// 于是有一个关口 N：n ＞ N 时，每一项都离 L 不到 1，// 也就是全都挤在 L 左右各 1 的那一小段里。// 关口**以前**呢？只有 a~1~ 到 a~N~ 这**有限多**项，// 有限多个数总有最大的、也总有最小的。// 把这两拨合起来取最大最小，整队数就被夹住了。**证毕。**

BOX[remember]: 注意这里的新动作 :: 前面几个例子都是**希希给 ε，我们回答**。// 这一次反过来了：**我们自己挑了一个 ε**（挑了 1）。// 定义说"对任意 ε 都成立"，那当然也包括我们随手挑的那个。// **"对任意"意味着我们可以任意取用**——这是 ε–N 定义的另一半好处。// 第五篇证柯西准则时，第一步用的就是这一招。

## 六、这一篇学到的两个动作

五个例子里，有两个动作反复出现。它们比任何一条具体结论都值钱。

BOX[remember]: 动作一：取靠后的那个关口 :: 希希只提**一次**要求，我们却常常要向**好几个人**要关口。// 拿到几个以后，取**最靠后**的那一个，所有条件就能同时成立。// 出现在：第二篇证"极限只有一个"、例二夹逼、例三求和，第五篇还会再用。

BOX[remember]: 动作二：把 ε 掰成两半 :: 要证一段路不到 ε，就把它拆成两截，每截各证不到 ε 的一半。// 出现在：例三求和；第五篇证柯西准则。// 以后你会见到掰成三半、掰成 n 半的版本。

BOX[key]: 这一篇的一句话 :: 五个例子，一个模式：**先看出现象，再把它翻译成"不管 ε 多小，我都能给出一个有限的 N"**。// **直观负责发现，ε–N 负责证明。**// 这套语言值得学，不是因为它复杂，// 而是因为它能把"我觉得"变成"**我证明了**"。

## 七、习题
__EX4__
## 长大以后的写法

BOX[grown]: 课本上会这样写 :: 例二那条叫**夹逼定理**（也叫迫敛性、两边夹定理）。// 例三属于**极限的四则运算法则**：和、差、积、商四条，证法都是"掰 ε ＋ 三角不等式"。// 例四那句话的正式说法是：**极限保持非严格不等号，不保持严格不等号**。// 例五叫**收敛数列必有界**；反过来不成立（有界不一定收敛，第二篇那队混起来的数就是反例）。// 三角不等式写作 | x + y | ≤ | x | + | y |。
'''

# ================================================================ 第五篇
old4 = open(os.path.join(C, '04-eight-theorems.md'), encoding='utf-8').read()
h4, secs4 = blocks(old4)
h4 = h4.replace('# 第四篇　同一件事的八种说法', '# 第五篇　同一件事的八种说法')

new5 = h4 + '## 一、先备几个词\n' \
    + '\n下面八句话里会用到几个点集的说法。都很朴素，一个一个来。\n' \
    + ''.join(t + b for t, b in set_words)
for k, (t, b) in enumerate(secs4):
    name = t[3:].strip()
    if '长大以后' in name:
        new5 += t + b
    else:
        # 原来的一二三四五 → 二三四五六
        name = re.sub(r'^[一二三四五六七八九]、', '', name)
        new5 += '## %s、%s\n%s' % (CN[k + 1], name, b)

open(os.path.join(C, '03-reals.md'), 'w', encoding='utf-8').write(ch3)
open(os.path.join(C, '04-epsilon-toolkit.md'), 'w', encoding='utf-8').write(ch4)
open(os.path.join(C, '05-eight-theorems.md'), 'w', encoding='utf-8').write(new5)
os.remove(os.path.join(C, '04-eight-theorems.md'))

# 把原习题/长大以后暂存，稍后手工重分
open('_ex3.txt', 'w', encoding='utf-8').write(s8)
open('_grown3.txt', 'w', encoding='utf-8').write(sg)
print('拆分完成。习题与"长大以后"已暂存到 _ex3.txt / _grown3.txt，待重分。')
for f in sorted(os.listdir(C)):
    txt = open(os.path.join(C, f), encoding='utf-8').read()
    print('  %-26s %5d 字  %s' % (f, len(txt),
          ' '.join(re.findall(r'(?m)^## (\S{1,6})', txt))))
