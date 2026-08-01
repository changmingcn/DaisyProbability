#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《兔子变了，什么没变》插图（样章）。

约定同前两册：中文用 Hiragino Sans GB，数学走 mathtext，两者绝不混在同一个字符串里。
全书吉祥物：RABBIT —— 一张点名单＋按顺序连线。改这里，全书的兔子一起改。
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['Hiragino Sans GB', 'Arial Unicode MS', 'Songti SC']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'dejavusans'

NAVY, ORANGE, GREEN = '#1F3A6E', '#E8743B', '#2E9E6B'
GREY, LIGHT, BAND = '#9AA5B1', '#DCE7F7', '#FBE3D6'

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs')
os.makedirs(OUT, exist_ok=True)

# 兔子点名单（面朝左、坐姿）。按顺序连线，最后一点连回第一点。
RABBIT = [
    (1.5, 0.0),   # 1  左脚
    (2.0, 0.0),   # 2
    (2.5, 0.0),   # 3
    (3.0, 0.0),   # 4  右脚
    (3.5, 0.5),   # 5  右脚外
    (3.5, 1.0),   # 6
    (3.5, 1.5),   # 7
    (4.0, 2.0),   # 8  身右
    (4.0, 2.5),   # 9
    (4.0, 3.0),   # 10
    (4.0, 4.0),   # 11 肩右
    (3.5, 4.5),   # 12 脖子右
    (4.0, 5.0),   # 13 脸右
    (4.0, 6.0),   # 14 头顶右
    (3.5, 6.5),   # 15 右耳根
    (3.5, 8.0),   # 16 右耳外
    (3.0, 8.5),   # 17 右耳尖
    (2.5, 7.0),   # 18 右耳内
    (2.0, 6.5),   # 19 两耳之间
    (1.5, 7.5),   # 20 左耳内
    (1.0, 8.5),   # 21 左耳尖
    (0.5, 8.0),   # 22 左耳外
    (1.0, 6.5),   # 23 左耳根
    (1.0, 5.5),   # 24 脸左
    (1.0, 5.0),   # 25
    (1.5, 4.5),   # 26 脖子左
    (1.5, 4.0),   # 27 肩左
    (1.0, 3.5),   # 28 前爪左
    (1.0, 3.0),   # 29
    (0.5, 2.5),   # 30 尾巴上
    (0.5, 2.0),   # 31 尾巴尖
    (0.5, 1.5),   # 32 尾巴下
    (1.0, 1.5),   # 33
    (1.0, 1.0),   # 34
    (1.0, 0.5),   # 35
    (1.5, 0.5),   # 36
]

# 第 37、38 号：两只眼睛，**不连给任何点**，各画一个点。
# 认朝向靠**尾巴**：它长在兔子的左边，照过镜子就跑到右边去。
EYES = [(2.5, 5.0), (3.5, 5.0)]
EYE = EYES[0]


def apply(M, pts):
    """账本 M（两行两列）乘点名单：每个点各算一次落点。"""
    return [(M[0][0] * x + M[0][1] * y, M[1][0] * x + M[1][1] * y) for x, y in pts]


def draw_rabbit(ax, pts, color=NAVY, dots=True, lw=2.0, ms=4.5, zorder=4, eye=None):
    xs = [p[0] for p in pts] + [pts[0][0]]
    ys = [p[1] for p in pts] + [pts[0][1]]
    ax.plot(xs, ys, color=color, lw=lw, zorder=zorder)
    if dots:
        ax.plot(xs[:-1], ys[:-1], 'o', ms=ms, color=color, zorder=zorder + 1)
    es = EYES if eye is None else ([eye] if isinstance(eye, tuple) else eye)
    for e in (es or []):
        ax.plot([e[0]], [e[1]], 'o', ms=ms + 2.5, color=color, zorder=zorder + 2)


def grid(ax, x0, x1, y0, y1, M=None, color='#C9D6EA', lw=0.7):
    """方格纸；给了账本 M 就画变换后的格线。"""
    for gx in range(x0, x1 + 1):
        seg = [(gx, y0), (gx, y1)]
        if M:
            seg = apply(M, seg)
        ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]], color=color, lw=lw, zorder=1)
    for gy in range(y0, y1 + 1):
        seg = [(x0, gy), (x1, gy)]
        if M:
            seg = apply(M, seg)
        ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]], color=color, lw=lw, zorder=1)



# ============================================================ 精细兔子
# 第一篇只印那只 36 点的粗兔子（孩子照着画得出来）；从第二篇起，
# 所有"变换"的图都改用下面这只**精细兔子**——它的点名单几百个点，
# 正文明说"因为篇幅不列出来"。原理一模一样：还是点名单＋连线单，
# 只是点多、线密。**变换时所有路径一起变**（眼睛、内耳、尾巴都在名单上）。

def _smooth(pts, per=26, closed=True):
    """Catmull-Rom：拿一串控制点，连成一条光滑曲线（返回密集点列）。"""
    P = np.asarray(pts, dtype=float)
    n = len(P)
    idx = range(n) if closed else range(n - 1)
    out = []
    for i in idx:
        p0 = P[(i - 1) % n] if closed else P[max(i - 1, 0)]
        p1, p2 = P[i % n], P[(i + 1) % n]
        p3 = P[(i + 2) % n] if closed else P[min(i + 2, n - 1)]
        t = np.linspace(0, 1, per, endpoint=False)[:, None]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t
                          + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    seg = np.vstack(out)
    return np.vstack([seg, seg[:1]]) if closed else seg


def _circle(cx, cy, r, n=56):
    a = np.linspace(0, 2 * np.pi, n)
    return np.column_stack([cx + r * np.cos(a), cy + r * np.sin(a)])


def _ellipse(cx, cy, rx, ry, rot=0.0, n=72):
    """椭圆（可转一个角度）。可爱的兔子基本是一堆圆和椭圆堆出来的。"""
    a = np.linspace(0, 2 * np.pi, n)
    x, y = rx * np.cos(a), ry * np.sin(a)
    t = np.radians(rot)
    return np.column_stack([cx + x * np.cos(t) - y * np.sin(t),
                            cy + x * np.sin(t) + y * np.cos(t)])


# ---- 配色
FUR, PINK, WHITE, ROSE = '#FDF6EA', '#F6C7B4', '#FFFFFF', '#E79A86'

# ============ 精细兔子＝用户提供的插画（vol3/assets/rabbit.png，已去背）
# 它是一张**图片**，不是一串点。可道理一样：图片本身就是一张巨大的数字表，
# 变换时**整张图按同一本账搬过去**（matplotlib 的仿射变换替我们做这件事）。
# 兔子在书里的坐标：宽 0.5 到 4.24，高 0 到 8.6。
_ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets',
                      'rabbit.png')
_PHOTO = None
PHOTO_BOX = (0.5, 4.24, 0.0, 8.6)      # 左, 右, 下, 上


def _photo(gray=False):
    global _PHOTO
    if _PHOTO is None:
        from PIL import Image
        _PHOTO = np.array(Image.open(_ASSET).convert('RGBA')).astype(float) / 255
    im = _PHOTO.copy()
    if gray:                            # 当"变换前"的影子用
        g = im[:, :, :3].mean(axis=2, keepdims=True)
        im[:, :, :3] = 0.62 + 0.38 * np.repeat(g, 3, axis=2)
    return im


def draw_fine(ax, M=None, color=None, lw=1.0, fill=True, zorder=4, alpha=1.0,
              shift=(0.0, 0.0), scale=1.0):
    """把兔子画上去；给了账本 M 就画变换后的样子。

    color=GREY 时自动改成灰影（书里"变换前"的画法）；shift/scale 只为排版。
    """
    from matplotlib.transforms import Affine2D
    x0, x1, y0, y1 = PHOTO_BOX
    A = Affine2D()
    if M is not None:
        A = Affine2D(matrix=np.array([[M[0][0], M[0][1], 0],
                                      [M[1][0], M[1][1], 0], [0, 0, 1]]))
    A = Affine2D().scale(scale).translate(*shift) if False else A
    T = A
    if scale != 1.0 or shift != (0.0, 0.0):
        T = A + Affine2D().scale(scale).translate(*shift)
    ax.imshow(_photo(gray=(color == GREY)), extent=[x0, x1, y0, y1],
              interpolation='bilinear', alpha=alpha,
              transform=T + ax.transData, zorder=zorder)


def axes_cross(ax, xmin, xmax, ymin, ymax):
    ax.axhline(0, color=NAVY, lw=1.3, zorder=2)
    ax.axvline(0, color=NAVY, lw=1.3, zorder=2)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal')
    ax.axis('off')


def figr00():
    """坐标系是三件事：出发点、两条轴、一格有多大。"""
    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    grid(ax, -1, 5, -1, 4)
    axes_cross(ax, -1.5, 5.6, -1.5, 4.5)
    ax.plot([0], [0], 'o', ms=8, color=ORANGE, zorder=5)
    ax.text(-0.25, -0.95, '出发点', fontsize=10.5, color=ORANGE, ha='right')
    ax.text(5.3, -0.55, '横轴', fontsize=10.5, color=NAVY, ha='right')
    ax.text(0.25, 4.3, '竖轴', fontsize=10.5, color=NAVY, ha='left')
    ax.plot([3, 3], [0, 2], color=GREY, lw=1.2, ls='--', zorder=2)
    ax.plot([0, 3], [2, 2], color=GREY, lw=1.2, ls='--', zorder=2)
    ax.plot([3], [2], 'o', ms=9, color=GREEN, zorder=6)
    ax.text(3.2, 2.15, '(3, 2)', fontsize=11.5, color=GREEN, ha='left')
    ax.annotate('', xy=(1, -0.72), xytext=(0, -0.72),
                arrowprops=dict(arrowstyle='<|-|>', color=ORANGE, lw=1.4,
                                mutation_scale=11))
    ax.text(0.5, -1.25, '一格', fontsize=10, color=ORANGE, ha='center')
    ax.text(1.5, 0.35, '先往右 3 格', fontsize=10.5, color=NAVY, ha='center')
    ax.text(3.75, 1.0, '再往上 2 格', fontsize=10.5, color=NAVY, ha='left')
    save(fig, 'fig-r00-coord.png')


def figr01():
    """兔子＝点名单＋连线单；两个点的坐标。"""
    fig, ax = plt.subplots(figsize=(5.6, 5.8))
    grid(ax, -1, 6, -1, 9)
    axes_cross(ax, -2.3, 6.4, -1.4, 9.4)
    draw_rabbit(ax, RABBIT)
    ax.plot([0], [0], 'o', ms=7, color=ORANGE, zorder=5)
    ax.text(-0.25, -0.95, '出发点 (0, 0)', fontsize=10, color=ORANGE, ha='left')
    ax.plot([0.5], [2], 'o', ms=7, color=ORANGE, zorder=6)
    ax.text(-2.15, 2.1, '(0.5, 2)', fontsize=10.5, color=ORANGE, ha='left')
    ax.text(-2.15, 1.5, '尾巴尖', fontsize=9.5, color=GREY, ha='left')
    ax.plot([3.0], [8.5], 'o', ms=7, color=GREEN, zorder=6)
    ax.text(3.25, 8.55, '(3, 8.5)', fontsize=10.5, color=GREEN, ha='left')
    ax.text(3.25, 7.95, '右耳尖', fontsize=9.5, color=GREY, ha='left')
    save(fig, 'fig-r01-rabbit.png')


def figr02():
    """对名单做同一件事：右移 3；两个坐标都乘 2。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 3.6))
    ax = axs[0]
    grid(ax, -1, 8, -1, 9)
    axes_cross(ax, -1.3, 8.3, -1.5, 9.5)
    draw_fine(ax, color=GREY, fill=False, lw=1.0)
    draw_fine(ax, color=ORANGE, lw=1.5, shift=(3, 0))
    ax.annotate('', xy=(5.6, 8.75), xytext=(2.6, 8.75),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=1.6))
    ax.text(0.5, -0.02, '横坐标都加 3：整只右移', transform=ax.transAxes,
            ha='center', va='top', fontsize=10.5, color=ORANGE)
    ax = axs[1]
    grid(ax, -1, 10, -1, 18)
    axes_cross(ax, -1.3, 10.3, -1.8, 18.3)
    draw_fine(ax, color=GREY, fill=False, lw=1.0)
    draw_fine(ax, M=[[2, 0], [0, 2]], color=GREEN, lw=1.5)
    ax.text(0.5, -0.02, '两个坐标都乘 2：从出发点吹气球', transform=ax.transAxes,
            ha='center', va='top', fontsize=10.5, color=GREEN)
    save(fig, 'fig-r02-moves.png')


def figr03():
    """配方：(3, 2) ＝ 三份横箭头 ＋ 两份竖箭头。"""
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    grid(ax, 0, 4, 0, 3)
    axes_cross(ax, -0.5, 4.6, -0.9, 3.4)
    for k in range(3):
        ax.annotate('', xy=(k + 0.94, 0), xytext=(k, 0),
                    arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.6))
    for k in range(2):
        ax.annotate('', xy=(3, k + 0.94), xytext=(3, k),
                    arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.6))
    ax.plot([3], [2], 'o', ms=8, color=NAVY, zorder=5)
    ax.text(3.15, 2.15, '(3, 2)', fontsize=11, color=NAVY)
    ax.text(1.5, -0.65, '三份横箭头', fontsize=10.5, color=ORANGE, ha='center')
    ax.text(3.35, 0.9, '两份竖箭头', fontsize=10.5, color=GREEN, ha='left')
    save(fig, 'fig-r03-recipe.png')


def figr04():
    """斜拉机：格子歪了，兔子跟着歪；两支箭头的落点就是账本。"""
    SHEAR = [[1, 1], [0, 1]]
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.4))
    ax = axs[0]
    grid(ax, -1, 6, -1, 9)
    axes_cross(ax, -1.3, 6.3, -1.8, 9.3)
    draw_fine(ax, lw=1.4)
    ax.annotate('', xy=(0.94, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.4, mutation_scale=13))
    ax.annotate('', xy=(0, 0.94), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.4, mutation_scale=13))
    ax.text(3.0, -1.7, '进机器前', fontsize=10.5, color=NAVY, ha='center')
    ax = axs[1]
    grid(ax, -1, 6, -1, 9, M=SHEAR)
    axes_cross(ax, -1.3, 13.6, -1.8, 9.3)
    draw_fine(ax, M=SHEAR, lw=1.4)
    ax.annotate('', xy=(0.94, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.4, mutation_scale=13))
    ax.annotate('', xy=(0.92, 0.92), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.4, mutation_scale=13))
    ax.text(7.0, -1.7, '出机器后：横箭头没动，竖箭头斜了', fontsize=10.5,
            color=NAVY, ha='center')
    save(fig, 'fig-r04-shear.png')



def figr05():
    """账本的本体：两支基本箭头进机器前后。"""
    SHEAR = [[1, 1], [0, 1]]
    fig, axs = plt.subplots(1, 2, figsize=(6.2, 2.9))
    ax = axs[0]
    grid(ax, 0, 2, 0, 2)
    axes_cross(ax, -0.45, 2.55, -0.75, 2.35)
    ax.annotate('', xy=(0.97, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=3.4, mutation_scale=20))
    ax.annotate('', xy=(0, 0.97), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=3.4, mutation_scale=20))
    ax.text(0.55, -0.42, '横箭头', fontsize=10.5, color=ORANGE, ha='center')
    ax.text(-0.38, 1.35, '竖\n箭\n头', fontsize=10.5, color=GREEN, ha='center',
            linespacing=1.1)
    ax.text(1.55, 1.75, '进机器前', fontsize=10.5, color=NAVY, ha='center')
    ax = axs[1]
    grid(ax, 0, 2, 0, 2, M=SHEAR)
    axes_cross(ax, -0.45, 4.35, -0.75, 2.35)
    ax.plot([0, 0], [0, 0.97], color=GREEN, lw=1.6, ls='--', zorder=2)
    ax.annotate('', xy=(0.97, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=3.4, mutation_scale=20))
    ax.annotate('', xy=(0.97, 0.97), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=3.4, mutation_scale=20))
    ax.text(0.62, -0.42, '还落在 (1, 0)', fontsize=10.5, color=ORANGE, ha='center')
    ax.text(1.62, 1.02, '斜到了 (1, 1)', fontsize=10.5, color=GREEN, ha='left')
    ax.text(3.35, 1.75, '出机器后', fontsize=10.5, color=NAVY, ha='center')
    save(fig, 'fig-r05-basis.png')


def figr06():
    """先转再压 ≠ 先压再转：两只不一样的兔子。"""
    R = [[0, -1], [1, 0]]
    S = [[1, 0], [0, 0.5]]
    SR = [[0, -1], [0.5, 0]]
    RS = [[0, -0.5], [1, 0]]
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 3.1),
                            gridspec_kw={'width_ratios': [0.55, 1.05, 0.85]})
    ax = axs[0]
    axes_cross(ax, -1.0, 5.2, -1.9, 9.2)
    draw_fine(ax)
    ax.text(2.9, -1.8, '原样', fontsize=10.5, color=NAVY, ha='center')
    ax = axs[1]
    axes_cross(ax, -9.2, 1.2, -1.9, 5.2)
    draw_fine(ax, M=SR, color=ORANGE, lw=1.4)
    ax.text(-3.8, -1.8, '先转，再压', fontsize=10.5, color=ORANGE, ha='center')
    ax = axs[2]
    axes_cross(ax, -5.2, 1.2, -1.9, 9.2)
    draw_fine(ax, M=RS, color=GREEN, lw=1.4)
    ax.text(0.9, -1.8, '先压，再转', fontsize=10.5, color=GREEN, ha='center')
    save(fig, 'fig-r06-order.png')


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  wrote', name)



# ---------------------------------------------------------------- r10
def figr10():
    """五台机器各变一次兔子。"""
    MS = [('放大机', [[1.5, 0], [0, 1.5]]), ('压扁机', [[1, 0], [0, 0.5]]),
          ('镜子机', [[-1, 0], [0, 1]]), ('转 90 度机', [[0, -1], [1, 0]]),
          ('斜拉机', [[1, 1], [0, 1]])]
    fig, axs = plt.subplots(2, 3, figsize=(7.2, 6.0))
    fig.subplots_adjust(hspace=0.32)
    ax = axs[0][0]
    axes_cross(ax, -1.2, 7.6, -1.3, 13.6)
    draw_fine(ax)
    ax.text(0.5, -0.03, '原样', transform=ax.transAxes, ha='center', va='top',
            fontsize=10.5, color=NAVY)
    # 前三格**共用同一个画框**：只有这样，"放大"和"压扁"才真的看得出大小变了。
    # 画框各自缩放的话，放大后的兔子在纸面上反而和原样一般大——那等于什么都没画。
    SAME = (-1.2, 7.6, -1.3, 13.6)
    lims = {'放大机': SAME, '压扁机': SAME,
            '镜子机': (-5.4, 5.4, -1.3, 13.6), '转 90 度机': (-9.6, 5.0, -1.3, 13.6),
            '斜拉机': (-1.2, 13.6, -1.3, 13.6)}
    for i, (name, M) in enumerate(MS):
        ax = axs[(i + 1) // 3][(i + 1) % 3]
        x0, x1, y0, y1 = lims[name]
        axes_cross(ax, x0, x1, y0, y1)
        draw_fine(ax, color=GREY)
        draw_fine(ax, M=M)
        # 标签放到画框**外面**：放里面会压住兔子（这类叠字在前两册踩过多次）
        ax.text(0.5, -0.03, name, transform=ax.transAxes, ha='center', va='top',
                fontsize=10.5, color=ORANGE)
    save(fig, 'fig-r10-five-machines.png')


# ---------------------------------------------------------------- r11
def figr11():
    """竖坐标乘 0：兔子被压成一条线段。"""
    FLAT = [[1, 0], [0, 0]]
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    axes_cross(ax, -1.0, 9.6, -1.6, 9.4)
    draw_fine(ax, color=GREY)
    for t in (2.0, 5.0, 8.0):
        ax.plot([2.5, 2.5], [0, t], color=BAND, lw=6, zorder=1,
                solid_capstyle='butt')
    ax.plot([2.5], [0], 'o', ms=9, color=ORANGE, zorder=6)
    for t in (2.0, 5.0):
        ax.plot([2.5], [t], 'o', ms=6, color=ORANGE, zorder=6)
        ax.annotate('', xy=(2.5, 0.35), xytext=(2.5, t - 0.3),
                    arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=1.3))
    ax.plot([0.5, 4.24], [0, 0],
            color=NAVY, lw=4.0, zorder=5, solid_capstyle='butt')
    ax.text(5.4, 4.6, '一竖排的点，\n全落到同一处', fontsize=10.5, color=ORANGE,
            ha='left', linespacing=1.5)
    ax.text(5.4, 0.4, '兔子只剩\n这一条线段', fontsize=10.5, color=NAVY,
            ha='left', linespacing=1.5)
    save(fig, 'fig-r11-squash-flat.png')


# ---------------------------------------------------------------- r12
def figr12():
    """单位方格变成平行四边形。"""
    SHEAR = [[1, 1], [0, 1]]
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 3.0))
    for ax, M, lab in ((axs[0], None, '单位方格：面积是 1'),
                       (axs[1], SHEAR, '过了斜拉机：面积还是 1')):
        pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        if M:
            pts = apply(M, pts)
        grid(ax, -1, 3, -1, 2, color='#E3E8EF')
        axes_cross(ax, -0.9, 3.1, -1.0, 2.3)
        ax.fill([p[0] for p in pts], [p[1] for p in pts], color=LIGHT, zorder=2)
        ax.plot([p[0] for p in pts] + [pts[0][0]],
                [p[1] for p in pts] + [pts[0][1]], color=NAVY, lw=1.8, zorder=3)
        h = (1, 0) if not M else tuple(apply(M, [(1, 0)])[0])
        v = (0, 1) if not M else tuple(apply(M, [(0, 1)])[0])
        ax.annotate('', xy=(h[0] * 0.94, h[1] * 0.94), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.6,
                                    mutation_scale=14), zorder=5)
        ax.annotate('', xy=(v[0] * 0.94, v[1] * 0.94), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.6,
                                    mutation_scale=14), zorder=5)
        ax.text(1.1, -0.85, lab, fontsize=10.5, color=NAVY, ha='center')
    save(fig, 'fig-r12-unit-square.png')


# ---------------------------------------------------------------- r13
def figr13():
    """剪拼：大长方形减掉六小块，剩下的就是 ad 减 bc。"""
    a, c, b, d = 3.0, 1.0, 1.0, 2.0
    fig, ax = plt.subplots(figsize=(6.0, 4.4))
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(-0.9, a + b + 0.7); ax.set_ylim(-1.9, c + d + 1.0)
    PINK, MINT, SAND = '#F7D8C4', '#CFE8DA', '#DDE4F0'
    pieces = [([(0, 0), (a, 0), (a, c)], PINK),
              ([(b, d), (b, c + d), (a + b, c + d)], PINK),
              ([(a, c), (a + b, c), (a + b, c + d)], MINT),
              ([(0, 0), (0, d), (b, d)], MINT),
              ([(a, 0), (a + b, 0), (a + b, c), (a, c)], SAND),
              ([(0, d), (0, c + d), (b, c + d), (b, d)], SAND)]
    for pts, col in pieces:
        ax.fill([q[0] for q in pts], [q[1] for q in pts], color=col, zorder=2)
    para = [(0, 0), (a, c), (a + b, c + d), (b, d)]
    ax.fill([q[0] for q in para], [q[1] for q in para], color=LIGHT, zorder=3)
    ax.plot([q[0] for q in para] + [para[0][0]],
            [q[1] for q in para] + [para[0][1]], color=NAVY, lw=2.4, zorder=5)
    ax.add_patch(plt.Rectangle((0, 0), a + b, c + d, fill=False,
                               edgecolor=GREY, lw=1.6, ls='--', zorder=4))
    ax.annotate('', xy=(a * 0.95, c * 0.95), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.6,
                                mutation_scale=14), zorder=6)
    ax.annotate('', xy=(b * 0.92, d * 0.92), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.6,
                                mutation_scale=14), zorder=6)
    ax.text(a + 0.1, c - 0.16, '(a, c)', fontsize=10.5, color=ORANGE)
    ax.text(b + 0.12, d - 0.42, '(b, d)', fontsize=10.5, color=GREEN)
    ax.text(a / 2 + 0.35, c / 4, 'ac', fontsize=9.5, color='#B0743F', ha='center')
    ax.text(b + (a - 0.2) / 2, c + d - 0.28, 'ac', fontsize=9.5, color='#B0743F',
            ha='center')
    ax.text(a + b - 0.22, c + d / 1.9, 'bd', fontsize=9.5, color='#3C7D5F',
            ha='center')
    ax.text(0.2, d - 0.55, 'bd', fontsize=9.5, color='#3C7D5F', ha='center')
    ax.text(a + b / 2, c / 2.6, 'bc', fontsize=9.5, color=NAVY, ha='center')
    ax.text(b / 2, d + c / 2.2, 'bc', fontsize=9.5, color=NAVY, ha='center')
    ax.text((a + b) / 2, -0.75, '大长方形：宽 a ＋ b，高 c ＋ d', fontsize=10.5,
            color=GREY, ha='center')
    ax.text((a + b) / 2, -1.55,
            '减掉两块 ac 的一半、两块 bd 的一半、两块 bc，\n剩下的就是 ad 减 bc',
            fontsize=10.5, color=NAVY, ha='center', linespacing=1.6)
    save(fig, 'fig-r13-shoelace.png')


# ---------------------------------------------------------------- r15
def figr15():
    """核：一整条竖线被压到一个点。"""
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    axes_cross(ax, -3.4, 4.4, -3.2, 3.6)
    ax.plot([0, 0], [-2.1, 3.2], color=ORANGE, lw=4.5, zorder=3,
            solid_capstyle='butt', alpha=0.85)
    ax.text(0.25, 3.0, '核：整条竖轴', fontsize=10.5, color=ORANGE, ha='left')
    ax.plot([0], [0], 'o', ms=10, color=ORANGE, zorder=6)
    for t in (2.5, 1.2, -1.8):
        ax.plot([2.0], [t], 'o', ms=7, color=NAVY, zorder=5)
        ax.annotate('', xy=(2.0, -0.28), xytext=(2.0, t * 0.86),
                    arrowprops=dict(arrowstyle='-|>', color=GREY, lw=1.2, ls='--'))
    ax.plot([2.0], [0], 'o', ms=9, color=GREEN, zorder=6)
    ax.text(2.3, 0.28, '全落在这一个点上', fontsize=10.5, color=GREEN, ha='left')
    ax.text(0.5, -0.02, '被送到出发点的那些箭头，凑成核', transform=ax.transAxes,
            ha='center', va='top', fontsize=10.5, color=ORANGE)
    save(fig, 'fig-r15-kernel.png')


# ---------------------------------------------------------------- r17
def figr17():
    """三维兔子和它的影子：沿光线挪动，影子不变。"""
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(-1.2, 12.5); ax.set_ylim(-1.6, 9.6)
    for k in range(6):
        x = 1.2 + k * 1.6
        ax.annotate('', xy=(x, -0.15), xytext=(x, 9.3),
                    arrowprops=dict(arrowstyle='-|>', color='#F0C9A8', lw=1.3))
    ax.text(10.3, 9.0, '太阳光：直上直下', fontsize=10, color=ORANGE, ha='right')
    ax.plot([-0.6, 12.2], [0, 0], color=NAVY, lw=2.0, zorder=4)
    ax.text(11.9, -0.75, '地面', fontsize=10.5, color=NAVY, ha='right')
    sc = 0.42
    draw_fine(ax, scale=sc, shift=(1.6, 5.4))
    draw_fine(ax, color=GREY, scale=sc, shift=(1.6, 1.3))
    xs = [0.5 * sc + 1.6, 4.24 * sc + 1.6]
    ax.plot([min(xs), max(xs)], [0, 0], color=ORANGE, lw=5.0, zorder=5,
            solid_capstyle='butt')
    ax.text((min(xs) + max(xs)) / 2, -1.15, '影子', fontsize=10.5, color=ORANGE,
            ha='center')
    ax.annotate('', xy=(6.2, 1.6), xytext=(6.2, 5.6),
                arrowprops=dict(arrowstyle='<|-|>', color=GREEN, lw=1.6))
    ax.text(6.45, 3.9, '沿光线挪一挪，\n影子一动不动', fontsize=10.5, color=GREEN,
            ha='left', linespacing=1.5)
    save(fig, 'fig-r17-shadow.png')


# ---------------------------------------------------------------- r19
def figr19():
    """两支不平行配得出整个平面；两支平行只配得出一条线。"""
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.2))
    ax = axs[0]
    grid(ax, -3, 4, -2, 3, color='#E3E8EF')
    axes_cross(ax, -3.2, 4.2, -2.4, 3.3)
    for xy in [(i, j) for i in range(-3, 5) for j in range(-2, 4)]:
        ax.plot([xy[0]], [xy[1]], 'o', ms=2.6, color=LIGHT, zorder=2)
    ax.annotate('', xy=(1.9, 0.94), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.6,
                                mutation_scale=14), zorder=5)
    ax.annotate('', xy=(-0.94, 1.9), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.6,
                                mutation_scale=14), zorder=5)
    ax.text(0.6, -2.15, '不平行：配得出整个平面', fontsize=10.5, color=NAVY,
            ha='center')
    ax = axs[1]
    grid(ax, -3, 4, -2, 3, color='#E3E8EF')
    axes_cross(ax, -3.2, 4.2, -2.4, 3.3)
    ax.plot([-2.6, 3.0], [-2.6, 3.0], color=BAND, lw=7, zorder=1,
            solid_capstyle='round')
    ax.annotate('', xy=(0.94, 0.94), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.6,
                                mutation_scale=14), zorder=5)
    ax.annotate('', xy=(1.9, 1.9), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.2,
                                mutation_scale=13), zorder=4)
    ax.text(0.6, -2.15, '平行：只配得出这一条线', fontsize=10.5, color=ORANGE,
            ha='center')
    save(fig, 'fig-r19-span.png')


# ---------------------------------------------------------------- r20
def figr20():
    """同一只兔子，两套格子——两格必须同一比例，才看得出'兔子没变'。"""
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 4.0))
    for ax, M, arrow2, lab in (
            (axs[0], None, (0, 1), '老格子：右脚外记作 (3.5, 0.5)'),
            (axs[1], [[1, 1], [0, 1]], (1, 1), '斜格子：同一个点记作 (3, 0.5)')):
        if M:
            grid(ax, -10, 8, -1, 9, M=M, color='#C9D6EA')
        else:
            grid(ax, -1, 8, -1, 9)
        axes_cross(ax, -1.6, 7.4, -1.5, 9.6)
        draw_fine(ax)
        ax.plot([3.5], [0.5], 'o', ms=8, color=ORANGE, zorder=9)
        ax.annotate('', xy=(0.94, 0), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.8,
                                    mutation_scale=15), zorder=6)
        ax.annotate('', xy=(arrow2[0] * 0.94, arrow2[1] * 0.94), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.8,
                                    mutation_scale=15), zorder=6)
        ax.text(0.5, -0.02, lab, transform=ax.transAxes, ha='center', va='top',
                fontsize=10.5, color=NAVY)
    save(fig, 'fig-r20-newbasis.png')


# ---------------------------------------------------------------- r21
def figr21():
    """两块地板：兔子的平面，和多项式机器的天地。"""
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.4))
    ax = axs[0]
    grid(ax, -1, 8, -1, 9, color='#E3E8EF')
    axes_cross(ax, -1.2, 5.6, -1.8, 9.6)
    draw_fine(ax)
    ax.annotate('', xy=(0.94, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.6,
                                mutation_scale=13), zorder=8)
    ax.annotate('', xy=(0, 0.94), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.6,
                                mutation_scale=13), zorder=8)
    ax.text(2.2, -1.7, '兔子住的平面：两支箭头', fontsize=10.5, color=NAVY,
            ha='center')
    ax = axs[1]
    ax.set_xlim(-0.6, 7.4); ax.set_ylim(-1.8, 9.6)
    ax.axis('off')
    t = np.linspace(0.2, 2.3, 120)
    curves = ((lambda u: 0 * u + 1, '1', ORANGE), (lambda u: u, 'a', GREEN),
              (lambda u: u ** 2, r'$a^2$', NAVY))
    for i, (f, lab, col) in enumerate(curves):
        base = 6.2 - i * 3.0
        ax.plot([0.2, 6.1], [base, base], color=GREY, lw=1.0)
        ax.plot(t * 2.4 + 0.3, f(t) * 0.85 + base, color=col, lw=2.4)
        ax.text(6.9, base + 0.45, lab, fontsize=13, color=col, ha='left')
    ax.text(3.4, -1.7, '多项式机器的天地：三支"箭头"', fontsize=10.5, color=NAVY,
            ha='center')
    save(fig, 'fig-r21-poly-space.png')



# ---------------------------------------------------------------- r22
def figr22():
    """同一个念头，两只兔子：36 个点的粗兔子，和几百个点的精细兔子。"""
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 4.2))
    ax = axs[0]
    grid(ax, -1, 6, -1, 9)
    axes_cross(ax, -1.2, 6.2, -1.5, 9.4)
    draw_rabbit(ax, RABBIT, lw=1.8, ms=4.0)
    ax.text(0.5, -0.02, '36 个点：名单印在上面，你照着画得出来',
            transform=ax.transAxes, ha='center', va='top', fontsize=10.5,
            color=NAVY)
    ax = axs[1]
    grid(ax, -1, 6, -1, 9)
    axes_cross(ax, -1.2, 6.2, -1.5, 9.4)
    draw_fine(ax)
    ax.text(0.5, -0.02, '几百个点：一样是点名单，只是太长，不印了',
            transform=ax.transAxes, ha='center', va='top', fontsize=10.5,
            color=NAVY)
    save(fig, 'fig-r22-two-rabbits.png')



# ---------------------------------------------------------------- r23
def figr23():
    """斜拉机：大多数箭头被掰歪，只有横着那支不动；兔子脚下那条线也不动。"""
    SHEAR = [[1, 1], [0, 1]]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.6),
                            gridspec_kw={'width_ratios': [1.0, 1.25]})
    ax = axs[0]
    grid(ax, -2, 4, -1, 3, color='#E3E8EF')
    axes_cross(ax, -2.3, 4.4, -1.3, 3.4)
    pairs = [((0, 1), GREEN), ((1, 1), '#7B61A8'), ((-1, 2), '#C2557A')]
    for v, col in pairs:
        w = apply(SHEAR, [v])[0]
        ax.annotate('', xy=(v[0] * 0.94, v[1] * 0.94), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='-|>', color=col, lw=1.6,
                                    alpha=0.45, mutation_scale=12), zorder=3)
        ax.annotate('', xy=(w[0] * 0.96, w[1] * 0.96), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='-|>', color=col, lw=2.4,
                                    mutation_scale=14), zorder=4)
    ax.annotate('', xy=(0.94, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=3.2,
                                mutation_scale=16), zorder=6)
    ax.text(1.15, 0.12, '这一支没歪', fontsize=10.5, color=ORANGE, ha='left')
    ax.text(0.5, -0.03, '淡的是进去前，浓的是出来后', transform=ax.transAxes,
            ha='center', va='top', fontsize=10.5, color=NAVY)
    ax = axs[1]
    grid(ax, -1, 6, -1, 9, M=SHEAR, color='#C9D6EA')
    axes_cross(ax, -1.2, 13.4, -1.4, 9.4)
    draw_fine(ax, color=GREY)
    draw_fine(ax, M=SHEAR)
    ax.plot([0.5, 4.24], [0, 0], color=ORANGE, lw=4.0, zorder=9,
            solid_capstyle='butt')
    ax.text(0.5, -0.03, '兔子被拉斜了，脚下那条线一步没挪',
            transform=ax.transAxes, ha='center', va='top', fontsize=10.5,
            color=ORANGE)
    save(fig, 'fig-r23-fixed-direction.png')


# ---------------------------------------------------------------- r24
def figr24():
    """两个不歪的方向；换成它们当格子，机器只剩"一个拉 3 倍、一个不动"。"""
    M = [[2, 1], [1, 2]]
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.6))
    ax = axs[0]
    grid(ax, -3, 4, -3, 4, color='#E3E8EF')
    axes_cross(ax, -3.4, 4.4, -3.4, 4.4)
    for v, col in (((1, 0), GREY), ((0, 1), GREY)):
        w = apply(M, [v])[0]
        ax.annotate('', xy=(w[0] * 0.95, w[1] * 0.95), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='-|>', color=col, lw=1.6,
                                    mutation_scale=12), zorder=3)
    ax.plot([-3.2, 3.4], [-3.2, 3.4], color=BAND, lw=6, zorder=1,
            solid_capstyle='round')
    ax.plot([-3.2, 3.4], [3.2, -3.4], color='#DCEEE3', lw=6, zorder=1,
            solid_capstyle='round')
    ax.annotate('', xy=(2.9, 2.9), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.8,
                                mutation_scale=15), zorder=5)
    ax.annotate('', xy=(0.95, 0.95), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=1.6,
                                alpha=0.5, mutation_scale=12), zorder=4)
    ax.annotate('', xy=(0.95, -0.95), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.8,
                                mutation_scale=15), zorder=5)
    ax.text(1.35, 2.55, '拉 3 倍', fontsize=10.5, color=ORANGE)
    ax.text(1.15, -1.35, '原样不动', fontsize=10.5, color=GREEN)
    ax.text(0.5, -0.03, '两个不歪的方向（灰的是被掰歪的横竖箭头）'.replace('（灰的是被掰歪的横竖箭头）', ''),
            transform=ax.transAxes, ha='center', va='top', fontsize=10.5,
            color=NAVY)
    ax = axs[1]
    B = [[1, 1], [1, -1]]
    grid(ax, -3, 4, -3, 4, M=B, color='#C9D6EA')
    axes_cross(ax, -4.4, 4.4, -4.4, 4.4)
    ax.annotate('', xy=(0.95, 0.95), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=2.8,
                                mutation_scale=15), zorder=5)
    ax.annotate('', xy=(0.95, -0.95), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color=GREEN, lw=2.8,
                                mutation_scale=15), zorder=5)
    ax.text(0.5, -0.03, '换成这两支当格子',
            transform=ax.transAxes, ha='center', va='top', fontsize=10.5,
            color=NAVY)
    save(fig, 'fig-r24-eigen-basis.png')


if __name__ == '__main__':
    print('generating ->', OUT)
    for f in (figr00, figr01, figr02, figr03, figr04, figr05, figr06,
              figr10, figr11, figr12, figr13, figr15, figr17, figr19,
              figr20, figr21, figr22, figr23, figr24):
        f()
    print('done:', len([a for a in os.listdir(OUT) if a.endswith('.png')]), 'figures')
