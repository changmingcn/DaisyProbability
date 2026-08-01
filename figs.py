#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成《不能做完无穷，怎么谈论无穷》全部插图。

约定：中文标签用 Hiragino Sans GB；数学符号一律走 mathtext（DejaVu），
两者绝不混在同一个字符串里 —— Hiragino 缺下标/上标/分数字形。
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch, Arc, Wedge, Polygon, FancyArrowPatch

plt.rcParams['font.sans-serif'] = ['Hiragino Sans GB', 'Arial Unicode MS', 'Songti SC']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'dejavusans'

NAVY   = '#1F3A6E'
ORANGE = '#E8743B'
GREEN  = '#2E9E6B'
GREY   = '#9AA5B1'
LIGHT  = '#DCE7F7'
BAND   = '#FBE3D6'
RED    = '#C0392B'

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
os.makedirs(OUT, exist_ok=True)


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  wrote', name)


def numberline(ax, lo, hi, y=0.0, ticks=None, ticklabels=None, lw=1.6):
    ax.annotate('', xy=(hi, y), xytext=(lo, y),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=lw))
    if ticks:
        for i, t in enumerate(ticks):
            ax.plot([t, t], [y - 0.045, y + 0.045], color=NAVY, lw=lw)
            lab = ticklabels[i] if ticklabels else None
            if lab:
                ax.text(t, y - 0.13, lab, ha='center', va='top', fontsize=11, color=NAVY)


# ---------------------------------------------------------------- 01
def fig01():
    """部分和在数轴上向 2 逼近：每一步只走掉剩下距离的一半。"""
    fig, ax = plt.subplots(figsize=(6.4, 1.75))
    vals = [1, 1.5, 1.75, 1.875, 1.9375, 1.96875, 1.984375]
    numberline(ax, 0.86, 2.22, ticks=[1, 2], ticklabels=['1', '2'])
    for i, v in enumerate(vals):
        ax.plot([v], [0], 'o', ms=7, color=ORANGE, zorder=3)
        if i < 4:
            ax.annotate('', xy=(v, 0.30), xytext=(vals[i - 1] if i else 1, 0.30),
                        arrowprops=dict(arrowstyle='-|>', color=GREY, lw=1.2,
                                        connectionstyle='arc3,rad=-0.45'))
    ax.plot([2], [0], 'o', ms=9, mfc='white', mec=NAVY, mew=2, zorder=4)
    ax.text(2, 0.20, '永远走不到', ha='center', fontsize=10.5, color=NAVY)
    ax.text(1.0, -0.34, '第 1 个', ha='center', fontsize=9.5, color=ORANGE)
    ax.text(1.5, -0.34, '第 2 个', ha='center', fontsize=9.5, color=ORANGE)
    ax.text(1.75, -0.34, '第 3 个', ha='center', fontsize=9.5, color=ORANGE)
    ax.text(1.98, -0.34, '越挤越密', ha='center', fontsize=9.5, color=ORANGE)
    ax.set_xlim(0.82, 2.30); ax.set_ylim(-0.52, 0.48); ax.axis('off')
    save(fig, 'fig-01-partial-sums.png')


# ---------------------------------------------------------------- 02
def fig02():
    """下标就是门牌号。"""
    fig, ax = plt.subplots(figsize=(6.4, 1.55))
    labels = [r'$a_1$', r'$a_2$', r'$a_3$', r'$a_4$', r'$a_5$', r'$\cdots$', r'$a_n$']
    vals = ['1', '1.5', '1.75', '1.875', '1.9375', '', '?']
    for i in range(7):
        x = i * 0.86
        ax.add_patch(FancyBboxPatch((x, 0), 0.74, 0.62,
                                    boxstyle='round,pad=0.02,rounding_size=0.07',
                                    fc=LIGHT if i != 6 else BAND,
                                    ec=NAVY if i != 6 else ORANGE, lw=1.4))
        ax.text(x + 0.37, 0.31, vals[i], ha='center', va='center',
                fontsize=10.5, color=NAVY)
        ax.text(x + 0.37, -0.20, labels[i], ha='center', va='center',
                fontsize=13, color=NAVY if i != 6 else ORANGE)
    ax.text(3.0, 0.92, '每个数发一个门牌号，写在右下角', ha='center',
            fontsize=11, color=NAVY)
    ax.set_xlim(-0.2, 6.2); ax.set_ylim(-0.48, 1.15); ax.axis('off')
    save(fig, 'fig-02-subscript.png')


# ---------------------------------------------------------------- 03
def fig03():
    """绝对值 = 数轴上两点的距离。"""
    fig, ax = plt.subplots(figsize=(6.4, 1.7))
    numberline(ax, -0.2, 3.4, ticks=[0.6, 2.6], ticklabels=['', ''])
    ax.plot([0.6], [0], 'o', ms=8, color=ORANGE, zorder=3)
    ax.plot([2.6], [0], 'o', ms=8, color=GREEN, zorder=3)
    ax.text(0.6, -0.16, r'$a_n$', ha='center', va='top', fontsize=13, color=ORANGE)
    ax.text(2.6, -0.16, r'$L$', ha='center', va='top', fontsize=13, color=GREEN)
    ax.annotate('', xy=(2.6, 0.34), xytext=(0.6, 0.34),
                arrowprops=dict(arrowstyle='<|-|>', color=NAVY, lw=1.6))
    ax.text(1.6, 0.44, '这一段的长度', ha='center', fontsize=11, color=NAVY)
    ax.text(1.6, 0.80, r'$|\,a_n - L\,|$', ha='center', fontsize=15, color=NAVY)
    ax.text(1.6, -0.72, '读作「第 n 个数 离 L 有多远」——两根竖线只是「距离」的缩写',
            ha='center', fontsize=10, color=GREY)
    ax.set_xlim(-0.3, 3.5); ax.set_ylim(-0.92, 1.05); ax.axis('off')
    save(fig, 'fig-03-absolute-value.png')


# ---------------------------------------------------------------- 04
def fig04():
    """ε–N：妹妹画误差带，姐姐给出关口 N。"""
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    n = np.arange(1, 22)
    a = 2 - 1.0 / 2 ** (n - 1)
    L, eps = 2.0, 0.12
    inside = a > L - eps
    N = int(n[inside][0]) - 1          # 关口＝最后一个还在带外的号码
    ax.axhspan(L - eps, L + eps, color=BAND, zorder=0)
    ax.axhline(L, color=GREEN, lw=1.6, zorder=1)
    ax.axhline(L + eps, color=ORANGE, lw=1.1, ls='--', zorder=1)
    ax.axhline(L - eps, color=ORANGE, lw=1.1, ls='--', zorder=1)
    ax.plot(n[~inside], a[~inside], 'o', ms=6.5, color=GREY, zorder=3)
    ax.plot(n[inside], a[inside], 'o', ms=6.5, color=NAVY, zorder=3)
    ax.axvline(N + 0.5, color=NAVY, lw=1.2, ls=':', zorder=2)
    ax.text(N + 0.75, 1.18, '关口', fontsize=11, color=NAVY, va='bottom')
    ax.text(N + 0.75, 1.02, r'$N=%d$' % N, fontsize=13, color=NAVY, va='bottom')
    bb = dict(fc='white', ec='none', pad=0.15)
    ax.text(21.6, L, r'$L$', fontsize=13, color=GREEN, va='center', bbox=bb)
    ax.text(21.6, L + eps, r'$L+\varepsilon$', fontsize=11, color=ORANGE, va='center', bbox=bb)
    ax.text(21.6, L - eps, r'$L-\varepsilon$', fontsize=11, color=ORANGE, va='center', bbox=bb)
    ax.text(13, 1.72, '过了关口，一个都不许再跑出去', fontsize=11.5, color=NAVY, ha='center')
    ax.annotate('', xy=(12, 1.90), xytext=(13, 1.78),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.2))
    ax.set_xlim(0, 24.5); ax.set_ylim(0.85, 2.22)
    ax.set_xlabel('第几个数', fontsize=11, color=NAVY)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9, colors=NAVY)
    save(fig, 'fig-04-epsilon-N.png')


# ---------------------------------------------------------------- 05
def fig05():
    """ε–δ：自动售货机。"""
    fig, ax = plt.subplots(figsize=(6.4, 2.5))
    ax.add_patch(FancyBboxPatch((2.1, 0.55), 1.8, 1.1,
                                boxstyle='round,pad=0.04,rounding_size=0.12',
                                fc=LIGHT, ec=NAVY, lw=1.8))
    ax.text(3.0, 1.28, '机器', ha='center', fontsize=12, color=NAVY)
    ax.text(3.0, 0.92, r'$f$', ha='center', fontsize=17, color=NAVY)
    ax.annotate('', xy=(2.05, 1.1), xytext=(0.75, 1.1),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2))
    ax.annotate('', xy=(5.3, 1.1), xytext=(3.95, 1.1),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2))
    ax.text(1.4, 1.55, '投进去的', ha='center', fontsize=11, color=ORANGE)
    ax.text(1.4, 0.62, r'$a$', ha='center', fontsize=14, color=ORANGE)
    ax.text(4.62, 1.55, '掉出来的', ha='center', fontsize=11, color=GREEN)
    ax.text(4.62, 0.62, r'$f(a)$', ha='center', fontsize=14, color=GREEN)
    ax.text(1.4, 0.16, '离 c 不超过', ha='center', fontsize=10.5, color=GREY)
    ax.text(1.4, -0.16, r'$\delta$', ha='center', fontsize=15, color=ORANGE)
    ax.text(4.62, 0.16, '离 L 不超过', ha='center', fontsize=10.5, color=GREY)
    ax.text(4.62, -0.16, r'$\varepsilon$', ha='center', fontsize=15, color=GREEN)
    ax.text(3.0, -0.42, '妹妹先定「掉出来要多准」，姐姐再回答「投进去要多准」',
            ha='center', fontsize=10.5, color=NAVY)
    ax.set_xlim(0.3, 5.75); ax.set_ylim(-0.62, 1.85); ax.axis('off')
    save(fig, 'fig-05-epsilon-delta.png')


# ---------------------------------------------------------------- 06
def fig06():
    """柯西条件：关口以后，随便挑两项都很近。"""
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    n = np.arange(1, 22)
    a = 2 - 1.0 / 2 ** (n - 1)
    N = 7
    ax.axvspan(N + 0.5, 22, color=BAND, zorder=0)
    ax.plot(n, a, 'o', ms=6.5, color=NAVY, zorder=3)
    ax.axvline(N + 0.5, color=NAVY, lw=1.2, ls=':', zorder=2)
    ax.text(N + 0.8, 1.02, '关口', fontsize=11, color=NAVY)
    ax.text(N + 0.8, 0.90, r'$N$', fontsize=13, color=NAVY)
    i, j = 10, 17
    ax.annotate('', xy=(j, a[j - 1]), xytext=(i, a[i - 1]),
                arrowprops=dict(arrowstyle='<|-|>', color=ORANGE, lw=1.8,
                                connectionstyle='arc3,rad=0.55'))
    ax.text(13.5, 1.60, '随便挑两项', fontsize=11, color=ORANGE, ha='center')
    ax.text(13.5, 1.44, '它们的距离也小于', fontsize=11, color=ORANGE, ha='center')
    ax.text(13.5, 1.26, r'$\varepsilon$', fontsize=15, color=ORANGE, ha='center')
    ax.text(4, 1.30, '关口以前\n随它去', fontsize=11, color=GREY, ha='center')
    ax.set_xlim(0, 22); ax.set_ylim(0.80, 2.15)
    ax.set_xlabel('第几个数', fontsize=11, color=NAVY)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9, colors=NAVY)
    save(fig, 'fig-06-cauchy.png')


# ---------------------------------------------------------------- 07
def fig07():
    """聚点：不论走到第几项，后面还有项落进圈里。"""
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    rng = np.random.RandomState(7)
    n = np.arange(1, 31)
    a = np.where(n % 3 == 0, 1.5 + 0.5 / n, 0.6 + 1.5 * rng.rand(30))
    p, eps = 1.5, 0.13
    ax.axhspan(p - eps, p + eps, color=BAND, zorder=0)
    ax.axhline(p, color=GREEN, lw=1.5)
    inb = np.abs(a - p) < eps
    ax.plot(n[~inb], a[~inb], 'o', ms=6, color=GREY, zorder=3)
    ax.plot(n[inb], a[inb], 'o', ms=7.5, color=ORANGE, zorder=4)
    for N in (8, 18, 26):
        ax.axvline(N + 0.5, color=NAVY, lw=1.0, ls=':')
        ax.text(N + 0.7, 0.42, '走到这', fontsize=9, color=NAVY, rotation=90, va='bottom')
    ax.text(31.2, p, r'$p$', fontsize=14, color=GREEN, va='center')
    ax.text(15, 2.25, '不管妹妹把圈画多小、说走到第几项，', fontsize=11, color=NAVY, ha='center')
    ax.text(15, 2.08, '后面总还有一项掉进圈里', fontsize=11, color=NAVY, ha='center')
    ax.set_xlim(0, 34); ax.set_ylim(0.35, 2.45)
    ax.set_xlabel('第几个数', fontsize=11, color=NAVY)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9, colors=NAVY)
    save(fig, 'fig-07-cluster-point.png')


# ---------------------------------------------------------------- 08
def fig08():
    """两个聚点 ⇒ 没有极限。"""
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    k = np.arange(1, 15)
    u = 2 - 1.0 / 2 ** (k - 1)
    v = 1.5 - 0.5 / 3 ** (k - 1)
    n_odd, n_even = 2 * k - 1, 2 * k
    ax.axhline(2.0, color=ORANGE, lw=1.4, ls='--')
    ax.axhline(1.5, color=GREEN, lw=1.4, ls='--')
    ax.plot(n_odd, u, 'o', ms=6.5, color=ORANGE, zorder=3, label='奇数号')
    ax.plot(n_even, v, 's', ms=6, color=GREEN, zorder=3, label='偶数号')
    ax.text(29.4, 2.0, '2', fontsize=13, color=ORANGE, va='center')
    ax.text(29.4, 1.5, r'$\frac{3}{2}$', fontsize=14, color=GREEN, va='center')
    ax.annotate('', xy=(24, 1.98), xytext=(24, 1.52),
                arrowprops=dict(arrowstyle='<|-|>', color=NAVY, lw=1.5))
    ax.text(23.2, 1.75, '永远差', fontsize=10.5, color=NAVY, ha='right')
    ax.text(23.2, 1.60, r'$\frac{1}{2}$', fontsize=13, color=NAVY, ha='right')
    ax.legend(loc='lower right', fontsize=10, frameon=False)
    ax.set_xlim(0, 32); ax.set_ylim(0.85, 2.22)
    ax.set_xlabel('第几个数', fontsize=11, color=NAVY)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9, colors=NAVY)
    save(fig, 'fig-08-two-cluster-points.png')


# ---------------------------------------------------------------- 09
def fig09():
    """从一维误差带到二维误差圈。"""
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.6))
    ax = axes[0]
    numberline(ax, -1.35, 1.35)
    ax.add_patch(Rectangle((-0.55, -0.1), 1.1, 0.2, fc=BAND, ec=ORANGE, lw=1.5))
    ax.plot([0], [0], 'o', ms=8, color=NAVY, zorder=4)
    ax.text(0, -0.16, r'$p$', ha='center', va='top', fontsize=13, color=NAVY)
    ax.text(0, 0.35, '数轴上：一段', ha='center', fontsize=11, color=NAVY)
    ax.text(-0.55, 0.16, r'$p-\varepsilon$', ha='center', fontsize=10, color=ORANGE)
    ax.text(0.55, 0.16, r'$p+\varepsilon$', ha='center', fontsize=10, color=ORANGE)
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-0.55, 0.62); ax.axis('off')

    ax = axes[1]
    ax.add_patch(Circle((0, 0), 0.62, fc=BAND, ec=ORANGE, lw=1.7))
    ax.plot([0], [0], 'o', ms=8, color=NAVY, zorder=4)
    ax.annotate('', xy=(0.62 * .707, 0.62 * .707), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.3))
    ax.text(0.20, 0.30, r'$\varepsilon$', fontsize=14, color=NAVY)
    ax.text(0.06, -0.20, r'$p$', fontsize=13, color=NAVY)
    ax.text(0, 0.86, '平面上：一个圈', ha='center', fontsize=11, color=NAVY)
    ax.set_xlim(-0.95, 0.95); ax.set_ylim(-0.80, 1.05)
    ax.set_aspect('equal'); ax.axis('off')
    fig.text(0.5, -0.03, '同一件事的两种样子：把「离 p 不超过 ε 的所有点」圈起来',
             ha='center', fontsize=10.5, color=GREY)
    save(fig, 'fig-09-neighborhood.png')


# ---------------------------------------------------------------- 10
def fig10():
    """内点 / 边界点 / 外点。"""
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    t = np.linspace(0, 2 * np.pi, 300)
    r = 1 + 0.16 * np.sin(3 * t) + 0.09 * np.cos(5 * t)
    ax.fill(r * np.cos(t), r * np.sin(t), color=LIGHT, ec=NAVY, lw=1.8, zorder=1)
    pts = [((0.15, 0.10), '内点', GREEN, 0.26),
           ((1.02, 0.42), '边界点', ORANGE, 0.24),
           ((1.62, -0.72), '外点', GREY, 0.24)]
    for (xy, name, col, rad) in pts:
        ax.add_patch(Circle(xy, rad, fc='none', ec=col, lw=1.6, ls='--', zorder=3))
        ax.plot([xy[0]], [xy[1]], 'o', ms=7, color=col, zorder=4)
        ax.text(xy[0], xy[1] + rad + 0.10, name, ha='center', fontsize=11, color=col)
    ax.text(0.0, -1.62, '内点：能画出一个整个圈都在里面的圈', ha='center', fontsize=10, color=GREEN)
    ax.text(0.0, -1.84, '边界点：怎么画，圈里都既有里面的点、也有外面的点',
            ha='center', fontsize=10, color=ORANGE)
    ax.set_xlim(-1.5, 2.1); ax.set_ylim(-2.0, 1.5)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-10-interior-boundary.png')


# ---------------------------------------------------------------- 11
def fig11():
    """开集 vs 闭集。"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.9))
    for ax, closed in zip(axes, (False, True)):
        ax.add_patch(Circle((0, 0), 1.0, fc=LIGHT,
                            ec=NAVY if closed else ORANGE, lw=2.4,
                            ls='-' if closed else (0, (4, 3))))
        ax.plot([0.15], [0.1], 'o', ms=6, color=GREEN)
        ax.add_patch(Circle((0.15, 0.1), 0.22, fc='none', ec=GREEN, lw=1.3, ls='--'))
        if closed:
            ax.plot([np.cos(0.9)], [np.sin(0.9)], 'o', ms=7, color=NAVY, zorder=5)
            ax.text(0, -1.42, '闭集：边界线算自己的', ha='center', fontsize=11, color=NAVY)
            ax.text(0, -1.70, '（皮包着馅）', ha='center', fontsize=10, color=GREY)
        else:
            ax.plot([np.cos(0.9)], [np.sin(0.9)], 'o', ms=7, mfc='white',
                    mec=ORANGE, mew=1.8, zorder=5)
            ax.text(0, -1.42, '开集：边界线不算自己的', ha='center', fontsize=11, color=ORANGE)
            ax.text(0, -1.70, '（每个点都能画个圈躲在里面）', ha='center', fontsize=10, color=GREY)
        ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.95, 1.25)
        ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-11-open-closed.png')


# ---------------------------------------------------------------- 12
def fig12():
    """闭包 = 自己 + 所有聚点。"""
    fig, ax = plt.subplots(figsize=(6.2, 2.2))
    numberline(ax, -0.15, 3.5, ticks=[3.0], ticklabels=[''])
    xs = [3 - 3.0 / 2 ** i for i in range(1, 10)]
    ax.plot(xs, [0] * len(xs), 'o', ms=7, color=NAVY, zorder=3)
    ax.plot([3.0], [0], 'o', ms=10, mfc='white', mec=ORANGE, mew=2.2, zorder=4)
    ax.text(3.0, -0.20, '聚点', ha='center', va='top', fontsize=11, color=ORANGE)
    ax.text(1.2, -0.20, '这一队数', ha='center', va='top', fontsize=11, color=NAVY)
    ax.text(1.75, 0.42, '把空心那个点也收进来，就叫「闭包」', ha='center',
            fontsize=11, color=NAVY)
    ax.text(1.75, 0.22, '收进来以后，这个集合就是闭集了', ha='center',
            fontsize=10, color=GREY)
    ax.set_xlim(-0.25, 3.7); ax.set_ylim(-0.55, 0.62); ax.axis('off')
    save(fig, 'fig-12-closure.png')


# ---------------------------------------------------------------- 13
def fig13():
    """连续的拓扑说法：开集的原像还是开集。"""
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ax.annotate('', xy=(4.6, 2.3), xytext=(0.2, 2.3),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.5))
    ax.annotate('', xy=(4.6, 0.5), xytext=(0.2, 0.5),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.5))
    ax.add_patch(Rectangle((1.55, 2.22), 1.0, 0.16, fc=LIGHT, ec=GREEN, lw=1.8))
    ax.add_patch(Rectangle((2.35, 0.42), 0.95, 0.16, fc=BAND, ec=ORANGE, lw=1.8))
    for x0, x1 in ((1.55, 2.35), (2.55, 3.30)):
        ax.annotate('', xy=(x1, 0.62), xytext=(x0, 2.18),
                    arrowprops=dict(arrowstyle='-|>', color=GREY, lw=1.1, ls=':'))
    ax.text(0.15, 1.98, '投进去的那条线', fontsize=11, color=NAVY, va='top')
    ax.text(0.15, 0.18, '掉出来的那条线', fontsize=11, color=NAVY, va='bottom')
    ax.text(2.05, 2.58, '②这一堆也一定是「没有边的一段」', ha='center',
            fontsize=10.5, color=GREEN)
    ax.text(3.55, 0.98, '①先在这里圈一段没有边的', ha='center',
            fontsize=10.5, color=ORANGE)
    ax.text(2.4, -0.42, '连续 ＝ 不管在下面怎么圈一个开集，', ha='center', fontsize=11, color=NAVY)
    ax.text(2.4, -0.66, '它在上面对应的那一堆，也一定是开集', ha='center', fontsize=11, color=NAVY)
    ax.set_xlim(0.0, 5.0); ax.set_ylim(-0.85, 2.95); ax.axis('off')
    save(fig, 'fig-13-continuity.png')


# ---------------------------------------------------------------- 14
def fig14():
    """紧致：无限多个圈里，挑得出有限几个就够盖住。"""
    fig, axes = plt.subplots(2, 1, figsize=(6.4, 3.4))
    rng = np.random.RandomState(11)
    centers = np.sort(np.concatenate([np.linspace(-0.01, 1.01, 22), rng.rand(16)]))
    radii = 0.045 + 0.035 * rng.rand(len(centers))

    def baseline(ax, lo=-0.02, hi=1.02):
        ax.plot([lo, hi], [0, 0], color=NAVY, lw=3.4, solid_capstyle='round', zorder=5)
        ax.plot([lo, hi], [0, 0], 'o', ms=7, color=NAVY, zorder=6)

    ax = axes[0]
    for c, r in zip(centers, radii):
        ax.add_patch(Circle((c, 0), r, fc=LIGHT, ec=GREY, lw=0.9, alpha=0.45, zorder=2))
    baseline(ax)
    ax.text(0.5, 0.20, '妹妹扔下无限多个圈，把这一整段都盖住了',
            ha='center', fontsize=11, color=NAVY)
    ax.set_xlim(-0.16, 1.16); ax.set_ylim(-0.13, 0.30)
    ax.set_aspect('equal'); ax.axis('off')

    ax = axes[1]
    pick = [(0.03, 0.11), (0.23, 0.115), (0.43, 0.115), (0.62, 0.11),
            (0.80, 0.11), (0.98, 0.10)]
    for c, r in pick:
        ax.add_patch(Circle((c, 0), r, fc=BAND, ec=ORANGE, lw=1.5, alpha=0.8, zorder=2))
    baseline(ax)
    ax.text(0.5, 0.20, '姐姐只挑出 6 个，照样盖得住 —— 这就叫「紧致」',
            ha='center', fontsize=11, color=ORANGE)
    ax.set_xlim(-0.16, 1.16); ax.set_ylim(-0.13, 0.30)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-14-compactness.png')


# ---------------------------------------------------------------- 15
def fig15():
    """连通 vs 不连通。"""
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.5))
    t = np.linspace(0, 2 * np.pi, 300)
    ax = axes[0]
    r = 1 + 0.18 * np.sin(3 * t)
    ax.fill(r * np.cos(t), r * np.sin(t), color=LIGHT, ec=NAVY, lw=1.8)
    ax.text(0, -1.62, '一整块：连通', ha='center', fontsize=11.5, color=NAVY)
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-2.0, 1.4)
    ax.set_aspect('equal'); ax.axis('off')
    ax = axes[1]
    for dx in (-0.72, 0.72):
        ax.fill(0.62 * np.cos(t) + dx, 0.62 * np.sin(t), color=BAND, ec=ORANGE, lw=1.8)
    ax.plot([0, 0], [-1.15, 1.15], color=GREY, lw=1.4, ls='--')
    ax.text(0, -1.62, '掰得开两半：不连通', ha='center', fontsize=11.5, color=ORANGE)
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-2.0, 1.4)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-15-connected.png')


# ---------------------------------------------------------------- 16
def fig16():
    """豪斯多夫分离：两个不同的点，能用不打架的圈隔开。"""
    fig, ax = plt.subplots(figsize=(6.0, 2.3))
    ax.add_patch(Circle((-1.05, 0), 0.62, fc=BAND, ec=ORANGE, lw=1.8))
    ax.add_patch(Circle((1.05, 0), 0.62, fc=LIGHT, ec=GREEN, lw=1.8))
    ax.plot([-1.05], [0], 'o', ms=8, color=ORANGE, zorder=4)
    ax.plot([1.05], [0], 'o', ms=8, color=GREEN, zorder=4)
    ax.text(-1.05, -0.90, r'$p$', ha='center', fontsize=14, color=ORANGE)
    ax.text(1.05, -0.90, r'$q$', ha='center', fontsize=14, color=GREEN)
    ax.annotate('', xy=(0.42, 0), xytext=(-0.42, 0),
                arrowprops=dict(arrowstyle='<|-|>', color=NAVY, lw=1.4))
    ax.text(0, 0.05, '不重叠', ha='center', va='bottom', fontsize=10.5, color=NAVY,
            bbox=dict(fc='white', ec='none', pad=0.2))
    ax.text(0, 1.30, '两个不一样的点，总能各自画一个圈，互不打架',
            ha='center', fontsize=11, color=NAVY)
    ax.text(0, -1.45, '——这才是「极限只能有一个」的真正原因',
            ha='center', fontsize=10.5, color=GREY)
    ax.set_xlim(-2.3, 2.3); ax.set_ylim(-1.80, 1.60)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-16-hausdorff.png')


# ---------------------------------------------------------------- 17
def fig17():
    """数洞：橡皮几何看什么。"""
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    t = np.linspace(0, 2 * np.pi, 200)

    # 纸片
    ax.add_patch(FancyBboxPatch((0.1, 0.35), 0.95, 0.8,
                                boxstyle='round,pad=0.02,rounding_size=0.08',
                                fc=LIGHT, ec=NAVY, lw=1.6))
    ax.text(0.58, 0.05, '纸片', ha='center', fontsize=11, color=NAVY)
    ax.text(0.58, -0.28, '0 个洞', ha='center', fontsize=10.5, color=GREY)

    # 甜甜圈
    cx = 2.0
    ax.fill(0.52 * np.cos(t) + cx, 0.52 * np.sin(t) + 0.75, color=LIGHT, ec=NAVY, lw=1.6)
    ax.fill(0.20 * np.cos(t) + cx, 0.20 * np.sin(t) + 0.75, color='white', ec=NAVY, lw=1.6)
    ax.text(cx, 0.05, '甜甜圈', ha='center', fontsize=11, color=NAVY)
    ax.text(cx, -0.28, '1 个洞', ha='center', fontsize=10.5, color=ORANGE)

    # 咖啡杯
    cx = 3.62
    body_r = cx + 0.26                      # 杯身右壁
    ax.add_patch(FancyBboxPatch((cx - 0.40, 0.35), 0.66, 0.82,
                                boxstyle='round,pad=0.02,rounding_size=0.10',
                                fc=LIGHT, ec=NAVY, lw=1.6))
    # 把手：两端正好落在杯壁上，中间才围出一个真正的洞
    ax.add_patch(Arc((body_r, 0.76), 0.62, 0.62, theta1=-90, theta2=90,
                     color=NAVY, lw=3.0))
    ax.add_patch(Arc((body_r, 0.76), 0.30, 0.30, theta1=-90, theta2=90,
                     color=NAVY, lw=3.0))
    for sgn in (-1, 1):
        ax.plot([body_r, body_r], [0.76 + sgn * 0.15, 0.76 + sgn * 0.31],
                color=NAVY, lw=3.0)
    ax.text(cx, 0.05, '咖啡杯', ha='center', fontsize=11, color=NAVY)
    ax.text(cx, -0.28, '1 个洞', ha='center', fontsize=10.5, color=ORANGE)

    # 眼镜
    cx = 5.36
    for dx in (-0.46, 0.46):
        ax.fill(0.40 * np.cos(t) + cx + dx, 0.40 * np.sin(t) + 0.75,
                color=LIGHT, ec=NAVY, lw=1.6)
        ax.fill(0.17 * np.cos(t) + cx + dx, 0.17 * np.sin(t) + 0.75,
                color='white', ec=NAVY, lw=1.6)
    ax.plot([cx - 0.12, cx + 0.12], [0.75, 0.75], color=NAVY, lw=3)
    ax.text(cx, 0.05, '眼镜框', ha='center', fontsize=11, color=NAVY)
    ax.text(cx, -0.28, '2 个洞', ha='center', fontsize=10.5, color=ORANGE)

    ax.annotate('', xy=(3.05, 0.75), xytext=(2.6, 0.75),
                arrowprops=dict(arrowstyle='<|-|>', color=ORANGE, lw=1.6))
    ax.text(2.82, 1.45, '在拓扑眼里', ha='center', fontsize=10, color=ORANGE)
    ax.text(2.82, 1.22, '这两个一样', ha='center', fontsize=10, color=ORANGE)
    ax.set_xlim(-0.1, 6.05); ax.set_ylim(-0.55, 1.75)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-17-holes.png')


# ---------------------------------------------------------------- 18
def fig18():
    """二分法：每次砍一半，留下装着无限多号码的那半边。"""
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    levels = [(0.0, 1.0), (0.5, 1.0), (0.5, 0.75), (0.625, 0.75), (0.625, 0.6875)]
    rng = np.random.RandomState(5)

    for i, (a, b) in enumerate(levels):
        y = -i * 0.62
        m = (a + b) / 2.0
        keep = levels[i + 1] if i + 1 < len(levels) else None
        # 整段：先画灰底
        ax.plot([a, b], [y, y], color=GREY, lw=6, solid_capstyle='butt', zorder=2)
        if keep:
            ax.plot([keep[0], keep[1]], [y, y], color=ORANGE, lw=6,
                    solid_capstyle='butt', zorder=3)
            ax.plot([m, m], [y - 0.15, y + 0.15], color=NAVY, lw=1.6, zorder=4)
        for x in (a, b):
            ax.plot([x, x], [y - 0.11, y + 0.11], color=NAVY, lw=1.8, zorder=4)
        ax.text(a - 0.035, y, '第 %d 次' % i if i else '一开始',
                ha='right', va='center', fontsize=9.5, color=NAVY)

    # 第 0 层撒一些数列项
    y0 = 0
    xs = np.concatenate([rng.rand(16) * 1.0, 0.66 + 0.06 * (rng.rand(10) - 0.5)])
    ax.plot(xs, [y0 + 0.30] * len(xs), 'o', ms=4.5, color=NAVY, alpha=0.75, zorder=5)
    ax.text(0.5, y0 + 0.52, '一队被困在这一段里的数', ha='center',
            fontsize=10.5, color=NAVY)

    p = 0.66
    ax.plot([p, p], [-2.72, 0.18], color=ORANGE, lw=1.0, ls=':', zorder=1)
    ax.plot([p], [-2.72], 'o', ms=9, color=ORANGE, zorder=6)
    ax.text(p, -2.95, '套住的那个点，就是聚点', ha='center', fontsize=10.5, color=ORANGE)

    ax.text(1.06, -0.31, '每次砍一半，', fontsize=10, color=NAVY)
    ax.text(1.06, -0.55, '留下装着', fontsize=10, color=NAVY)
    ax.text(1.06, -0.79, '无限多个号码', fontsize=10, color=ORANGE)
    ax.text(1.06, -1.03, '的那半边', fontsize=10, color=NAVY)

    ax.set_xlim(-0.20, 1.52); ax.set_ylim(-3.15, 0.72); ax.axis('off')
    save(fig, 'fig-18-bisection.png')


# ---------------------------------------------------------------- 19
def fig19():
    """一位一位地把一个点钉住：小数就是一串越套越小的区间。"""
    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    rows = [(0.0, 1.0, 6, '0.6'), (0.6, 0.7, 6, '0.66'), (0.66, 0.67, 5, '0.665')]
    for i, (a, b, d, lab) in enumerate(rows):
        y = -i * 1.15
        w = b - a
        ax.plot([0, 1], [y, y], color=NAVY, lw=2.2, solid_capstyle='butt', zorder=3)
        for k in range(11):
            x = k / 10.0
            ax.plot([x, x], [y - 0.055, y + 0.055], color=NAVY, lw=1.1, zorder=3)
        lo, hi = d / 10.0, (d + 1) / 10.0
        ax.add_patch(Rectangle((lo, y - 0.11), 0.1, 0.22, fc=BAND, ec=ORANGE,
                               lw=1.8, zorder=2))
        ax.text(-0.045, y, '%.10g' % a, ha='right', va='center', fontsize=9.5, color=NAVY)
        ax.text(1.045, y, '%.10g' % b, ha='left', va='center', fontsize=9.5, color=NAVY)
        ax.text(1.30, y + 0.02, '第 %d 位是 %d' % (i + 1, d), fontsize=10.5, color=ORANGE)
        ax.text(1.30, y - 0.24, '缩到 ' + lab + ' 那一格', fontsize=9.5, color=GREY)
        if i + 1 < len(rows):
            for xs, xt in ((lo, 0.0), (hi, 1.0)):
                ax.annotate('', xy=(xt, y - 1.15 + 0.09), xytext=(xs, y - 0.13),
                            arrowprops=dict(arrowstyle='-', color=GREY, lw=1.0, ls=':'))
    ax.text(0.5, 0.62, '每多写一位小数，就把这个点关进一个小十倍的格子里',
            ha='center', fontsize=11, color=NAVY)
    ax.text(0.5, -3.05, '写不完，但每一位都写得出来 —— 这就是一个实数',
            ha='center', fontsize=10.5, color=ORANGE)
    ax.set_xlim(-0.22, 2.15); ax.set_ylim(-3.30, 0.85); ax.axis('off')
    save(fig, 'fig-19-decimal-zoom.png')


# ---------------------------------------------------------------- 20
def fig20():
    """戴德金分割：切一刀，切口上正好有一个数。"""
    fig, ax = plt.subplots(figsize=(6.4, 2.2))
    c = 0.58
    ax.plot([0.02, c], [0, 0], color=NAVY, lw=6, solid_capstyle='butt', zorder=2)
    ax.plot([c, 1.06], [0, 0], color=ORANGE, lw=6, solid_capstyle='butt', zorder=2)
    ax.plot([c, c], [-0.30, 0.30], color=GREY, lw=1.6, ls='--', zorder=3)
    ax.plot([c], [0], 'o', ms=11, mfc='white', mec=NAVY, mew=2.4, zorder=5)
    ax.text(0.28, 0.20, '左边这一堆', ha='center', fontsize=11, color=NAVY)
    ax.text(0.84, 0.20, '右边这一堆', ha='center', fontsize=11, color=ORANGE)
    ax.text(c, -0.42, '切口', ha='center', fontsize=11, color=NAVY)
    ax.text(0.54, 0.62, '不管你怎么切，切口上一定正好站着一个数',
            ha='center', fontsize=11.5, color=NAVY)
    ax.text(0.54, -0.78, '数轴上没有缝 —— 这就是"实数没有洞"',
            ha='center', fontsize=10.5, color=GREY)
    ax.set_xlim(-0.03, 1.11); ax.set_ylim(-0.95, 0.82); ax.axis('off')
    save(fig, 'fig-20-dedekind-cut.png')


# ---------------------------------------------------------------- 21
def fig21():
    """八大定理：八种说法，一件事。"""
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    names = ['① 确界原理', '② 单调有界', '③ 区间套', '④ 有限覆盖',
             '⑤ 聚点定理', '⑥ 致密性', '⑦ 柯西准则', '⑧ 戴德金分割']
    R = 1.62
    ax.add_patch(Circle((0, 0), 0.70, fc=BAND, ec=ORANGE, lw=2.0, zorder=3))
    ax.text(0, 0.14, '数轴上', ha='center', va='center', fontsize=12.5,
            color=ORANGE, fontweight='bold', zorder=4)
    ax.text(0, -0.16, '没有洞', ha='center', va='center', fontsize=12.5,
            color=ORANGE, fontweight='bold', zorder=4)
    for i, nm in enumerate(names):
        th = np.pi / 2 - i * 2 * np.pi / 8
        x, y = R * np.cos(th), R * np.sin(th)
        ax.plot([0.72 * np.cos(th), (R - 0.42) * np.cos(th)],
                [0.72 * np.sin(th), (R - 0.42) * np.sin(th)],
                color=GREY, lw=1.2, ls=':', zorder=1)
        ax.text(x, y, nm, ha='center', va='center', fontsize=10.5, color=NAVY,
                bbox=dict(boxstyle='round,pad=0.34', fc=LIGHT, ec=NAVY, lw=1.4),
                zorder=4)
    ax.text(0, -2.42, '任意一个成立，其余七个都跟着成立', ha='center',
            fontsize=11, color=NAVY)
    ax.set_xlim(-2.45, 2.45); ax.set_ylim(-2.70, 2.25)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-21-eight-theorems.png')


# ---------------------------------------------------------------- 22
def fig22():
    """上确界：所有上界里最小的那一个。"""
    fig, ax = plt.subplots(figsize=(6.4, 2.4))
    numberline(ax, -0.08, 1.22)
    rng = np.random.RandomState(9)
    xs = np.concatenate([rng.rand(9) * 0.62, 0.70 - 0.10 * rng.rand(6) ** 2])
    ax.plot(xs, [0] * len(xs), 'o', ms=7, color=NAVY, zorder=3)
    sup = 0.72
    ax.add_patch(Rectangle((sup, -0.075), 0.50, 0.15, fc=BAND, ec='none', zorder=1))
    ax.plot([sup], [0], 'o', ms=11, mfc='white', mec=ORANGE, mew=2.6, zorder=5)
    ax.text(0.30, -0.20, '这一堆数', ha='center', va='top', fontsize=11, color=NAVY)
    ax.text(0.97, -0.20, '上界们（都在右边）', ha='center', va='top',
            fontsize=10.5, color=ORANGE)
    ax.text(sup, 0.19, '上确界', ha='center', fontsize=11, color=ORANGE)
    ax.text(sup, 0.36, '＝ 所有上界里最小的那个', ha='center', fontsize=10, color=GREY)
    ax.text(0.55, -0.52, '注意：上确界自己不一定在这堆数里面',
            ha='center', fontsize=10.5, color=NAVY)
    ax.set_xlim(-0.14, 1.30); ax.set_ylim(-0.70, 0.52); ax.axis('off')
    save(fig, 'fig-22-supremum.png')


# ---------------------------------------------------------------- 23
def fig23():
    """夹逼：上下两队都奔向 L，夹在中间那队想跑也跑不掉。"""
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    n = np.arange(1, 22)
    L = 1.0
    a = L - 0.95 / n
    c = L + 1.15 / n
    t = 0.5 + 0.42 * np.sin(1.9 * n)
    b = a + (c - a) * t

    ax.fill_between(n, a, c, color=BAND, alpha=0.55, zorder=0)
    ax.axhline(L, color=GREEN, lw=1.8, zorder=1)
    ax.plot(n, c, 'o-', ms=5, lw=1.0, color=ORANGE, zorder=3)
    ax.plot(n, a, 'o-', ms=5, lw=1.0, color=ORANGE, zorder=3)
    ax.plot(n, b, 'o', ms=7, color=NAVY, zorder=4)

    # 右端三条线已经收敛，标签会挤成一团 —— 标在左边带子还宽的地方
    ax.text(22.0, L, r'$L$', fontsize=13, color=GREEN, va='center')
    ax.text(4.2, c[3] + 0.13, r'$c_n$', fontsize=13, color=ORANGE, ha='center')
    ax.text(4.2, a[3] - 0.19, r'$a_n$', fontsize=13, color=ORANGE, ha='center')
    ax.text(9.9, 1.40, r'$b_n$', fontsize=13, color=NAVY, ha='center', va='center')
    ax.text(11.5, 1.72, '上面一队奔向 L，下面一队也奔向 L', ha='center',
            fontsize=11, color=NAVY)
    ax.text(11.5, 1.56, '夹在中间的那队（深蓝），想跑也跑不掉', ha='center',
            fontsize=11, color=NAVY)
    ax.annotate('', xy=(7.15, b[6] + 0.05), xytext=(9.4, 1.36),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.1))

    ax.set_xlim(0, 24); ax.set_ylim(-0.15, 1.95)
    ax.set_xlabel('第几个数', fontsize=11, color=NAVY)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=9, colors=NAVY)
    save(fig, 'fig-23-squeeze.png')


# ---------------------------------------------------------------- 24
def fig24():
    """取极限是一种运算：它和别的运算换不换得了次序。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.2))

    def square(ax, op, tl, tr, bl, br, ok):
        col = GREEN if ok else RED
        for (x, y, txt) in ((0.06, 0.86, tl), (0.94, 0.86, tr),
                            (0.06, 0.14, bl), (0.94, 0.14, br)):
            ax.text(x, y, txt, ha='left' if x < 0.5 else 'right',
                    va='center', fontsize=12, color=NAVY)
        ax.annotate('', xy=(0.66, 0.86), xytext=(0.34, 0.86),
                    arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.6))
        ax.annotate('', xy=(0.66, 0.14), xytext=(0.34, 0.14),
                    arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.6))
        ax.annotate('', xy=(0.06, 0.26), xytext=(0.06, 0.74),
                    arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=1.6))
        ax.annotate('', xy=(0.94, 0.26), xytext=(0.94, 0.74),
                    arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=1.6))
        ax.text(0.5, 0.93, op, ha='center', fontsize=10.5, color=NAVY)
        ax.text(0.5, 0.055, op, ha='center', fontsize=10.5, color=NAVY)
        ax.text(0.015, 0.5, '取\n极\n限', ha='center', va='center',
                fontsize=10, color=ORANGE)
        ax.text(0.985, 0.5, '取\n极\n限', ha='center', va='center',
                fontsize=10, color=ORANGE)
        # 勾和叉用线条画 —— 中文字体里没有 ✓ ✗ 的字形，写字符会变豆腐块
        if ok:
            ax.plot([0.42, 0.48, 0.60], [0.50, 0.43, 0.60], color=col, lw=3.4,
                    solid_capstyle='round')
        else:
            ax.plot([0.43, 0.59], [0.42, 0.58], color=col, lw=3.4, solid_capstyle='round')
            ax.plot([0.43, 0.59], [0.58, 0.42], color=col, lw=3.4, solid_capstyle='round')
        ax.set_xlim(-0.08, 1.08); ax.set_ylim(-0.22, 1.12); ax.axis('off')

    square(axs[0], '先加起来', r'$a_n,\ b_n$', r'$a_n+b_n$', r'$A,\ B$', r'$A+B$', True)
    axs[0].text(0.5, -0.15, '两条路走到同一个地方', ha='center',
                fontsize=10.5, color=GREEN)
    square(axs[1], '先比大小', r'$a_n>0$', '成立', r'$A$', r'$A>0$', False)
    axs[1].text(0.5, -0.15, '这里断了：只剩 A ≥ 0', ha='center',
                fontsize=10.5, color=RED)
    fig.text(0.5, -0.04, '取极限是一台机器。问题是：它和别的运算，换不换得了次序？',
             ha='center', fontsize=11, color=NAVY)
    save(fig, 'fig-24-commute.png')


# ---------------------------------------------------------------- 25
def fig25():
    """连"是分数"都过不了取极限这一关 —— 和 fig-24 同构的第三个方框。"""
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.text(0.04, 0.86, r'$a_n$', ha='left', va='center', fontsize=13, color=NAVY)
    ax.text(0.155, 0.86, '的每一项', ha='left', va='center', fontsize=10, color=GREY)
    ax.text(0.96, 0.86, '是分数', ha='right', va='center', fontsize=12.5, color=GREEN)
    ax.text(0.04, 0.14, r'$\sqrt{2}$', ha='left', va='center', fontsize=13, color=NAVY)
    ax.text(0.96, 0.14, '不是分数', ha='right', va='center', fontsize=12.5, color=RED)
    ax.annotate('', xy=(0.66, 0.86), xytext=(0.30, 0.86),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.6))
    ax.annotate('', xy=(0.66, 0.14), xytext=(0.30, 0.14),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.6))
    ax.text(0.48, 0.93, '问："是分数吗"', ha='center', fontsize=10.5, color=NAVY)
    ax.text(0.48, 0.055, '问："是分数吗"', ha='center', fontsize=10.5, color=NAVY)
    ax.annotate('', xy=(0.06, 0.26), xytext=(0.06, 0.74),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=1.6))
    ax.text(0.012, 0.5, '取\n极\n限', ha='center', va='center', fontsize=10, color=ORANGE)
    ax.plot([0.40, 0.56], [0.40, 0.60], color=RED, lw=3.4, solid_capstyle='round')
    ax.plot([0.40, 0.56], [0.60, 0.40], color=RED, lw=3.4, solid_capstyle='round')
    ax.text(0.5, -0.12, '前两次取极限只是削弱了性质；这一次，性质整个没了',
            ha='center', fontsize=11, color=RED)
    ax.text(0.5, -0.24, '在只有分数的世界里，这队数满足柯西条件，却没有极限',
            ha='center', fontsize=10.5, color=NAVY)
    ax.set_xlim(-0.06, 1.06); ax.set_ylim(-0.32, 1.06); ax.axis('off')
    save(fig, 'fig-25-not-a-fraction.png')


if __name__ == '__main__':
    print('generating figures ->', OUT)
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
              fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17,
              fig18, fig19, fig20, fig21, fig22, fig23, fig24, fig25):
        f()
    print('done:', len(os.listdir(OUT)), 'files')
