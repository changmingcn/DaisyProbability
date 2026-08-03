#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《给小学生讲概率论》插图。

约定同前三册：中文用 Hiragino Sans GB，数学走 mathtext，两者绝不混在同一个字符串里。
中文字体缺 U+2212，图里的减号只能用"减"字或 ASCII 连字符。

开篇那三个数字（30 次里各中了几次）不是编的，是下面 run_trials() 用固定种子跑出来的，
正文引用的就是它。改了这里的种子或做法，**正文那张表要跟着改** —— 下面有 assert 卡着。
"""
import math
import os
import random

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon

plt.rcParams['font.sans-serif'] = ['Hiragino Sans GB', 'Arial Unicode MS', 'Songti SC']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'dejavusans'

NAVY, ORANGE, GREEN = '#1F3A6E', '#E8743B', '#2E9E6B'
GREY, LIGHT, BAND = '#9AA5B1', '#DCE7F7', '#FBE3D6'
RED = '#C0392B'

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
os.makedirs(OUT, exist_ok=True)

R3 = math.sqrt(3)          # 内接正三角形的边长 ＝ √3 × 半径
SEED30, SEED10K = 4, 400   # 4 ＝ 第四册；一万次那一行另跑一次，别和 30 次共用流


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  wrote', name)


# ---------------------------------------------------------------- 三个动手实验
def one_trial(rng):
    """严格照正文写的三种做法各做一次，返回三个"中了没有"。"""
    # ① 两个骰子选 36 等分点里的两个（撞了就重掷），连成一条弦
    i = rng.randrange(6) * 6 + rng.randrange(6)
    j = rng.randrange(6) * 6 + rng.randrange(6)
    while j == i:
        j = rng.randrange(6) * 6 + rng.randrange(6)
    k = min((i - j) % 36, (j - i) % 36)
    a = 2 * math.sin(k * math.pi / 36) > R3
    # ② 半径十等分，抽签 1–10，中点取第 k 格的正中
    b = (rng.randrange(1, 11) - 0.5) / 10 < 0.5
    # ③ 圆面上撒一粒米当中点（落在圆外就重撒）
    while True:
        x, y = rng.uniform(-1, 1), rng.uniform(-1, 1)
        if x * x + y * y <= 1:
            break
    c = math.hypot(x, y) < 0.5
    return a, b, c


def run_trials(n, seed):
    rng = random.Random(seed)
    hit = [0, 0, 0]
    for _ in range(n):
        for idx, ok in enumerate(one_trial(rng)):
            hit[idx] += ok
    return hit


THIRTY = run_trials(30, SEED30)
TEN_K = run_trials(10000, SEED10K)
# 正文里印着这两行数，动了上面就会在这里当场断掉
assert THIRTY == [13, 18, 7], THIRTY
assert TEN_K == [3143, 4972, 2484], TEN_K


# ---------------------------------------------------------------- 抛硬币的记录
def coin_run(n, seed):
    """抛 n 次硬币，返回每一步的"正面比例"和几个checkpoint的正面数。"""
    rng = random.Random(seed)
    heads = 0
    steps, freq, marks = [], [], {}
    for i in range(1, n + 1):
        heads += rng.random() < 0.5
        if i >= 8:
            steps.append(i)
            freq.append(heads / i)
        if i in (10, 100, 1000, 10000, 100000):
            marks[i] = heads
    return steps, freq, marks


def gap_average(runs, seed):
    """把"抛 n 次"重做很多遍，看"正面比反面多几个"平均有多大。"""
    rng = random.Random(seed)
    marks = (10, 100, 1000, 10000)
    acc = {m: 0 for m in marks}
    for _ in range(runs):
        h = 0
        for i in range(1, 10001):
            h += rng.random() < 0.5
            if i in acc:
                acc[i] += abs(2 * h - i)
    return {m: acc[m] / runs for m in marks}


COIN_STEPS, COIN_FREQ, COIN_MARKS = coin_run(100000, 7)
GAPS = gap_average(200, 21)
# 第七篇那两张表印的就是这些数
assert COIN_MARKS == {10: 7, 100: 54, 1000: 537, 10000: 5030, 100000: 50039}, COIN_MARKS
assert [round(GAPS[m], 1) for m in (10, 100, 1000, 10000)] == [2.6, 8.3, 26.5, 72.1], GAPS


# ---------------------------------------------------------------- 分金问题
def replay_match(rounds, seed):
    """从 2 比 1 开始，把剩下的局打完，重复若干遍，数姐姐赢了几遍。"""
    rng = random.Random(seed)
    won = 0
    for _ in range(rounds):
        a, b = 2, 1
        while a < 3 and b < 3:
            if rng.random() < 0.5:
                a += 1
            else:
                b += 1
        won += a == 3
    return won


SPLIT40 = replay_match(40, 4)      # 4 ＝ 第四册；没有挑种子
assert SPLIT40 == 31, SPLIT40      # 开篇正文印的就是它


# ---------------------------------------------------------------- p00
def fig_p00():
    """分金：把没打完的两局补完，四条路，姐姐赢三条。

    两组分叉之间要留出空档，好让"这一局其实不会打"那句注解有地方站，
    并且用一条虚线牵到它说的那支箭头上——第一版它悬在中间，指向不明。
    """
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ROOT_Y, UP_Y, DN_Y = 1.45, 2.45, 0.60
    LEAF = (2.80, 2.10, 1.10, 0.10)

    ax.add_patch(Rectangle((-0.05, ROOT_Y - 0.31), 1.05, 0.62, facecolor=LIGHT,
                           edgecolor=NAVY, lw=1.4))
    ax.text(0.475, ROOT_Y, '2 比 1', ha='center', va='center', fontsize=13, color=NAVY)

    for y, mark in ((UP_Y, '正'), (DN_Y, '反')):
        ax.annotate('', xy=(2.32, y), xytext=(1.05, ROOT_Y),
                    arrowprops=dict(arrowstyle='-|>', color=GREY, lw=1.3))
        ax.text(1.62, (ROOT_Y + y) / 2 + 0.16, mark, ha='center',
                fontsize=11.5, color=ORANGE)

    plan = ((LEAF[0], UP_Y, '正', '姐姐', False, False),
            (LEAF[1], UP_Y, '反', '姐姐', False, True),
            (LEAF[2], DN_Y, '正', '姐姐', False, False),
            (LEAF[3], DN_Y, '反', '妹妹', True, False))
    for y, ytop, mark, who, is_b, dashed in plan:
        ax.annotate('', xy=(4.42, y), xytext=(2.42, ytop),
                    arrowprops=dict(arrowstyle='-|>', color=GREY, lw=1.3,
                                    ls='--' if dashed else '-'))
        ax.text(3.4, (ytop + y) / 2 + 0.15, mark, ha='center', fontsize=11.5,
                color=ORANGE)
        ax.add_patch(Rectangle((4.5, y - 0.31), 1.5, 0.62,
                               facecolor=BAND if is_b else LIGHT,
                               edgecolor=RED if is_b else NAVY, lw=1.4))
        ax.text(5.25, y, who + '拿走', ha='center', va='center', fontsize=12,
                color=RED if is_b else NAVY)

    ax.text(6.22, (LEAF[0] + LEAF[2]) / 2, '姐姐赢' + chr(10) + '三条',
            ha='left', va='center', fontsize=11, color=NAVY, linespacing=1.5)
    ax.text(6.22, LEAF[3], '妹妹赢' + chr(10) + '一条', ha='left', va='center',
            fontsize=11, color=RED, linespacing=1.5)

    ax.annotate('这一局其实不会打' + chr(10) + '（姐姐已经够 3 分了）',
                xy=(3.75, (UP_Y + LEAF[1]) / 2 - 0.03), xytext=(3.15, 1.42),
                ha='center', va='center', fontsize=9.5, color=GREY,
                linespacing=1.5,
                arrowprops=dict(arrowstyle='-|>', color=GREY, lw=1.0,
                                ls=(0, (3, 3))))
    ax.text(3.3, -0.55, '把两局都补满，四条路才一样可能', ha='center',
            fontsize=11.5, color=NAVY)
    ax.set_xlim(-0.4, 7.7); ax.set_ylim(-1.0, 3.35)
    ax.axis('off')
    save(fig, 'fig-p00-split.png')


# ---------------------------------------------------------------- p01
def fig_p01():
    """弦是什么、内接正三角形是什么、什么叫"比它长"。"""
    fig, ax = plt.subplots(figsize=(4.6, 4.6))
    ax.add_patch(Circle((0, 0), 1, fill=False, color=NAVY, lw=1.8))
    tri = [(math.cos(math.radians(t)), math.sin(math.radians(t)))
           for t in (90, 210, 330)]
    ax.add_patch(Polygon(tri, closed=True, fill=False, color=GREY, lw=1.6, ls=(0, (5, 3))))
    for p in tri:
        ax.plot([p[0]], [p[1]], 'o', ms=5, color=GREY, zorder=3)
    ax.text(0, -0.72, '三条边一样长', ha='center', fontsize=10, color=GREY)

    long_c = [(math.cos(math.radians(t)), math.sin(math.radians(t))) for t in (150, 20)]
    short_c = [(math.cos(math.radians(t)), math.sin(math.radians(t))) for t in (255, 300)]
    for pts, col, lab, dy in ((long_c, GREEN, '这条比边长', 0.15),
                              (short_c, ORANGE, '这条比边短', -0.17)):
        ax.plot([pts[0][0], pts[1][0]], [pts[0][1], pts[1][1]], color=col, lw=2.6)
        mx, my = (pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2
        ax.text(mx, my + dy, lab, ha='center', fontsize=10.5, color=col)
        for p in pts:
            ax.plot([p[0]], [p[1]], 'o', ms=5, color=col, zorder=3)

    ax.text(0, 1.16, '两头都落在圆上的线段，叫弦', ha='center', fontsize=11, color=NAVY)
    ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.32)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-p01-chord.png')


# ---------------------------------------------------------------- p02
def fig_p02():
    """三种"随便画一条弦"的做法，一格一种。只画怎么做，不画为什么。"""
    fig, axs = plt.subplots(1, 3, figsize=(9.6, 3.9))
    titles = ('一、两个骰子挑两个点', '二、半径上抽一个签', '三、往圆里撒一粒米')

    for ax, t in zip(axs, titles):
        ax.add_patch(Circle((0, 0), 1, fill=False, color=NAVY, lw=1.6))
        ax.text(0, 1.30, t, ha='center', fontsize=11, color=NAVY)
        ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.35, 1.5)
        ax.set_aspect('equal'); ax.axis('off')

    # 一、圆周 36 等分，取两点连线
    ax = axs[0]
    for d in range(36):
        x, y = math.cos(math.radians(d * 10)), math.sin(math.radians(d * 10))
        ax.plot([x], [y], 'o', ms=2.6, color=GREY, zorder=2)
    p, q = 8, 26
    P = (math.cos(math.radians(p * 10)), math.sin(math.radians(p * 10)))
    Q = (math.cos(math.radians(q * 10)), math.sin(math.radians(q * 10)))
    ax.plot([P[0], Q[0]], [P[1], Q[1]], color=GREEN, lw=2.4, zorder=3)
    for X in (P, Q):
        ax.plot([X[0]], [X[1]], 'o', ms=7, color=ORANGE, zorder=4)
    ax.text(0, -1.28, '圆周先点上 36 个点', ha='center', fontsize=9.5, color=GREY)

    # 二、一条半径，十等分，取第 k 格的正中，作垂直弦
    ax = axs[1]
    ang = math.radians(35)
    ux, uy = math.cos(ang), math.sin(ang)
    ax.plot([0, ux], [0, uy], color=NAVY, lw=1.8, zorder=3)
    # 刻度要垂直于半径地画出来，用 '|' 标记会变成一把和半径无关的梳子（08-02 看图抓到）
    for m in range(11):
        s = m / 10
        t = 0.055 if m % 5 else 0.085
        ax.plot([s * ux - t * uy, s * ux + t * uy],
                [s * uy + t * ux, s * uy - t * ux],
                color=NAVY, lw=1.3, zorder=4)
    s = 0.35
    Mx, My = s * ux, s * uy
    half = math.sqrt(max(1 - s * s, 0))
    ax.plot([Mx - half * uy, Mx + half * uy], [My + half * ux, My - half * ux],
            color=GREEN, lw=2.4, zorder=3)
    ax.plot([Mx], [My], 'o', ms=7, color=ORANGE, zorder=4)
    ax.text(0, -1.28, '抽到第几格，中点就放在哪儿', ha='center', fontsize=9.5, color=GREY)

    # 三、撒米粒，取一粒当中点
    ax = axs[2]
    rng = random.Random(11)
    for _ in range(60):
        while True:
            x, y = rng.uniform(-1, 1), rng.uniform(-1, 1)
            if x * x + y * y <= 0.97:
                break
        ax.plot([x], [y], 'o', ms=2.4, color=GREY, zorder=2)
    Mx, My = 0.18, -0.42
    d = math.hypot(Mx, My)
    ux, uy = Mx / d, My / d
    half = math.sqrt(max(1 - d * d, 0))
    ax.plot([Mx - half * uy, Mx + half * uy], [My + half * ux, My - half * ux],
            color=GREEN, lw=2.4, zorder=3)
    ax.plot([Mx], [My], 'o', ms=7, color=ORANGE, zorder=4)
    ax.text(0, -1.28, '哪一粒说了算，就以它为中点', ha='center', fontsize=9.5, color=GREY)

    save(fig, 'fig-p02-three-ways.png')


# ---------------------------------------------------------------- p03
def fig_p03():
    """三种做法数出来的成绩：30 次一组，一万次一组。三个数各自稳住，就是不碰头。"""
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    labs = ('一、两个骰子\n挑两个点', '二、半径上\n抽一个签', '三、往圆里\n撒一粒米')
    f30 = [h / 30 for h in THIRTY]
    f10k = [h / 10000 for h in TEN_K]
    xs = [0, 1, 2]
    w = 0.32
    b1 = ax.bar([x - w / 2 - 0.02 for x in xs], f30, width=w, color=BAND,
                edgecolor=ORANGE, lw=1.4, label='我们做的 30 次')
    b2 = ax.bar([x + w / 2 + 0.02 for x in xs], f10k, width=w, color=LIGHT,
                edgecolor=NAVY, lw=1.4, label='电脑做的一万次')
    for rect, h in zip(b1, THIRTY):
        ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 0.012,
                '%d 次' % h, ha='center', fontsize=9.5, color=ORANGE)
    for rect, v in zip(b2, f10k):
        ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 0.012,
                '%.2f' % v, ha='center', fontsize=9.5, color=NAVY)
    # 参考线画到 2.5 为止，标签从 2.6 起 —— axhline 会一路铺到边框，把标签压在线上
    for y, lab in ((1 / 3, '三分之一'), (1 / 2, '一半'), (1 / 4, '四分之一')):
        ax.plot([-0.5, 2.5], [y, y], color=GREY, lw=1.0, ls=(0, (4, 3)), zorder=0)
        ax.text(2.6, y, lab, va='center', ha='left', fontsize=9.5, color=GREY)
    ax.set_xticks(xs); ax.set_xticklabels(labs, fontsize=10.5, color=NAVY)
    ax.set_yticks([0, 0.25, 1 / 3, 0.5]); ax.set_yticklabels(['0', '', '', ''])
    ax.set_ylim(0, 0.72); ax.set_xlim(-0.55, 3.55)
    ax.text(-0.5, 0.685, '中了的比例', fontsize=10, color=NAVY)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_color(GREY); ax.spines['bottom'].set_color(GREY)
    ax.legend(loc='upper center', ncol=2, frameon=False, fontsize=10,
              bbox_to_anchor=(0.5, 1.14))
    save(fig, 'fig-p03-three-answers.png')



# ================================================================ 正文插图
def _grid(ax, nx, ny, x0=0.0, y0=0.0, w=1.0, h=1.0, color=GREY, lw=1.0):
    for i in range(nx + 1):
        ax.plot([x0 + i * w, x0 + i * w], [y0, y0 + ny * h], color=color, lw=lw)
    for j in range(ny + 1):
        ax.plot([x0, x0 + nx * w], [y0 + j * h, y0 + j * h], color=color, lw=lw)


# ---------------------------------------------------------------- p04
def fig_p04():
    """你早就会算的三样：转盘（角度）、飞镖靶（面积）、地板砖（份数）。"""
    from matplotlib.patches import Wedge, Rectangle
    fig, axs = plt.subplots(1, 3, figsize=(9.6, 3.6))

    ax = axs[0]
    for k in range(6):
        ax.add_patch(Wedge((0, 0), 1, k * 60, (k + 1) * 60,
                           facecolor=BAND if k < 3 else 'white',
                           edgecolor=NAVY, lw=1.3))
    ax.text(0, -1.42, '六格里三格红', ha='center', fontsize=10.5, color=NAVY)
    ax.text(0, 1.22, '转盘：比角度', ha='center', fontsize=11, color=NAVY)
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.6, 1.45)

    ax = axs[1]
    ax.add_patch(Circle((0, 0), 1, facecolor='white', edgecolor=NAVY, lw=1.5))
    ax.add_patch(Circle((0, 0), 0.5, facecolor=BAND, edgecolor=ORANGE, lw=1.5))
    ax.annotate('', xy=(0.5, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='<->', color=ORANGE, lw=1.2))
    ax.text(0.25, 0.09, '一半', ha='center', fontsize=9.5, color=ORANGE)
    ax.text(0, -1.42, '小圆面积是四分之一', ha='center', fontsize=10.5, color=NAVY)
    ax.text(0, 1.22, '飞镖靶：比面积', ha='center', fontsize=11, color=NAVY)
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.6, 1.45)

    ax = axs[2]
    flower = {(1, 1), (3, 2), (6, 0), (8, 4), (2, 6), (5, 7), (9, 8), (0, 9), (7, 5)}
    for i in range(10):
        for j in range(10):
            ax.add_patch(Rectangle((i, j), 1, 1,
                                   facecolor=BAND if (i, j) in flower else 'white',
                                   edgecolor=GREY, lw=0.6))
    ax.text(5, -1.5, '一百块里九块花砖', ha='center', fontsize=10.5, color=NAVY)
    ax.text(5, 11.0, '地板砖：比份数', ha='center', fontsize=11, color=NAVY)
    ax.set_xlim(-1.2, 11.2); ax.set_ylim(-2.6, 11.9)

    for ax in axs:
        ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-p04-what-you-know.png')


# ---------------------------------------------------------------- p05
def fig_p05():
    """两枚硬币：四格，不是三项。"""
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(5.2, 4.0))
    cells = [(0, 1, '正 正'), (1, 1, '正 反'), (0, 0, '反 正'), (1, 0, '反 反')]
    for i, j, lab in cells:
        mid = lab in ('正 反', '反 正')
        ax.add_patch(Rectangle((i, j), 1, 1, facecolor=BAND if mid else 'white',
                               edgecolor=NAVY, lw=1.4))
        ax.text(i + 0.5, j + 0.52, lab, ha='center', va='center',
                fontsize=13, color=NAVY)
    ax.text(-0.12, 1.5, '一角\n正', ha='right', va='center', fontsize=10,
            color=GREY, linespacing=1.5)
    ax.text(-0.12, 0.5, '一角\n反', ha='right', va='center', fontsize=10,
            color=GREY, linespacing=1.5)
    ax.text(0.5, 2.1, '五角正', ha='center', fontsize=10, color=GREY)
    ax.text(1.5, 2.1, '五角反', ha='center', fontsize=10, color=GREY)
    ax.text(1.0, -0.42, '涂色的两格，合起来才是"一正一反"',
            ha='center', fontsize=10.5, color=ORANGE)
    ax.set_xlim(-1.15, 2.2); ax.set_ylim(-0.85, 2.45)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-p05-two-coins.png')


# ---------------------------------------------------------------- p06
def fig_p06():
    """一件事＝在结果单上挑出几项。左边两件事不重叠，右边重叠了。

    别用一个椭圆去"圈住"不连续的几项（偶数是 2、4、6，一椭圆下去把 3、5 也
    圈进来了，08-02 看图抓到）——逐项画标记才不会说谎。
    """
    from matplotlib.patches import Rectangle
    fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.2))
    plans = ((axs[0], (5, 6), (1,), '不重叠：可以直接相加', '大于 4', '等于 1', ()),
             (axs[1], (2, 4, 6), (4, 5, 6), '重叠了：4 和 6 被数了两遍',
              '是偶数', '大于 3', (4, 6)))
    for ax, ga, gb, title, la, lb, dup in plans:
        for k in range(1, 7):
            ax.text(k, 0, str(k), ha='center', va='center', fontsize=15, color=NAVY)
        for k in ga:
            ax.add_patch(Rectangle((k - 0.32, -0.62), 0.64, 0.16,
                                   facecolor=GREEN, edgecolor='none'))
        for k in gb:
            ax.add_patch(Rectangle((k - 0.32, 0.46), 0.64, 0.16,
                                   facecolor=ORANGE, edgecolor='none'))
        ax.text(0.35, -0.54, la, ha='right', va='center', fontsize=10.5, color=GREEN)
        ax.text(0.35, 0.54, lb, ha='right', va='center', fontsize=10.5, color=ORANGE)
        for k in dup:
            ax.plot([k], [0], 'o', ms=30, mfc='none', mec=RED, mew=1.8)
        ax.text(3.2, -1.25, title, ha='center', fontsize=11,
                color=RED if dup else NAVY)
        ax.set_xlim(-2.2, 6.9); ax.set_ylim(-1.55, 1.0)
        ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-p06-events.png')


# ---------------------------------------------------------------- p07
def fig_p07():
    """两个骰子的 36 格，按和分堆——每堆格数根本不一样。"""
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(5.8, 5.4))
    for r in range(6):
        for b in range(6):
            s = r + b + 2
            shade = BAND if s == 7 else (LIGHT if s == 2 else 'white')
            ax.add_patch(Rectangle((b, 5 - r), 1, 1, facecolor=shade,
                                   edgecolor=GREY, lw=0.8))
            ax.text(b + 0.5, 5 - r + 0.5, str(s), ha='center', va='center',
                    fontsize=11, color=NAVY)
    for k in range(6):
        ax.text(k + 0.5, 6.18, str(k + 1), ha='center', fontsize=11, color=GREY)
        ax.text(-0.22, 5 - k + 0.5, str(k + 1), ha='right', va='center',
                fontsize=11, color=GREY)
    ax.text(3, 6.72, '蓝骰子', ha='center', fontsize=11, color=GREY)
    ax.text(-1.05, 3, '红\n骰\n子', ha='center', va='center', fontsize=11,
            color=GREY, linespacing=1.4)
    ax.text(3, -0.55, '和是 7 有 6 格，和是 2 只有 1 格',
            ha='center', fontsize=11, color=ORANGE)
    ax.set_xlim(-1.5, 6.4); ax.set_ylim(-1.0, 7.1)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-p07-two-dice.png')


# ---------------------------------------------------------------- p08
def fig_p08():
    """一枚硬币配一个骰子：2 乘 6 ＝ 12 格。"""
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(6.6, 2.9))
    for j, coin in enumerate(('反', '正')):
        for i in range(6):
            hit = (coin == '正' and i == 5)
            ax.add_patch(Rectangle((i, j), 1, 1, facecolor=BAND if hit else 'white',
                                   edgecolor=NAVY, lw=1.1))
            ax.text(i + 0.5, j + 0.5, '%s %d' % (coin, i + 1), ha='center',
                    va='center', fontsize=10.5, color=NAVY)
    ax.text(5.5, 2.32, '正面而且 6', ha='center', fontsize=10.5, color=ORANGE)
    ax.plot([5.5, 5.5], [2.16, 2.02], color=ORANGE, lw=1.2)
    ax.text(3, -0.55, '一共 2 乘 6 ＝ 12 格，要的那一格只占 1 格',
            ha='center', fontsize=11, color=NAVY)
    ax.set_xlim(-0.3, 6.3); ax.set_ylim(-0.95, 2.7)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-p08-coin-die.png')


# ---------------------------------------------------------------- p09
def fig_p09():
    """三扇门：三种情形各占三分之一，换在两种情形里赢。"""
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    rows = ((2, 0, '车在 1 号（你选中了）', '不换赢', True),
            (1, 1, '车在 2 号', '换赢', False),
            (0, 2, '车在 3 号', '换赢', False))
    for y, carpos, lab, res, stay in rows:
        yy = y * 1.35
        for d in range(3):
            car = (d == carpos)
            face = BAND if car else 'white'
            ax.add_patch(Rectangle((d * 1.15, yy), 0.95, 1.0, facecolor=face,
                                   edgecolor=NAVY, lw=1.3))
            ax.text(d * 1.15 + 0.475, yy + 0.5, '车' if car else '羊',
                    ha='center', va='center', fontsize=12, color=NAVY)
            ax.text(d * 1.15 + 0.475, yy - 0.22, '%d 号' % (d + 1),
                    ha='center', fontsize=9, color=GREY)
        ax.text(3.75, yy + 0.5, lab, va='center', fontsize=10.5, color=NAVY)
        ax.text(8.15, yy + 0.5, res, va='center', fontsize=11,
                color=GREY if stay else GREEN)
        ax.text(-0.45, yy + 0.5, '三分之一', va='center', ha='right',
                fontsize=10, color=GREY)
    ax.text(-0.45, 4.62, '各占', ha='right', fontsize=10, color=GREY)
    ax.text(8.15, 4.62, '结果', fontsize=10.5, color=GREY)
    ax.text(4.0, -0.75, '你先选 1 号。不换只在第一行赢，换在下面两行都赢',
            ha='center', fontsize=11, color=NAVY)
    ax.set_xlim(-1.6, 9.7); ax.set_ylim(-1.2, 5.1)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-p09-three-doors.png')


# ---------------------------------------------------------------- p10
def fig_p10():
    """公平价＝把六根柱子削平以后的高度。"""
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    xs = list(range(1, 7))
    ax.bar(xs, xs, width=0.62, color=LIGHT, edgecolor=NAVY, lw=1.3)
    ax.plot([0.4, 6.6], [3.5, 3.5], color=ORANGE, lw=2.0, ls=(0, (5, 3)))
    ax.text(6.75, 3.5, '公平价\n3.5', va='center', fontsize=10.5, color=ORANGE,
            linespacing=1.5)
    for k in xs:
        ax.text(k, k + 0.16, str(k), ha='center', fontsize=10, color=NAVY)
    ax.text(3.5, -1.15, '掷出几拿几块：把六根柱子削平，就是 3.5',
            ha='center', fontsize=11, color=NAVY)
    ax.set_xticks(xs); ax.set_xticklabels([str(k) for k in xs], fontsize=10.5,
                                          color=NAVY)
    ax.set_yticks([]); ax.set_xlim(0.3, 8.2); ax.set_ylim(0, 7.2)
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color(GREY)
    save(fig, 'fig-p10-fair-price.png')


# ---------------------------------------------------------------- p11
def fig_p11():
    """抛硬币十万次，正面比例慢慢挤向一半。"""
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    ax.plot(COIN_STEPS, COIN_FREQ, color=NAVY, lw=1.3)
    ax.axhline(0.5, color=ORANGE, lw=1.6, ls=(0, (5, 3)))
    ax.text(1.35e5, 0.5, '一半', va='center', fontsize=10.5, color=ORANGE)
    ax.set_xscale('log')
    ax.set_xlim(8, 2.4e5); ax.set_ylim(0.28, 0.78)
    ax.set_yticks([0.3, 0.4, 0.5, 0.6, 0.7])
    ax.set_xticks([10, 100, 1000, 10000, 100000])
    ax.set_xticklabels(['10', '100', '1000', '一万', '十万'], fontsize=10.5,
                       color=NAVY)
    ax.tick_params(axis='y', labelsize=9.5, colors=GREY)
    ax.text(9, 0.80, '正面的比例', fontsize=10.5, color=NAVY)
    ax.text(3000, 0.176, '抛了多少次（每一格是十倍）', ha='center',
            fontsize=10.5, color=NAVY)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_color(GREY); ax.spines['bottom'].set_color(GREY)
    save(fig, 'fig-p11-frequency.png')


# ---------------------------------------------------------------- p12
def fig_p12():
    """36 格按红骰子分成六堆：每堆先平均，再平均，和一口气平均一样。"""
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    for r in range(6):
        for b in range(6):
            ax.add_patch(Rectangle((b, 5 - r), 1, 1,
                                   facecolor=LIGHT if r % 2 == 0 else 'white',
                                   edgecolor=GREY, lw=0.7))
            ax.text(b + 0.5, 5 - r + 0.5, str(r + b + 2), ha='center',
                    va='center', fontsize=10, color=NAVY)
        ax.text(6.45, 5 - r + 0.5, '%.1f' % (r + 1 + 3.5), va='center',
                fontsize=11, color=ORANGE)
    ax.text(6.9, 6.28, '这一堆的\n公平价', ha='center', fontsize=10,
            color=ORANGE, linespacing=1.5)
    ax.annotate('', xy=(7.6, 2.6), xytext=(7.6, 3.6),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=1.6))
    ax.text(8.35, 3.1, '六个数\n再平均\n＝ 7', ha='center', va='center',
            fontsize=10.5, color=GREEN, linespacing=1.5)
    ax.text(3, -0.62, '一口气把 36 个数平均，也是 7 —— 同一批数，换个顺序加',
            ha='center', fontsize=11, color=NAVY)
    ax.set_xlim(-0.4, 9.4); ax.set_ylim(-1.1, 7.1)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-p12-tower.png')


# ---------------------------------------------------------------- p13
def fig_p13():
    """三种做法各自的"中了"区域：一段弧、半条半径、一个小圆。"""
    from matplotlib.patches import Wedge
    fig, axs = plt.subplots(1, 3, figsize=(9.6, 3.9))
    for ax in axs:
        ax.set_xlim(-1.32, 1.32); ax.set_ylim(-1.55, 1.45)
        ax.set_aspect('equal'); ax.axis('off')

    ax = axs[0]
    ax.add_patch(Circle((0, 0), 1, fill=False, color=NAVY, lw=1.6))
    A = (math.cos(math.radians(90)), math.sin(math.radians(90)))
    tri = [(math.cos(math.radians(t)), math.sin(math.radians(t)))
           for t in (90, 210, 330)]
    ax.add_patch(Polygon(tri, closed=True, fill=False, color=GREY, lw=1.2,
                         ls=(0, (4, 3))))
    arc = [(math.cos(math.radians(t)), math.sin(math.radians(t)))
           for t in range(210, 331)]
    ax.plot([p[0] for p in arc], [p[1] for p in arc], color=GREEN, lw=4.5,
            solid_capstyle='butt')
    ax.plot([A[0]], [A[1]], 'o', ms=8, color=ORANGE, zorder=4)
    ax.text(-0.78, 1.02, '钉住这一头', ha='center', fontsize=9.5, color=ORANGE)
    ax.text(0, 1.24, '端点法：比弧长', ha='center', fontsize=11, color=NAVY)
    ax.text(0, -1.42, '另一头落在绿弧上才够长　三段之一', ha='center',
            fontsize=9.5, color=GREEN)

    ax = axs[1]
    ax.add_patch(Circle((0, 0), 1, fill=False, color=NAVY, lw=1.6))
    ang = math.radians(35)
    ux, uy = math.cos(ang), math.sin(ang)
    ax.plot([0, ux], [0, uy], color=GREY, lw=1.4)
    ax.plot([0, 0.5 * ux], [0, 0.5 * uy], color=GREEN, lw=4.5,
            solid_capstyle='butt')
    ax.plot([0.5 * ux], [0.5 * uy], 'o', ms=6, color=ORANGE, zorder=4)
    ax.text(0, 1.24, '半径法：比长度', ha='center', fontsize=11, color=NAVY)
    ax.text(0, -1.42, '中点落在靠里的半段才够长　一半', ha='center',
            fontsize=9.5, color=GREEN)

    ax = axs[2]
    ax.add_patch(Circle((0, 0), 1, fill=False, color=NAVY, lw=1.6))
    ax.add_patch(Circle((0, 0), 0.5, facecolor=BAND, edgecolor=GREEN, lw=1.8))
    ax.text(0, 1.24, '撒米法：比面积', ha='center', fontsize=11, color=NAVY)
    ax.text(0, -1.42, '中点落在小圆里才够长　四分之一', ha='center',
            fontsize=9.5, color=GREEN)

    save(fig, 'fig-p13-three-answers.png')

# ================================================================ 尾声
def double_bet_run(rounds, seed):
    """翻倍下注，口袋 7 块（最多押 1、2、4 三把）：赢一把收手赚 1，三连输赔 7。

    返回每回合结束后的累计净赚（开头补一个 0），和赔光的回合数。
    """
    rng = random.Random(seed)
    net, path, crashes = 0, [0], 0
    for _ in range(rounds):
        won = False
        for _bet in (1, 2, 4):
            if rng.random() < 0.5:
                won = True
                break
        if won:
            net += 1
        else:
            net -= 7
            crashes += 1
        path.append(net)
    return path, crashes


DBL_PATH, DBL_CRASHES = double_bet_run(200, 8)   # 种子定在 8，没有挑：跑出净赔就印净赔
# 尾声正文印着这四个数：171 回赚 1、29 回赔 7、最后净赔 32、路上最高赚到 40
assert DBL_CRASHES == 29, DBL_CRASHES
assert DBL_PATH[-1] == -32, DBL_PATH[-1]
assert (min(DBL_PATH), max(DBL_PATH)) == (-44, 40), (min(DBL_PATH), max(DBL_PATH))


def match_value(a, b):
    """分金：比分 a 比 b（先到 3 分、每局各半、赌注 64）时这个局面值多少。"""
    if a >= 3:
        return 64
    if b >= 3:
        return 0
    return (match_value(a + 1, b) + match_value(a, b + 1)) / 2


# 尾声那张树印着这些价：0比0=32、1比0=44、0比1=20、1比1=32、2比0=56、2比1=48、1比2=16
assert [match_value(*s) for s in
        ((0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (2, 1), (1, 2))] == \
       [32, 44, 20, 32, 56, 48, 16]


# ---------------------------------------------------------------- p14
def fig_p14():
    """造点的机器：正面留左半、反面留右半，剩下的段一半一半地短下去。"""
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    segs = ((0.0, 1.0, '开始', '1 米'),
            (0.0, 0.5, '第一次：正——留左半', '50 厘米'),
            (0.25, 0.5, '第二次：反——留右半', '25 厘米'),
            (0.25, 0.375, '第三次：正——留左半', '12.5 厘米'),
            (0.3125, 0.375, '第四次：反——留右半', '6.25 厘米'))
    for k, (a, b, lab, ln) in enumerate(segs):
        y = 4.4 - k
        ax.plot([0, 1], [y, y], color=GREY, lw=1.2, ls=(0, (2, 3)))
        ax.plot([a, b], [y, y], color=GREEN if k else NAVY, lw=5.0,
                solid_capstyle='butt')
        for e in (a, b):
            ax.plot([e, e], [y - 0.09, y + 0.09],
                    color=GREEN if k else NAVY, lw=1.6)
        ax.text(-0.04, y, lab, ha='right', va='center', fontsize=10.5,
                color=NAVY if k == 0 else GREEN)
        ax.text(1.04, y, ln, ha='left', va='center', fontsize=10, color=GREY)
    ax.text(-0.04, -0.6, '……一直抛下去', ha='right', va='center',
            fontsize=10.5, color=GREY)
    ax.plot([1 / 3], [-0.6], 'o', ms=8, color=ORANGE, zorder=4)
    ax.annotate('最后只剩一个点', xy=(1 / 3, -0.6), xytext=(0.62, -0.6),
                ha='left', va='center', fontsize=10.5, color=ORANGE,
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=1.2))
    ax.text(0.5, -1.45, '剩下的段：要多短有多短 —— 零件全是互不影响的硬币',
            ha='center', fontsize=11, color=NAVY)
    ax.set_xlim(-1.45, 1.55); ax.set_ylim(-1.8, 4.9)
    ax.axis('off')
    save(fig, 'fig-p14-rope-halving.png')


# ---------------------------------------------------------------- p15
def fig_p15():
    """翻倍下注 200 回合的账：缓坡一块一块赚，悬崖一把赔 7。"""
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.plot(range(len(DBL_PATH)), DBL_PATH, color=NAVY, lw=1.5)
    ax.axhline(0, color=ORANGE, lw=1.4, ls=(0, (5, 3)))
    top = max(DBL_PATH)
    k_top = DBL_PATH.index(top)
    ax.plot([k_top], [top], 'o', ms=6, color=GREEN, zorder=4)
    ax.annotate('一度赚到 40', xy=(k_top, top), xytext=(k_top - 52, top + 9),
                fontsize=10, color=GREEN,
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=1.1))
    ax.plot([200], [DBL_PATH[-1]], 'o', ms=6, color=RED, zorder=4)
    ax.annotate('200 回合后：赔 32', xy=(200, DBL_PATH[-1]),
                xytext=(132, DBL_PATH[-1] - 13), fontsize=10, color=RED,
                arrowprops=dict(arrowstyle='-|>', color=RED, lw=1.1))
    ax.set_yticks([-40, -20, 0, 20, 40])
    ax.set_yticklabels(['赔 40', '赔 20', '0', '赚 20', '赚 40'],
                       fontsize=9.5, color=GREY)
    ax.set_xticks([0, 50, 100, 150, 200])
    ax.tick_params(axis='x', labelsize=9.5, colors=GREY)
    ax.text(4, 46, '口袋里的总账', fontsize=10.5, color=NAVY)
    ax.text(100, -66, '玩了多少回合', ha='center', fontsize=10.5, color=NAVY)
    ax.set_xlim(0, 232); ax.set_ylim(-56, 54)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_color(GREY); ax.spines['bottom'].set_color(GREY)
    save(fig, 'fig-p15-double-bet.png')


# ---------------------------------------------------------------- p16
def fig_p16():
    """分金价钱的树：每个局面的价 ＝ 下一局两种明天的平均。"""
    from matplotlib.patches import Rectangle

    fig, ax = plt.subplots(figsize=(8.0, 4.6))

    def node(cx, cy, score, val, on_path):
        w, h = 1.24, 0.86
        ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h,
                               facecolor=LIGHT if on_path else 'white',
                               edgecolor=NAVY if on_path else GREY,
                               lw=1.5 if on_path else 1.1))
        col = NAVY if on_path else GREY
        ax.text(cx, cy + 0.17, score, ha='center', va='center',
                fontsize=11 if on_path else 10, color=col)
        ax.text(cx, cy - 0.21, '值 %d' % val, ha='center', va='center',
                fontsize=10 if on_path else 9.5, color=ORANGE if on_path else GREY)

    def arrow(x0, y0, x1, y1, mark, strong):
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='-|>',
                                    color=NAVY if strong else GREY,
                                    lw=1.5 if strong else 1.0))
        ax.text((x0 + x1) / 2 - 0.1, (y0 + y1) / 2 + 0.18, mark,
                ha='center', fontsize=10, color=ORANGE if strong else GREY)

    P = ((0.0, 1.6), (1.9, 2.6), (3.8, 1.6), (5.7, 2.6))       # 路径上的四个局面
    node(*P[0], '0 比 0', 32, True)
    node(*P[1], '1 比 0', 44, True)
    node(*P[2], '1 比 1', 32, True)
    node(*P[3], '2 比 1', 48, True)
    node(1.9, 0.5, '0 比 1', 20, False)
    node(3.8, 3.7, '2 比 0', 56, False)
    node(5.7, 0.5, '1 比 2', 16, False)
    node(7.6, 3.7, '姐姐 3 分', 64, False)
    node(7.6, 1.6, '2 比 2', 32, False)

    arrow(0.66, 1.85, 1.24, 2.42, '正', True)
    arrow(0.66, 1.35, 1.24, 0.72, '反', False)
    arrow(2.56, 2.85, 3.14, 3.48, '正', False)
    arrow(2.56, 2.35, 3.14, 1.82, '反', True)
    arrow(4.46, 1.85, 5.04, 2.42, '正', True)
    arrow(4.46, 1.35, 5.04, 0.72, '反', False)
    arrow(6.36, 2.85, 6.94, 3.48, '正', False)
    arrow(6.36, 2.35, 6.94, 1.82, '反', False)

    ax.annotate('妈妈在这儿喊停\n按 48 分钱', xy=(5.7, 3.05), xytext=(4.55, 4.35),
                ha='center', fontsize=9.5, color=RED, linespacing=1.5,
                arrowprops=dict(arrowstyle='-|>', color=RED, lw=1.0,
                                ls=(0, (3, 3))))
    ax.text(3.8, -0.55, '每个价都是两种明天的平均：56 和 32 平均是 44，48 和 16 平均是 32，64 和 32 平均是 48',
            ha='center', fontsize=10.5, color=NAVY)
    ax.set_xlim(-0.85, 8.55); ax.set_ylim(-1.0, 5.0)
    ax.axis('off')
    save(fig, 'fig-p16-split-fair.png')


if __name__ == '__main__':
    print('generating figures ->', OUT)
    print('  30 次：', THIRTY, ' 一万次：', TEN_K, ' 分金重打 40 遍：', SPLIT40)
    print('  翻倍下注 200 回合：赔光', DBL_CRASHES, '回，净', DBL_PATH[-1])
    for f in (fig_p00, fig_p01, fig_p02, fig_p03, fig_p04, fig_p05, fig_p06,
              fig_p07, fig_p08, fig_p09, fig_p10, fig_p11, fig_p12, fig_p13,
              fig_p14, fig_p15, fig_p16):
        f()
    print('done:', len(os.listdir(OUT)), 'files')
