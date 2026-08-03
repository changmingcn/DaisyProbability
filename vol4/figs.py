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


if __name__ == '__main__':
    print('generating figures ->', OUT)
    print('  30 次：', THIRTY, ' 一万次：', TEN_K)
    for f in (fig_p01, fig_p02, fig_p03):
        f()
    print('done:', len(os.listdir(OUT)), 'files')
