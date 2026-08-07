#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《给小学生讲微积分（下）》插图。

约定同第一册：中文用 Hiragino Sans GB，数学走 mathtext，两者绝不混在同一个字符串里。
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle

plt.rcParams['font.sans-serif'] = ['Hiragino Sans GB', 'Arial Unicode MS', 'Songti SC']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'dejavusans'

NAVY, ORANGE, GREEN = '#1F3A6E', '#E8743B', '#2E9E6B'
GREY, LIGHT, BAND = '#9AA5B1', '#DCE7F7', '#FBE3D6'

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
os.makedirs(OUT, exist_ok=True)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  wrote', name)


def axes(ax, xmax, ymax, xlabel='投进去的数', ylabel='吐出来的数'):
    ax.annotate('', xy=(xmax, 0), xytext=(-0.08 * xmax, 0),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.5))
    ax.annotate('', xy=(0, ymax), xytext=(0, -0.08 * ymax),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.5))
    ax.text(xmax, -0.09 * ymax, xlabel, ha='right', va='top', fontsize=10, color=NAVY)
    # 注意：纵轴说明占住左上角，正文说明别放在 y > 0.85*ymax 的地方
    ax.text(0.06 * xmax, ymax, ylabel, ha='left', va='top', fontsize=10, color=NAVY)
    ax.set_xlim(-0.12 * xmax, xmax * 1.06)
    ax.set_ylim(-0.16 * ymax, ymax * 1.06)
    ax.axis('off')


# ---------------------------------------------------------------- 01
def fig01():
    """机器的图：每投一个数，画一个点。"""
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    t = np.linspace(0, 3, 200)
    axes(ax, 3.3, 9.6)
    ax.plot(t, t ** 2, color=NAVY, lw=2.2, zorder=3)
    for v in (1, 2, 3):
        ax.plot([v, v], [0, v ** 2], color=GREY, lw=1.0, ls=':')
        ax.plot([0, v], [v ** 2, v ** 2], color=GREY, lw=1.0, ls=':')
        ax.plot([v], [v ** 2], 'o', ms=8, color=ORANGE, zorder=4)
        ax.text(v, -0.35, '%d' % v, ha='center', va='top', fontsize=10.5, color=NAVY)
        ax.text(-0.12, v ** 2, '%d' % v ** 2, ha='right', va='center',
                fontsize=10.5, color=NAVY)
    ax.text(2.15, 7.6, '投 3 出 9', fontsize=11, color=ORANGE)
    ax.text(0.55, 8.4, '这台机器：投进去的数', fontsize=11, color=NAVY)
    ax.text(0.55, 7.6, '自己乘自己', fontsize=11, color=NAVY)
    save(fig, 'fig-01-machine.png')


# ---------------------------------------------------------------- 02
def fig02():
    """割线转切线：把两个点挪近。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 3.0))
    t = np.linspace(0, 2.6, 200)
    for ax, h, tag in zip(axs, (1.2, 0.35), ('h 还很大', 'h 变小了')):
        axes(ax, 2.9, 7.2)
        ax.plot(t, t ** 2, color=NAVY, lw=2.0, zorder=3)
        a = 1.0
        xs = [a, a + h]
        ys = [a ** 2, (a + h) ** 2]
        k = (ys[1] - ys[0]) / h
        u = np.linspace(-0.5, 1.9, 10)
        ax.plot(u, ys[0] + k * (u - a), color=ORANGE, lw=1.8, zorder=2)
        ax.plot(xs, ys, 'o', ms=7, color=ORANGE, zorder=4)
        ax.plot([xs[0], xs[1]], [ys[0], ys[0]], color=GREY, lw=1.2)
        ax.plot([xs[1], xs[1]], [ys[0], ys[1]], color=GREY, lw=1.2)
        ax.text((xs[0] + xs[1]) / 2, ys[0] - 0.55, r'$h$', ha='center',
                fontsize=12, color=GREY)
        ax.text(0.9, 6.5, tag, fontsize=11, color=NAVY)
    fig.text(0.5, -0.02, '两个点越挨越近，那条橙色的线就越来越像"贴着曲线走"',
             ha='center', fontsize=10.5, color=GREY)
    save(fig, 'fig-02-secant-to-tangent.png')


# ---------------------------------------------------------------- 03
def fig03():
    """平均变化率就是"竖着变了多少 ÷ 横着挪了多少"。"""
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    t = np.linspace(0, 2.6, 200)
    axes(ax, 2.9, 7.2)
    ax.plot(t, t ** 2, color=NAVY, lw=2.2, zorder=3)
    a, h = 1.0, 1.0
    ax.plot([a, a + h], [a ** 2, (a + h) ** 2], 'o', ms=8, color=ORANGE, zorder=4)
    ax.plot([a, a + h], [a ** 2, a ** 2], color=GREEN, lw=2.0)
    ax.plot([a + h, a + h], [a ** 2, (a + h) ** 2], color=GREEN, lw=2.0)
    ax.text(a + h / 2, a ** 2 - 0.6, '横着挪了 h', ha='center', fontsize=10.5, color=GREEN)
    ax.text(a + h + 0.08, (a ** 2 + (a + h) ** 2) / 2, '竖着变了这么多',
            fontsize=10.5, color=GREEN)
    ax.text(0.12, 6.3, '这两个一比，就是"走得多快"', fontsize=11, color=NAVY)
    save(fig, 'fig-03-difference-quotient.png')


# ---------------------------------------------------------------- 04
def fig04():
    """乘积法则：长方形长宽都变一点。"""
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    f, g, df, dg = 2.4, 1.8, 0.7, 0.55
    ax.add_patch(Rectangle((0, 0), f, g, fc=LIGHT, ec=NAVY, lw=1.6))
    ax.add_patch(Rectangle((f, 0), df, g, fc=BAND, ec=ORANGE, lw=1.4))
    ax.add_patch(Rectangle((0, g), f, dg, fc=BAND, ec=ORANGE, lw=1.4))
    ax.add_patch(Rectangle((f, g), df, dg, fc='#EFEFEF', ec=GREY, lw=1.2, ls='--'))
    ax.text(f / 2, g / 2, '本来的', ha='center', va='center', fontsize=11, color=NAVY)
    ax.text(f + df / 2, g / 2, '长\n变\n了', ha='center', va='center',
            fontsize=9.5, color=ORANGE)
    ax.text(f / 2, g + dg / 2, '宽变了', ha='center', va='center',
            fontsize=10, color=ORANGE)
    ax.text(f + df + 0.06, g + dg / 2, '这一小块\n取极限时\n奔向 0', fontsize=9.5, color=GREY,
            va='center')
    ax.text(f / 2, -0.28, '长', ha='center', fontsize=11, color=NAVY)
    ax.text(-0.16, g / 2, '宽', va='center', ha='right', fontsize=11, color=NAVY)
    ax.set_xlim(-0.6, f + df + 1.35); ax.set_ylim(-0.55, g + dg + 0.35)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-04-product-rule.png')


# ---------------------------------------------------------------- 05
def fig05():
    """f′ 的正负：在涨还是在跌。"""
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    t = np.linspace(-0.3, 3.3, 300)
    y = t ** 3 / 3 - 1.5 * t ** 2 + 2 * t + 1.2
    axes(ax, 3.5, 3.4, xlabel='投进去的数', ylabel='吐出来的数')
    ax.plot(t[t <= 1], y[t <= 1], color=GREEN, lw=2.4)
    ax.plot(t[(t >= 1) & (t <= 2)], y[(t >= 1) & (t <= 2)], color=ORANGE, lw=2.4)
    ax.plot(t[t >= 2], y[t >= 2], color=GREEN, lw=2.4)
    for v, lab in ((1, '最高点'), (2, '最低点')):
        yy = v ** 3 / 3 - 1.5 * v ** 2 + 2 * v + 1.2
        ax.plot([v], [yy], 'o', ms=9, color=NAVY, zorder=5)
        ax.plot([v - 0.42, v + 0.42], [yy, yy], color=NAVY, lw=1.6, ls='--')
        ax.text(v, yy + (0.28 if lab == '最高点' else -0.42), lab,
                ha='center', fontsize=10.5, color=NAVY)
    # 图例放左上会压住纵轴说明和"最高点"标签 —— 挪到曲线下方的空白处
    ax.text(1.45, 0.92, '绿色：在涨（f′ 是正的）', fontsize=10.5, color=GREEN)
    ax.text(1.45, 0.57, '橙色：在跌（f′ 是负的）', fontsize=10.5, color=ORANGE)
    ax.text(1.45, 0.22, '拐弯处：f′ 正好是 0', fontsize=10.5, color=NAVY)
    save(fig, 'fig-05-sign.png')


# ---------------------------------------------------------------- 06
def fig06():
    """切成竖条：矮的一套低估，高的一套高估。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.9))
    n = 6
    b = 2.0
    t = np.linspace(0, b, 200)
    for ax, mode, tag, col in zip(axs, ('low', 'high'),
                                  ('每条取左边那头当高：矮了', '每条取右边那头当高：高了'),
                                  (GREEN, ORANGE)):
        axes(ax, 2.35, 4.6)
        for k in range(n):
            a0 = k * b / n
            a1 = (k + 1) * b / n
            h = (a0 if mode == 'low' else a1) ** 2
            ax.add_patch(Rectangle((a0, 0), b / n, h, fc=BAND if mode == 'high' else LIGHT,
                                   ec=col, lw=1.1, alpha=0.85, zorder=2))
        ax.plot(t, t ** 2, color=NAVY, lw=2.2, zorder=3)
        # 说明放到图下方 —— 放在左上角会压住纵轴的"吐出来的数"
        ax.set_ylim(-1.55, 4.9)
        ax.text(1.1, -1.35, tag, ha='center', fontsize=10.5, color=col)
    fig.text(0.5, -0.03, '真面积被夹在两套长条中间；条子越细，两套越靠拢',
             ha='center', fontsize=10.5, color=GREY)
    save(fig, 'fig-06-strips.png')


# ---------------------------------------------------------------- 07
def fig07():
    """1+2+…+n：两个三角摆成一个长方形。"""
    fig, ax = plt.subplots(figsize=(5.6, 2.7))
    n = 5
    for r in range(n):
        for c in range(r + 1):
            ax.plot([c], [n - 1 - r], 'o', ms=11, color=NAVY)
        for c in range(r + 1, n + 1):
            ax.plot([c], [n - 1 - r], 'o', ms=11, mfc='white', mec=ORANGE, mew=1.8)
    ax.text(n / 2.0, n + 0.25, '一共 n 行、n+1 列，正好一半实心一半空心',
            ha='center', fontsize=10.5, color=NAVY)
    ax.text(n / 2.0, -1.35, '所以 1+2+…+n 就是这个长方形的一半', ha='center',
            fontsize=11, color=NAVY)
    ax.text(n / 2.0, -2.0, r'$1+2+\cdots+n=\frac{n(n+1)}{2}$', ha='center',
            fontsize=14, color=ORANGE)
    ax.set_xlim(-0.8, n + 0.8); ax.set_ylim(-2.4, n + 0.7)
    ax.set_aspect('equal'); ax.axis('off')
    save(fig, 'fig-07-triangle-number.png')


# ---------------------------------------------------------------- 08
def fig08():
    """面积函数：多走一点点，面积多出一小条。"""
    fig, ax = plt.subplots(figsize=(5.8, 3.2))
    b = 2.4
    t = np.linspace(0, b, 200)
    axes(ax, 2.7, 6.4)
    a, h = 1.5, 0.45
    ax.fill_between(t[t <= a], 0, (t[t <= a]) ** 2, color=LIGHT, zorder=1)
    xs = t[(t >= a) & (t <= a + h)]
    ax.fill_between(xs, 0, xs ** 2, color=BAND, zorder=2)
    ax.plot(t, t ** 2, color=NAVY, lw=2.2, zorder=3)
    ax.plot([a, a], [0, a ** 2], color=NAVY, lw=1.2, ls=':')
    ax.plot([a + h, a + h], [0, (a + h) ** 2], color=ORANGE, lw=1.2, ls=':')
    ax.text(a * 0.62, 0.30, r'$A(a)$', ha='center', fontsize=13, color=NAVY, zorder=5)
    ax.text(0.06, 4.7, '已经攒下的面积', fontsize=10.5, color=NAVY)
    ax.annotate('', xy=(a * 0.66, 0.75), xytext=(0.5, 4.45),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.0))
    ax.text(a + h + 0.1, 1.4, '多出来的一小条', fontsize=10.5, color=ORANGE)
    ax.text(a + h + 0.1, 0.85, '宽是 h，高差不多是', fontsize=10.5, color=ORANGE)
    ax.text(a + h + 0.1, 0.30, r'$f(a)$', fontsize=12, color=ORANGE)
    ax.text(a, -0.55, r'$a$', ha='center', fontsize=12, color=NAVY)
    save(fig, 'fig-08-area-function.png')


# ---------------------------------------------------------------- 09
def fig09():
    """开方是平方反过来：沿着斜线一翻。"""
    fig, ax = plt.subplots(figsize=(4.4, 4.0))
    t = np.linspace(0, 2.0, 200)
    ax.plot(t, t ** 2, color=NAVY, lw=2.2)
    ax.plot(t, np.sqrt(t), color=ORANGE, lw=2.2)
    ax.plot([0, 2.0], [0, 2.0], color=GREY, lw=1.2, ls='--')
    ax.text(1.42, 2.15, '平方', color=NAVY, fontsize=11)
    ax.text(1.95, 1.30, '开方', color=ORANGE, fontsize=11)
    ax.text(1.72, 1.86, '镜子', color=GREY, fontsize=10, rotation=45)
    ax.plot([1.5], [2.25], 'o', ms=7, color=NAVY)
    ax.plot([2.25], [1.5], 'o', ms=7, color=ORANGE)
    ax.set_xlim(-0.12, 2.5); ax.set_ylim(-0.12, 2.5)
    ax.set_aspect('equal')
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color(NAVY)
    ax.tick_params(labelsize=9, colors=NAVY)
    ax.set_title('投 1.5 出 2.25；反过来投 2.25 出 1.5', fontsize=10.5, color=NAVY, pad=8)
    save(fig, 'fig-09-square-and-root.png')


# ---------------------------------------------------------------- 10
def fig10():
    """第一条路：让投进去的数排成一队奔向 c，看吐出来的那队奔向哪。"""
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    t = np.linspace(0, 2.6, 300)
    axes(ax, 2.9, 7.4)
    ax.plot(t, t ** 2, color=NAVY, lw=2.2, zorder=3)
    c = 1.6
    pts = [c - 1.0, c - 0.6, c - 0.36, c - 0.2, c - 0.1]
    ax.plot([c, c], [0, c ** 2], color=GREY, lw=1.0, ls=':')
    ax.plot([0, c], [c ** 2, c ** 2], color=GREY, lw=1.0, ls=':')
    for v in pts:
        ax.plot([v], [0], 'o', ms=6, color=ORANGE, zorder=4)
        ax.plot([0], [v ** 2], 'o', ms=6, color=GREEN, zorder=4)
        ax.plot([v, v], [0, v ** 2], color=GREY, lw=0.7, ls=':')
        ax.plot([0, v], [v ** 2, v ** 2], color=GREY, lw=0.7, ls=':')
    ax.plot([c], [0], 'o', ms=9, mfc='white', mec=ORANGE, mew=2, zorder=5)
    ax.plot([0], [c ** 2], 'o', ms=9, mfc='white', mec=GREEN, mew=2, zorder=5)
    ax.text(c, -0.45, r'$c$', ha='center', va='top', fontsize=13, color=ORANGE)
    ax.text(-0.12, c ** 2, r'$L$', ha='right', va='center', fontsize=13, color=GREEN)
    ax.text(0.30, 6.6, '投进去的排成一队，挤向 c', fontsize=10.5, color=ORANGE)
    ax.text(0.30, 6.0, '吐出来的那一队，就挤向 L', fontsize=10.5, color=GREEN)
    save(fig, 'fig-10-sequence-to-function.png')


# ---------------------------------------------------------------- 11
def fig11():
    """第二条路：妹妹画出口的带，姐姐回答入口的带。"""
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    t = np.linspace(0, 2.6, 300)
    axes(ax, 2.9, 7.4)
    c = 1.5
    L = c ** 2
    eps, dlt = 1.05, 0.34
    ax.axhspan(L - eps, L + eps, xmin=0.04, color=BAND, zorder=0)
    ax.axvspan(c - dlt, c + dlt, ymin=0.03, color=LIGHT, zorder=1)
    ax.plot(t, t ** 2, color=NAVY, lw=2.2, zorder=3)
    ax.plot([c], [L], 'o', ms=8, color=NAVY, zorder=5)
    ax.text(2.62, L, r'$L$', fontsize=12, color=GREEN, va='center')
    ax.text(2.62, L + eps, r'$L+\varepsilon$', fontsize=10, color=ORANGE, va='center')
    ax.text(2.62, L - eps, r'$L-\varepsilon$', fontsize=10, color=ORANGE, va='center')
    ax.text(c, -0.45, r'$c$', ha='center', va='top', fontsize=13, color=NAVY)
    ax.text(c - dlt, -0.45, r'$c-\delta$', ha='center', va='top', fontsize=9.5, color=NAVY)
    ax.text(c + dlt, -0.45, r'$c+\delta$', ha='center', va='top', fontsize=9.5, color=NAVY)
    # 纵轴说明占着左上角（axes() 放的），说明文字必须往下让 —— 这个坑踩过三次了
    ax.text(0.06, 6.2, '妹妹先画横的那条带（出口）', fontsize=10.5, color=ORANGE)
    ax.text(0.06, 5.6, '姐姐回答竖的那条带（入口）', fontsize=10.5, color=NAVY)
    ax.text(0.06, 5.0, '竖带里的点，出来都落在横带里', fontsize=10.5, color=GREEN)
    save(fig, 'fig-11-epsilon-delta.png')


# ---------------------------------------------------------------- 12
def fig12():
    """会跳的机器：左右两边奔向不同的数，极限不存在。"""
    fig, ax = plt.subplots(figsize=(5.6, 2.9))
    axes(ax, 2.6, 2.3, ylabel='吐出来的数')
    ax.plot([0.05, 1.5], [0.5, 0.5], color=NAVY, lw=2.6)
    ax.plot([1.5, 2.4], [1.6, 1.6], color=NAVY, lw=2.6)
    ax.plot([1.5], [0.5], 'o', ms=8, mfc='white', mec=NAVY, mew=2, zorder=5)
    ax.plot([1.5], [1.6], 'o', ms=8, color=NAVY, zorder=5)
    ax.plot([1.5, 1.5], [0.5, 1.6], color=GREY, lw=1.0, ls=':')
    ax.text(1.5, -0.16, r'$c$', ha='center', va='top', fontsize=13, color=NAVY)
    ax.text(0.55, 0.72, '左边一直奔向这里', fontsize=10, color=NAVY)
    ax.text(1.62, 1.82, '右边一直奔向那里', fontsize=10, color=NAVY)
    ax.text(0.06, 2.15, '两边不一样 —— 在 c 处没有极限', fontsize=11, color=ORANGE)
    save(fig, 'fig-12-jump.png')


def axes_signed(ax, xmin, xmax, ymin, ymax):
    """两边都有负值时的坐标轴：横轴纵轴都穿过原点。
    注意：这个助手**不写**纵轴说明，所以左上角是空的，正文标签可以放那儿。"""
    ax.annotate('', xy=(xmax, 0), xytext=(xmin, 0),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.4))
    ax.annotate('', xy=(0, ymax), xytext=(0, ymin),
                arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.4))
    dx, dy = xmax - xmin, ymax - ymin
    ax.set_xlim(xmin - 0.05 * dx, xmax + 0.05 * dx)
    ax.set_ylim(ymin - 0.08 * dy, ymax + 0.08 * dy)
    ax.axis('off')


CUBIC = lambda x: x ** 3 - 3 * x


# ---------------------------------------------------------------- 13
def fig13():
    """一点的 f′ 管不住一整段。"""
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    axes_signed(ax, -2.35, 2.35, -3.6, 3.4)
    t = np.linspace(-2.13, 2.13, 400)
    for m, col in (((t <= -1), GREEN), ((t >= -1) & (t <= 1), ORANGE), ((t >= 1), GREEN)):
        ax.plot(t[m], CUBIC(t[m]), color=col, lw=2.4, zorder=3)
    a0, k = -2.0, 9.0
    y0 = CUBIC(a0)
    u = np.linspace(a0 - 0.15, a0 + 0.15, 10)
    ax.plot(u, y0 + k * (u - a0), color=NAVY, lw=2.0, zorder=4)
    ax.plot([a0], [y0], 'o', ms=8, color=NAVY, zorder=5)
    ax.text(-2.25, 2.9, '左边这一点：切线朝上，', fontsize=10.5, color=NAVY, ha='left')
    ax.text(-2.25, 2.35, 'f′ 是正的', fontsize=10.5, color=NAVY, ha='left')
    ax.annotate('', xy=(a0 - 0.02, y0 + 0.55), xytext=(-1.9, 2.05),
                arrowprops=dict(arrowstyle='->', color=NAVY, lw=1.2))
    ax.plot([-1, 1], [-3.35, -3.35], color=ORANGE, lw=2.6, solid_capstyle='butt')
    for v in (-1, 1):
        ax.plot([v, v], [-3.45, -3.25], color=ORANGE, lw=2.0)
    ax.text(0, -3.15, '可这一整段在跌', ha='center', va='bottom',
            fontsize=10.5, color=ORANGE)
    save(fig, 'fig-13-one-point-not-enough.png')


# ---------------------------------------------------------------- 14
def fig14():
    """砍一半：每次留下坏的那一半，段子越套越短。"""
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    lo, hi = 0.0, 8.0
    keep_right = (True, False, True, False)
    tags = ('一开始的整段', '第一次砍：留右半', '第二次砍：留左半',
            '第三次砍：留右半', '第四次砍：留左半')
    ax.set_xlim(-0.7, 11.6)
    ax.set_ylim(-4.9, 0.9)
    ax.axis('off')
    for i in range(5):
        y = -i
        if i:
            mid = (lo + hi) / 2
            drop = (lo, mid) if keep_right[i - 1] else (mid, hi)
            ax.plot(drop, [y, y], color=GREY, lw=3.0, alpha=0.45,
                    solid_capstyle='butt')
            lo, hi = (mid, hi) if keep_right[i - 1] else (lo, mid)
        ax.plot([lo, hi], [y, y], color=ORANGE, lw=5.0, solid_capstyle='butt')
        for v in (lo, hi):
            ax.plot([v, v], [y - 0.17, y + 0.17], color=NAVY, lw=1.4)
        ax.text(8.55, y, tags[i], fontsize=10, color=NAVY, va='center')
    p = (lo + hi) / 2
    ax.plot([p, p], [-4.55, 0.55], color=NAVY, lw=1.1, ls=':', zorder=1)
    ax.plot([p], [-4.0], 'o', ms=7, color=NAVY, zorder=5)
    ax.text(p, -4.72, '所有段子都套住的那一个点', ha='center', va='top',
            fontsize=10.5, color=NAVY)
    ax.text(-0.55, 0.62, '灰色是砍掉的一半，橙色是留下的那一半',
            fontsize=10, color=GREY, ha='left')
    save(fig, 'fig-14-halving-max.png')


# ---------------------------------------------------------------- 15
def fig15():
    """顶上是平的：两边的平均变化率把 f′ 夹成 0。"""
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    g = lambda x: 3.0 - (x - 2.0) ** 2
    axes_signed(ax, 0.0, 4.1, 0.0, 3.9)
    t = np.linspace(0.35, 3.65, 300)
    ax.plot(t, g(t), color=NAVY, lw=2.4, zorder=3)
    ax.plot([1.35, 2.65], [3.0, 3.0], color=GREEN, lw=2.2, ls='--', zorder=4)
    ax.plot([2.0], [3.0], 'o', ms=9, color=GREEN, zorder=5)
    for x1, col in ((1.0, ORANGE), (3.0, ORANGE)):
        ax.plot([x1, 2.0], [g(x1), 3.0], color=col, lw=1.8, zorder=4)
        ax.plot([x1], [g(x1)], 'o', ms=7, color=col, zorder=5)
    # 说明一律放到横轴下面 —— 放在曲线两侧会被下坠的曲线压住
    ax.text(1.0, -0.28, '左边爬上来：\n平均变化率不是负的', ha='center', va='top',
            fontsize=10.5, color=ORANGE, linespacing=1.7)
    ax.text(3.0, -0.28, '右边掉下去：\n平均变化率不是正的', ha='center', va='top',
            fontsize=10.5, color=ORANGE, linespacing=1.7)
    ax.text(2.0, 3.45, '顶上：只能是 0', ha='center', fontsize=11, color=GREEN)
    ax.set_ylim(-1.75, 4.1)
    save(fig, 'fig-15-fermat.png')


# ---------------------------------------------------------------- 16
def fig16():
    """左：罗尔。右：把割线减掉，就回到罗尔。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.1))
    b, c = 0.5, 3.5
    base = lambda x: 3.0 - (x - 2.0) ** 2
    t = np.linspace(b, c, 300)
    for ax, tilt, tag in zip(axs, (0.0, 1.1),
                             ('两头一样高：中间必有一处是平的',
                              '两头不一样高：中间必有一处和割线一样陡')):
        f = lambda x: base(x) + tilt * (x - b)
        axes_signed(ax, 0.0, 4.0, 0.0, 5.6)
        ax.plot(t, f(t), color=NAVY, lw=2.3, zorder=3)
        ax.plot([b, c], [f(b), f(c)], color=ORANGE, lw=1.8, ls='--', zorder=2)
        for v in (b, c):
            ax.plot([v], [f(v)], 'o', ms=6.5, color=ORANGE, zorder=5)
        ax.plot([2.0], [f(2.0)], 'o', ms=8.5, color=GREEN, zorder=5)
        u = np.array([1.35, 2.65])
        ax.plot(u, f(2.0) + tilt * (u - 2.0), color=GREEN, lw=2.2, zorder=4)
        ax.text(2.0, -0.55, tag, ha='center', va='top', fontsize=10, color=NAVY)
        ax.set_ylim(-1.7, 6.0)
    axs[0].text(0.15, 5.3, '割线是平的', fontsize=10, color=ORANGE)
    axs[1].text(0.15, 5.3, '割线是斜的', fontsize=10, color=ORANGE)
    save(fig, 'fig-16-rolle-mvt.png')


# ---------------------------------------------------------------- 17
def fig17():
    """两头都要不是摆设：去掉一头，最高点就没了。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.0))
    t = np.linspace(0, 1, 100)
    for ax, closed, tag in zip(axs, (False, True),
                               ('两头都不要：够不着那条线',
                                '两头都要：最高点就站在这里')):
        axes_signed(ax, 0.0, 1.35, 0.0, 1.35)
        ax.plot([0, 1], [1.0, 1.0], color=GREY, lw=1.2, ls=':')
        ax.plot(t, t, color=NAVY, lw=2.4, zorder=3)
        # 空心＝这一头不要，实心＝这一头也要。两头必须一致，否则和正文的
        # "两头都要 / 两头都不要"对不上。
        if closed:
            ax.plot([1.0], [1.0], 'o', ms=9, color=GREEN, zorder=5)
            ax.plot([0.0], [0.0], 'o', ms=7, color=NAVY, zorder=5)
        else:
            ax.plot([1.0], [1.0], 'o', ms=9, color=ORANGE, zorder=5,
                    mfc='white', mew=2.0)
            ax.plot([0.0], [0.0], 'o', ms=7, color=NAVY, zorder=5,
                    mfc='white', mew=1.6)
        ax.text(0.68, -0.16, tag, ha='center', va='top', fontsize=10,
                color=(GREEN if closed else ORANGE))
        ax.set_ylim(-0.52, 1.45)
    save(fig, 'fig-17-open-end.png')


# ---------------------------------------------------------------- 18
def fig18():
    """碗形与拱形：切线全在下面 / 全在上面。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.1))
    t = np.linspace(-1.55, 1.55, 300)
    for ax, s, tag in zip(axs, (1.0, -1.0),
                          ('碗形：切线全躺在画像下面',
                           '拱形：切线全压在画像上面')):
        # 顶点必须离开横轴：顶点落在原点时，中间那条切线正好和横轴重合，被轴吃掉。
        off = -1.6 * s
        g = lambda x: s * x ** 2 + off
        axes_signed(ax, -1.8, 1.8, -2.6, 2.6)
        ax.plot(t, g(t), color=NAVY, lw=2.4, zorder=3)
        for a0 in (-1.1, 0.0, 1.1):
            u = np.array([a0 - 0.62, a0 + 0.62])
            ax.plot(u, g(a0) + s * 2 * a0 * (u - a0),
                    color=ORANGE, lw=1.6, zorder=2)
            ax.plot([a0], [g(a0)], 'o', ms=5.5, color=ORANGE, zorder=5)
        ax.text(0.0, -3.0, tag, ha='center', va='top', fontsize=10.5, color=NAVY)
        ax.set_ylim(-3.9, 2.9)
    save(fig, 'fig-18-concave.png')


# ---------------------------------------------------------------- 19
def fig19():
    """三张图对齐：机器、它的导函数、导函数的导函数。"""
    fig, axs = plt.subplots(3, 1, figsize=(5.8, 5.6))
    t = np.linspace(-2.05, 2.05, 400)
    funcs = ((CUBIC, '机器', 3.4), (lambda x: 3 * x ** 2 - 3, '它的导函数', 9.5),
             (lambda x: 6 * x, '导函数的导函数', 12.5))
    for ax, (fn, name, ylim) in zip(axs, funcs):
        axes_signed(ax, -2.2, 2.2, -ylim, ylim)
        ax.plot(t, fn(t), color=NAVY, lw=2.2, zorder=3)
        for v in (-1.0, 0.0, 1.0):
            ax.plot([v, v], [-ylim, ylim], color=GREY, lw=0.9, ls=':', zorder=1)
            if abs(fn(v)) < 1e-9:
                ax.plot([v], [0.0], 'o', ms=7, color=ORANGE, zorder=5)
        ax.text(2.3, 0.0, name, fontsize=11, color=NAVY, va='center')
        ax.set_xlim(-2.45, 3.35)
    axs[0].plot([-1.0, 1.0], [2.0, -2.0], 'o', ms=7, color=GREEN, zorder=6, ls='none')
    axs[0].plot([0.0], [0.0], 'o', ms=7, color=ORANGE, zorder=6)
    # 两行分开写会贴在一起（纵向单位不同，靠眼估必翻车）——用 \n ＋ linespacing
    axs[1].text(2.3, -5.2, '它为 0 的地方，\n上面正好是顶和谷',
                fontsize=9.5, color=GREY, va='top', linespacing=1.9)
    axs[2].text(2.3, -6.4, '它变号的地方，\n上面正好是拐点',
                fontsize=9.5, color=GREY, va='top', linespacing=1.9)
    save(fig, 'fig-19-f-fp-fpp.png')


# ---------------------------------------------------------------- 20
def fig20():
    """把形状描出来：顶、拐点、谷，以及每一段的涨跌与碗拱。"""
    fig, ax = plt.subplots(figsize=(6.2, 3.9))
    axes_signed(ax, -2.2, 2.2, -3.6, 3.4)
    t = np.linspace(-2.13, 2.13, 400)
    for m, col in (((t <= -1), GREEN), ((t >= -1) & (t <= 1), ORANGE), ((t >= 1), GREEN)):
        ax.plot(t[m], CUBIC(t[m]), color=col, lw=2.6, zorder=3)
    # 拐点的标签往右挪：正落在原点上方会贴住下坠的曲线
    marks = ((-1.0, 2.0, '顶', GREEN, 0.0, 0.42), (0.0, 0.0, '拐点', NAVY, 0.30, 0.34),
             (1.0, -2.0, '谷', GREEN, 0.0, -0.78))
    for x0, y0, lab, col, dx, dy in marks:
        ax.plot([x0], [y0], 'o', ms=9, color=col, zorder=6)
        ax.text(x0 + dx, y0 + dy, lab, ha='center', fontsize=11, color=col)
    ax.plot([-1.42, -0.58], [2.0, 2.0], color=GREY, lw=1.3, ls='--', zorder=2)
    ax.plot([0.58, 1.42], [-2.0, -2.0], color=GREY, lw=1.3, ls='--', zorder=2)
    ax.text(-1.15, -3.35, '左半边：拱形', ha='center', fontsize=10.5, color=NAVY)
    ax.text(1.15, -3.35, '右半边：碗形', ha='center', fontsize=10.5, color=NAVY)
    ax.text(-2.15, 3.05, '绿色在涨，橙色在跌', fontsize=10, color=GREY, ha='left')
    save(fig, 'fig-20-shape-cubic.png')

# ---------------------------------------------------------------- 21
def fig21():
    """放大镜：同一段抛物线，越放越大，看着越直。"""
    fig, axs = plt.subplots(1, 3, figsize=(6.4, 2.5))
    windows = ((1.0, '原来的样子'), (0.35, '放大三倍'), (0.12, '再放大三倍'))
    for i, (ax, (w, label)) in enumerate(zip(axs, windows)):
        t = np.linspace(1 - w, 1 + w, 300)
        y = t ** 2
        y0, y1 = y.min(), y.max()
        pad_x, pad_y = 0.06 * 2 * w, 0.08 * (y1 - y0)
        ax.plot(t, y, color=NAVY, lw=2.2, zorder=3)
        ax.plot([1], [1], 'o', ms=7, color=ORANGE, zorder=4)
        ax.set_xlim(1 - w - pad_x, 1 + w + pad_x)
        ax.set_ylim(y0 - pad_y, y1 + pad_y)
        ax.axis('off')
        ax.add_patch(Rectangle((1 - w - pad_x, y0 - pad_y),
                               2 * (w + pad_x), (y1 - y0) + 2 * pad_y,
                               fill=False, edgecolor=GREY, lw=1.2, zorder=2))
        # 在前一格里用虚线框出下一格看的范围
        if i < 2:
            nw = windows[i + 1][0]
            ny = np.linspace(1 - nw, 1 + nw, 50) ** 2
            ax.add_patch(Rectangle((1 - nw, ny.min()), 2 * nw, ny.max() - ny.min(),
                                   fill=False, edgecolor=ORANGE, ls='--', lw=1.1,
                                   zorder=2))
        ax.text(0.5, -0.11, label, transform=ax.transAxes,
                ha='center', fontsize=10.5, color=NAVY)
    save(fig, 'fig-21-zoom.png')


# ---------------------------------------------------------------- 22
def fig22():
    """牛顿法：画切线，滑到横轴，回到曲线再来一遍。"""
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    axes_signed(ax, 0.0, 2.5, -2.4, 3.0)
    t = np.linspace(0.15, 2.25, 300)
    ax.plot(t, t ** 2 - 2, color=NAVY, lw=2.4, zorder=3)
    # 第一步：站在 a1 = 2（先画出它在横轴上的落脚点），切线滑到 1.5
    ax.plot([2, 2], [0, 2], color=GREY, lw=1.2, ls='--', zorder=2)
    ax.plot([2], [0], 'o', ms=5, color=NAVY, zorder=5)
    ax.plot([2], [2], 'o', ms=7, color=NAVY, zorder=5)
    ax.annotate('', xy=(1.5, 0), xytext=(2.16, 2.64),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.0), zorder=4)
    ax.plot([1.5], [0], 'o', ms=7, color=ORANGE, zorder=5)
    # 回到曲线，第二条切线（虚线箭头），滑到 1.4167
    ax.plot([1.5, 1.5], [0, 0.25], color=GREY, lw=1.2, ls='--', zorder=2)
    ax.plot([1.5], [0.25], 'o', ms=6, color=NAVY, zorder=5)
    ax.annotate('', xy=(1.4167, 0), xytext=(1.72, 0.91),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=1.7,
                                linestyle='--'), zorder=4)
    # 目标：√2 所在的穿轴点
    ax.plot([np.sqrt(2)], [0], 'o', ms=8, color=GREEN, zorder=4)
    ax.text(1.26, -0.62, r'$\sqrt{2}$', ha='center', fontsize=12, color=GREEN)
    ax.text(2.0, -0.62, r'$a_1$', ha='center', fontsize=12, color=NAVY)
    ax.text(1.56, -0.62, r'$a_2$', ha='center', fontsize=12, color=ORANGE)
    ax.text(0.10, 2.72, '画切线，滑到横轴；', fontsize=10.5, color=NAVY, ha='left')
    ax.text(0.10, 2.28, '回到曲线，再来一遍', fontsize=10.5, color=NAVY, ha='left')
    save(fig, 'fig-22-newton-slide.png')


# ---------------------------------------------------------------- 23
def fig23():
    """牛顿法翻车：站在谷底，切线平躺，够不到横轴。"""
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    axes_signed(ax, -2.3, 2.3, -3.6, 3.4)
    t = np.linspace(-2.13, 2.13, 400)
    ax.plot(t, CUBIC(t), color=NAVY, lw=2.4, zorder=3)
    for r in (-np.sqrt(3), 0.0, np.sqrt(3)):
        ax.plot([r], [0], 'o', ms=7, color=GREEN, zorder=4)
    ax.text(-2.2, 3.0, '要找的是穿轴的绿点', fontsize=10.5, color=GREEN, ha='left')
    ax.plot([-0.15, 2.2], [-2, -2], color=ORANGE, lw=2.2, zorder=4)
    ax.plot([1], [-2], 'o', ms=8, color=ORANGE, zorder=5)
    ax.text(2.2, -2.55, '谷底的切线平躺，永远碰不到横轴', fontsize=10.5,
            color=ORANGE, ha='right')
    save(fig, 'fig-23-flat-tangent.png')


# ---------------------------------------------------------------- 24
def fig24():
    """曲顶小条不成正比；拍平成长方形才成正比。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 3.0))
    for i, ax in enumerate(axs):
        t = np.linspace(0, 2.1, 300)
        axes(ax, 2.3, 5.0, '', '')
        ax.plot(t, t ** 2, color=NAVY, lw=2.2, zorder=3)
        if i == 0:
            seg = np.linspace(1, 1.6, 60)
            ax.fill_between(seg, 0, seg ** 2, color=BAND, zorder=2)
            ax.plot(seg, seg ** 2, color=ORANGE, lw=2.6, zorder=4)
            ax.plot([1, 1], [0, 1], color=ORANGE, lw=1.2, zorder=2)
            ax.plot([1.6, 1.6], [0, 2.56], color=ORANGE, lw=1.2, zorder=2)
            ax.text(0.5, -0.13, '曲顶的小条：不成正比', transform=ax.transAxes,
                    ha='center', fontsize=10.5, color=ORANGE)
        else:
            ax.add_patch(Rectangle((1, 0), 0.6, 1, facecolor='#DCEEE3',
                                   edgecolor=GREEN, lw=1.4, zorder=2))
            ax.plot([1, 1.6], [1, 1], color=GREEN, lw=2.6, zorder=4)
            ax.text(0.5, -0.13, '拍平以后：面积恰好和宽成正比',
                    transform=ax.transAxes, ha='center', fontsize=10.5, color=GREEN)
    save(fig, 'fig-24-strip-flatten.png')


# ---------------------------------------------------------------- 25
def fig25():
    """芝诺：两张照片一模一样，单看一瞬说不出快。"""
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    ax.set_xlim(-0.2, 9.4)
    ax.set_ylim(-0.9, 3.4)
    ax.axis('off')
    for x0, label in ((0.0, '这支正在飞'), (5.2, '这支挂在墙上')):
        ax.add_patch(Rectangle((x0, 0), 4, 3, fill=False, edgecolor=GREY, lw=1.6))
        if x0 > 4:                       # 墙上那支：一枚钉子和一根细线
            ax.plot([x0 + 2, x0 + 2], [1.5, 2.85], color=GREY, lw=1.0)
            ax.plot([x0 + 2], [2.85], 'o', ms=4, color=GREY)
        ax.annotate('', xy=(x0 + 3.4, 1.5), xytext=(x0 + 0.8, 1.5),
                    arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=2.4))
        for d in (0.0, 0.22, 0.44):      # 尾羽
            ax.plot([x0 + 0.62 + d, x0 + 0.86 + d], [1.82, 1.5], color=NAVY, lw=1.6)
            ax.plot([x0 + 0.62 + d, x0 + 0.86 + d], [1.18, 1.5], color=NAVY, lw=1.6)
        ax.text(x0 + 2, -0.55, label, ha='center', fontsize=11, color=NAVY)
    save(fig, 'fig-25-arrow-photo.png')


# ---------------------------------------------------------------- 26
def fig26():
    """抛球：上为高度机器（顶在 1 秒），下为速度机器（1 秒处穿轴）。"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.2, 5.4))
    # 上：高度
    axes(ax1, 2.3, 5.8, '时刻（秒）', '高多少米')
    t = np.linspace(0, 2, 300)
    ax1.plot(t, 10 * t - 5 * t ** 2, color=NAVY, lw=2.4, zorder=3)
    ax1.plot([1, 1], [0, 5], color=GREY, lw=1.2, ls='--', zorder=2)
    ax1.plot([1], [5], 'o', ms=8, color=ORANGE, zorder=4)
    ax1.text(1.42, 4.55, '顶：第 1 秒末，高 5 米', fontsize=10.5, color=ORANGE)
    for v in (1, 2):
        ax1.text(v, -0.55, str(v), ha='center', fontsize=9.5, color=GREY)
    # 下：速度
    axes_signed(ax2, -0.26, 2.33, -11, 11)
    ax2.plot([0, 2], [10, -10], color=GREEN, lw=2.4, zorder=3)
    ax2.plot([1, 1], [0, 10], color=GREY, lw=1.2, ls='--', zorder=2)
    ax2.plot([1], [0], 'o', ms=8, color=ORANGE, zorder=4)
    ax2.text(-0.24, 10.4, '速度（米每秒）', fontsize=10, color=NAVY, ha='left')
    ax2.text(1.1, 1.6, '正好在这里指 0，正要掉头', fontsize=10.5, color=ORANGE)
    ax2.text(0.90, -2.0, '1', ha='right', fontsize=9.5, color=GREY)
    ax2.text(2.0, -2.0, '2', ha='center', fontsize=9.5, color=GREY)
    save(fig, 'fig-26-throw.png')


# ---------------------------------------------------------------- 27
def fig27():
    """刹车：底和高各翻一倍，三角形面积翻四倍。"""
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    axes(ax, 4.6, 44, '刹车后的秒数', '速度（米每秒）')
    ax.fill_between([0, 4], [40, 0], 0, color=LIGHT, zorder=2)
    ax.plot([0, 4], [40, 0], color=NAVY, lw=2.4, zorder=4)
    ax.fill_between([0, 2], [20, 0], 0, color=BAND, zorder=3)
    ax.plot([0, 2], [20, 0], color=ORANGE, lw=2.4, zorder=4)
    for y in (20, 40):
        ax.text(-0.14, y, str(y), ha='right', va='center', fontsize=9.5, color=NAVY)
    ax.text(0.62, 5.6, '20 米', fontsize=11, color=ORANGE, ha='center')
    ax.text(2.45, 10.5, '一共冲出 80 米', fontsize=11, color=NAVY, ha='left')
    ax.text(0.13, 29.0, '起步快一倍', fontsize=10.5, color=NAVY, ha='left')
    for v in (2, 4):
        ax.text(v, -4.2, str(v), ha='center', fontsize=9.5, color=GREY)
    save(fig, 'fig-27-brake.png')


# ---------------------------------------------------------------- 28
def fig28():
    """方尖塔切薄板：切面边长跟深度走，面积跟深度的平方走。"""
    fig, ax = plt.subplots(figsize=(6.2, 3.5))
    ax.set_xlim(-3.5, 3.4)
    ax.set_ylim(-0.6, 4.7)
    ax.axis('off')
    n, H = 6, 4.0
    for k in range(1, n + 1):
        d = k * H / n
        color = BAND if k == 4 else LIGHT
        edge = ORANGE if k == 4 else NAVY
        ax.add_patch(Rectangle((-d / 2, H - d), d, H / n,
                               facecolor=color, edgecolor=edge, lw=1.0, zorder=2))
    ax.plot([-2, 0, 2], [0, H, 0], color=NAVY, lw=2.2, zorder=3)
    ax.plot([-2, 2], [0, 0], color=NAVY, lw=2.2, zorder=3)
    ax.annotate('', xy=(-2.6, H - 8 / 3), xytext=(-2.6, H),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=1.4))
    ax.text(-2.75, 3.25, '从尖往下量深度', fontsize=10, color=ORANGE,
            ha='right')
    ax.plot([-2.6, -4 / 3], [4 - 8 / 3, 4 - 8 / 3], color=GREY, lw=1.0, ls='--',
            zorder=1)
    ax.text(0.85, 3.85, '切面边长跟深度走，\n切面面积就跟深度的平方走',
            fontsize=10, color=NAVY, ha='left', linespacing=1.6)
    save(fig, 'fig-28-pyramid.png')



# ---------------------------------------------------------------- 29
def fig29():
    """速度表：量的一小段越短，平均速度越挤向针指的那个数。"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.8, 3.2),
                                   gridspec_kw={'width_ratios': [1.0, 1.15]})
    # 左：表盘。刻度 0..25，针指 12
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.set_xlim(-1.42, 1.42)
    ax1.set_ylim(-0.62, 1.50)
    th = np.linspace(np.pi, 0, 200)
    ax1.plot(np.cos(th), np.sin(th), color=NAVY, lw=2.2)
    for v in range(0, 26, 5):
        a = np.pi * (1 - v / 25.0)
        ax1.plot([0.86 * np.cos(a), np.cos(a)], [0.86 * np.sin(a), np.sin(a)],
                 color=NAVY, lw=1.6)
        # 刻度数字放到表盘**外面**：放里面会被指针扫到（这类叠字踩过多次）
        ax1.text(1.16 * np.cos(a), 1.16 * np.sin(a), str(v),
                 ha='center', va='center', fontsize=9, color=GREY)
    a12 = np.pi * (1 - 12 / 25.0)
    ax1.annotate('', xy=(0.80 * np.cos(a12), 0.80 * np.sin(a12)), xytext=(0, 0),
                 arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=3.0,
                                 mutation_scale=18))
    ax1.plot([0], [0], 'o', ms=7, color=ORANGE)
    ax1.text(0, -0.34, '此刻：每秒 12 米', ha='center', fontsize=10.5, color=ORANGE)
    ax1.text(0, 1.48, '仪表盘', ha='center', fontsize=10.5, color=NAVY)
    # 右：四次测量，越缩越挤向 12
    vals = [14.0, 12.2, 12.02, 12.002]
    labs = ['1 秒', '0.1 秒', '0.01 秒', '0.001 秒']
    xs = list(range(1, 5))
    ax2.axhline(12, color=ORANGE, lw=1.6, ls='--', zorder=2)
    ax2.plot(xs, vals, '-o', color=NAVY, lw=1.8, ms=7, zorder=3)
    for x0, v, lb in zip(xs, vals, labs):
        ax2.text(x0, v + 0.16, ('%g' % v), ha='center', fontsize=10, color=NAVY)
        ax2.text(x0, 11.62, lb, ha='center', fontsize=9.5, color=GREY)
    ax2.text(0.52, 12.13, '12', ha='left', va='bottom', fontsize=11, color=ORANGE)
    ax2.text(2.5, 11.42, '量的那一小段有多长', ha='center', fontsize=10, color=GREY)
    ax2.text(4.62, 13.95, '算出来的\n平均速度', fontsize=10.5, color=NAVY, ha='right',
             linespacing=1.5)
    ax2.set_xlim(0.45, 4.75)
    ax2.set_ylim(11.3, 14.35)
    ax2.axis('off')
    save(fig, 'fig-29-speedometer.png')



# ---------------------------------------------------------------- 30
def fig30():
    """竖线检验：守诺言的画像，一条竖线只碰一次。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 3.0))
    # 左：正经机器 a^2
    ax = axs[0]
    axes(ax, 2.6, 5.2, '', '')
    t = np.linspace(0, 2.25, 300)
    ax.plot(t, t ** 2, color=NAVY, lw=2.4, zorder=3)
    ax.plot([1.5, 1.5], [0, 4.6], color=GREY, lw=1.6, ls='--', zorder=2)
    ax.plot([1.5], [2.25], 'o', ms=9, color=GREEN, zorder=5)
    ax.text(1.66, 2.05, '只碰到一个点', fontsize=10.5, color=GREEN, ha='left')
    ax.text(0.5, -0.62, '守诺言：这是机器的画像', transform=ax.transData,
            fontsize=10.5, color=NAVY, ha='left')
    # 右：躺倒的抛物线（面积→边长，没挑）
    ax = axs[1]
    axes(ax, 2.6, 5.2, '', '')
    y = np.linspace(-2.1, 2.1, 300)
    ax.plot(y ** 2 * 0.5, y + 2.4, color=NAVY, lw=2.4, zorder=3)
    ax.plot([1.5, 1.5], [0, 4.6], color=GREY, lw=1.6, ls='--', zorder=2)
    for yy in (2.4 + np.sqrt(3.0), 2.4 - np.sqrt(3.0)):
        ax.plot([1.5], [yy], 'o', ms=9, color=ORANGE, zorder=5)
    ax.text(1.66, 4.15, '同一个数', fontsize=10.5, color=ORANGE, ha='left')
    ax.text(1.66, 0.52, '两个答案', fontsize=10.5, color=ORANGE, ha='left')
    ax.text(0.5, -0.62, '变卦了：这不是机器的画像', transform=ax.transData,
            fontsize=10.5, color=ORANGE, ha='left')
    save(fig, 'fig-30-promise.png')


def fig31():
    """微分的几何意义：左＝一点上按切线走（真变化＝微分＋零头）；右＝整条曲线用小切线段顶替。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.1))
    # 左：站在 a ＝ 1，挪 h ＝ 0.9（f ＝ a^2，切线陡度 2）
    ax = axs[0]
    axes(ax, 2.45, 4.7, '', '')
    a, h = 1.0, 0.9
    t = np.linspace(0, 2.15, 300)
    ax.plot(t, t ** 2, color=NAVY, lw=2.2, zorder=3)
    u = np.linspace(0.35, 2.1, 10)
    ax.plot(u, a ** 2 + 2 * a * (u - a), color=GREEN, lw=1.8, zorder=2)
    y0, y_tan, y_true = a ** 2, a ** 2 + 2 * a * h, (a + h) ** 2
    # 数值与几何都钉死：微分＝2h、零头＝h^2、真变化＝两者之和
    assert abs(y_tan - y0 - 2 * h) < 1e-12 and abs(y_true - y_tan - h * h) < 1e-12
    ax.plot([a, a + h], [y0, y0], color=GREY, lw=1.3, zorder=2)
    ax.plot([a], [y0], 'o', ms=7, color=ORANGE, zorder=5)
    ax.plot([a + h, a + h], [y0, y_tan], color=GREEN, lw=3.4, zorder=4,
            solid_capstyle='butt')
    ax.plot([a + h, a + h], [y_tan, y_true], color=ORANGE, lw=3.4, zorder=4,
            solid_capstyle='butt')
    ax.plot([a + h], [y_true], 'o', ms=6, color=NAVY, zorder=5)
    ax.text(a + h / 2, y0 - 0.16, '挪动 h', ha='center', va='top',
            fontsize=10, color=NAVY)
    ax.text(a + h + 0.07, (y0 + y_tan) / 2, '微分：按切线走，\n升的这一段',
            ha='left', va='center', fontsize=9.5, color=GREEN, linespacing=1.3)
    ax.text(a + h + 0.07, (y_tan + y_true) / 2, '零头', ha='left', va='center',
            fontsize=9.5, color=ORANGE)
    ax.text(0.42, 3.95, '爬曲线，升的是一整段：', fontsize=9.5, color=NAVY)
    ax.text(0.42, 3.55, '微分＋零头', fontsize=9.5, color=NAVY)
    ax.text(0.30, -0.60, '切线', fontsize=9.5, color=GREEN, ha='left')
    # 右：整条曲线切成小段，每段用自己的小切线段顶替
    ax = axs[1]
    axes(ax, 2.45, 4.7, '', '')
    ax.plot(t, t ** 2, color=GREY, lw=2.6, zorder=2)
    n = 5
    xs = np.linspace(0.1, 2.0, n + 1)
    for i in range(n):
        lo, hi = xs[i], xs[i + 1]
        m = (lo + hi) / 2
        ax.plot([lo, hi], [m ** 2 + 2 * m * (lo - m), m ** 2 + 2 * m * (hi - m)],
                color=ORANGE, lw=2.0, zorder=4)
        ax.plot([lo], [m ** 2 + 2 * m * (lo - m)], 'o', ms=3.5, color=ORANGE, zorder=5)
    ax.plot([xs[-1]], [((xs[-2] + xs[-1]) / 2) ** 2 + 2 * ((xs[-2] + xs[-1]) / 2)
            * (xs[-1] - (xs[-2] + xs[-1]) / 2)], 'o', ms=3.5, color=ORANGE, zorder=5)
    ax.text(0.18, 4.15, '每一小段，都用它自己的', fontsize=9.5, color=ORANGE)
    ax.text(0.18, 3.75, '切线小段顶替', fontsize=9.5, color=ORANGE)
    ax.text(0.18, 3.2, '段切得越细，贴得越紧', fontsize=9.5, color=NAVY)
    # 不变量：段数翻倍，折线偏差缩到四分之一（眼睛判构图，这个判几何）
    def polyerr(n):
        xs = np.linspace(0.1, 2.0, n + 1)
        worst = 0.0
        for i in range(n):
            m = (xs[i] + xs[i + 1]) / 2
            tt = np.linspace(xs[i], xs[i + 1], 60)
            worst = max(worst, np.max(np.abs((m ** 2 + 2 * m * (tt - m)) - tt ** 2)))
        return worst
    e5, e10 = polyerr(5), polyerr(10)
    assert e10 < e5 and 0.2 < e10 / e5 < 0.3, (e5, e10)
    save(fig, 'fig-31-tangent-pieces.png')


def fig32():
    """可微性的几何：左＝尖角（切线定不下来）；右＝浑身毛刺的曲线（处处连着、处处是尖）。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.0))
    # 左：绝对值机器的 V 字尖角
    ax = axs[0]
    axes(ax, 2.45, 2.6, '', '')
    c, y0 = 1.2, 0.55
    t1 = np.linspace(0.15, c, 60); t2 = np.linspace(c, 2.3, 60)
    ax.plot(t1, y0 + (c - t1), color=ORANGE, lw=2.4, zorder=3)
    ax.plot(t2, y0 + (t2 - c), color=GREEN, lw=2.4, zorder=3)
    ax.plot([c], [y0], 'o', ms=8, color=NAVY, zorder=5)
    # 尖角两侧陡度 −1 与 ＋1，对不上——这正是"切线定不下来"的几何
    slope_left = ((y0 + (c - t1[0])) - (y0 + (c - t1[-2]))) / (t1[0] - t1[-2])
    slope_right = ((y0 + (t2[-1] - c)) - (y0 + (t2[1] - c))) / (t2[-1] - t2[1])
    assert abs(slope_left + 1) < 1e-9 and abs(slope_right - 1) < 1e-9 and slope_left != slope_right
    ax.text(1.72, 1.30, '右边的陡度', fontsize=9.5, color=GREEN)
    ax.text(0.24, 1.30, '左边的陡度', fontsize=9.5, color=ORANGE)
    ax.text(0.62, 2.28, '尖角上，切线定不下来', fontsize=10, color=NAVY)
    ax.text(0.55, -0.42, '连着，可是在尖角上不可微', fontsize=9.5, color=NAVY)
    # 右：毛刺曲线（魏尔斯特拉斯函数的有限层近亲）
    ax = axs[1]
    axes(ax, 2.45, 2.6, '', '')
    x = np.linspace(0.05, 2.35, 4200)
    def W(layers):
        return sum(0.55 ** k * np.cos(5 ** k * 2.6 * x) for k in range(layers))
    y = W(6)
    y = 1.25 + 0.85 * y / np.max(np.abs(y))
    ax.plot(x, y, color=NAVY, lw=0.9, zorder=3)
    ax.text(0.28, 2.28, '处处连着，处处是毛刺', fontsize=10, color=NAVY)
    ax.text(0.30, -0.42, '放大多少倍，毛刺都不消失', fontsize=9.5, color=NAVY)
    # 不变量：叠的层数越多，最陡处越陡（毛刺越看越尖），3 层到 6 层至少陡 3 倍
    def maxslope(layers):
        yy = W(layers)
        return np.max(np.abs(np.diff(yy) / np.diff(x)))
    assert maxslope(6) > 3 * maxslope(3), (maxslope(3), maxslope(6))
    save(fig, 'fig-32-spikes.png')


def fig33():
    """跨线数陡度（给第十篇灰盒配）：一步跨几条竖线、几条横线，两数一比就是陡度。"""
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    xmax, ymax = 2.35, 4.7
    axes(ax, xmax, ymax, '', '')
    for gx in np.arange(0.0, 2.21, 0.5):
        ax.plot([gx, gx], [0, 4.4], color=LIGHT, lw=1.0, zorder=1)
    for gy in np.arange(0.0, 4.41, 0.5):
        ax.plot([0, 2.2], [gy, gy], color=LIGHT, lw=1.0, zorder=1)
    t = np.linspace(0, 2.08, 300)
    ax.plot(t, t ** 2, color=NAVY, lw=2.2, zorder=3)
    for a, dx in ((0.5, 0.5), (1.55, 0.5)):
        y0, k = a * a, 2 * a
        ax.annotate('', xy=(a + dx, y0 + k * dx), xytext=(a, y0),
                    arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.2), zorder=4)
        # 不变量：同样横跨一格（一条竖线），缓处跨 1 条横线、陡处跨 3 条
        assert int(k * dx / 0.5) in (1, 3), (a, k * dx)
    ax.text(0.18, 1.55, '缓处：跨 1 格，', fontsize=9.5, color=ORANGE)
    ax.text(0.18, 1.15, '过 1 条横线', fontsize=9.5, color=ORANGE)
    ax.text(1.28, 3.95, '陡处：跨 1 格，', fontsize=9.5, color=ORANGE)
    ax.text(1.28, 3.55, '过 3 条横线', fontsize=9.5, color=ORANGE)
    ax.text(0.16, 4.35, '同一步，过的横线越多，坡越陡', fontsize=10, color=NAVY)
    ax.text(0.30, -0.50, '横线数一比竖线数，就是陡度', fontsize=9.5, color=NAVY)
    save(fig, 'fig-33-crossing-lines.png')


if __name__ == '__main__':
    print('generating ->', OUT)
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09,
              fig10, fig11, fig12, fig13, fig14, fig15, fig16, fig17, fig18,
              fig19, fig20, fig21, fig22, fig23, fig24, fig25, fig26, fig27,
              fig28, fig29, fig30, fig31, fig32, fig33):
        f()
    print('done:', len([a for a in os.listdir(OUT) if a.endswith('.png')]), 'figures')
