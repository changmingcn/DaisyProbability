#!/usr/bin/env python3
"""互动页的自动校验闸 —— 不过就不许上传（和 verify_docx.py 一个规矩）。

    python3 vol3/interactive/check_interactive.py          # 查默认那一页
    python3 vol3/interactive/check_interactive.py <文件>    # 查指定文件

为什么要这道闸：这一页的正确性有一半不在"看得见的地方"。
兔子转多少度、镜头站在哪个方位角，是**分开写在四处**的两个数；
只要改了一处忘了另一处，兔子就悄悄背对着镜头，而页面照样能打开、
控制台也不报错——正是那种"没有任何检查会响"的错（教训 12）。
所以把这几条不变量钉成会失败的检查。
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, '兔子的线性变换-三维版.html')

fails, warns, done = [], [], []


def check(tag, ok, msg):
    print(('  ✓ ' if ok else '  ✗ ') + '[%s] %s' % (tag, msg))
    done.append(tag)
    if not ok:
        fails.append(tag)


def warn(tag, msg):
    print('  ⚠ [%s] %s' % (tag, msg))
    warns.append(tag)


def num(expr):
    """把 `3 * Math.PI / 4`、`135 * Math.PI / 180` 这类写法算成数。"""
    e = expr.replace('Math.PI', str(math.pi))
    if not re.fullmatch(r'[-+*/(). 0-9e]+', e):
        raise ValueError('看不懂的表达式：' + expr)
    return eval(e)  # noqa: S307 —— 上一行已经把字符集卡死在数字和四则运算里


def main(path):
    print('检查 %s（%d 字节）' % (os.path.basename(path), os.path.getsize(path)))
    src = open(path, encoding='utf-8').read()

    # ---- [W1] 每个 <script> 块的 JS 语法 ----
    blocks = re.findall(r'<script>(.*?)</script>', src, re.S)
    if not blocks:
        check('W1', False, '一个 <script> 块都没找到，文件多半不完整')
    elif shutil.which('node') is None:
        warn('W1', '本机没有 node，跳过 JS 语法检查（装了 node 这道闸才是硬的）')
    else:
        bad = []
        with tempfile.TemporaryDirectory() as d:
            for i, b in enumerate(blocks):
                f = os.path.join(d, 'b%d.js' % i)
                open(f, 'w', encoding='utf-8').write(b)
                r = subprocess.run(['node', '--check', f], capture_output=True, text=True)
                if r.returncode != 0:
                    bad.append('第 %d 块：%s' % (i + 1, r.stderr.strip().splitlines()[-1][:80]))
        check('W1', not bad, 'JS 语法：%d 个 <script> 块%s'
              % (len(blocks), ' 全通过' if not bad else ' —— ' + '；'.join(bad)))

    # ---- [W2] 三根轴的名字 ----
    letters = re.findall(r"letter:\s*'([XYZ])'", src)
    check('W2', letters == ['X', 'Y', 'Z'],
          '坐标轴名字 = %s（应为 X Y Z，按 往右／往里／往上 的顺序）' % (letters or '无'))

    # ---- [W3] 镜头方位角 ＝ 兔子转角 − 整幅画面右手旋的角度 ----
    # 图纸里兔子脸朝 −y，绕 z 转 YAW 之后脸朝 (sin YAW, −cos YAW)；
    # 镜头在方位角 az 时站在 (sin az, −cos az) 那一侧。两者之差就是兔子侧过去多少。
    # 08-06 之前这个差必须是 0（兔子正面朝人）；现在用户要整幅画面右手旋 45°，
    # 差变成一个**写明了的** VIEW_TURN——闸不是钉死"必须正面"，而是钉死
    # "这三个数必须还是当初说好的那个关系"，任何一处被悄悄改动照样红。
    m_yaw = re.search(r'var YAW\s*=\s*([^;]+);', src)                 # RABBIT 模块里的
    m_yaw2 = re.search(r'var RABBIT_YAW\s*=\s*([^;]+);', src)         # 绘图模块里的副本
    m_turn = re.search(r'var VIEW_TURN\s*=\s*([^;]+);', src)
    m_az = re.search(r'cam:\s*\{\s*az:\s*([^,]+),', src)
    if not (m_yaw and m_yaw2 and m_turn and m_az):
        check('W3', False, '找不到 YAW / RABBIT_YAW / VIEW_TURN / cam.az —— 这几个数是这一页的命门')
    else:
        yaw, yaw2, turn = num(m_yaw.group(1)), num(m_yaw2.group(1)), num(m_turn.group(1))
        # cam.az 必须是**算出来的**，不许写死字面量：写死了，改 YAW 就会悄悄脱节
        az_expr = m_az.group(1).strip()
        computed = az_expr == 'RABBIT_YAW - VIEW_TURN'
        d = abs(math.degrees(yaw - yaw2))
        cosface = math.cos(turn)
        check('W3', d < 1e-6 and computed,
              '两处兔子转角一致（YAW %.3f° vs RABBIT_YAW %.3f°，差 %.4f°）且 cam.az 是算出来的'
              '（现为 `%s`%s）；整幅画面右手旋 %.1f°，兔子因此侧了这么多，脸朝向·镜头 = %.3f'
              % (math.degrees(yaw), math.degrees(yaw2), d, az_expr,
                 '' if computed else ' —— 应为 `RABBIT_YAW - VIEW_TURN`，写死字面量迟早脱节',
                 math.degrees(turn), cosface))

    # ---- [W4] 视角按钮的基准角也得跟上 ----
    m_btn = re.search(r'var YAW_AZ\s*=\s*([^;]+);', src)
    if not m_btn:
        check('W4', False, '找不到 YAW_AZ —— 三个视角按钮就会各转各的')
    elif m_yaw:
        d = abs(math.degrees(num(m_btn.group(1)) - num(m_yaw.group(1))))
        check('W4', d < 1e-6, '视角按钮基准角对齐兔子转角？差 %.4f°' % d)

    # ---- [W5] 主光在镜头这一侧，脸不能背光 ----
    # 脸朝向要从**兔子的转角**算，不能从镜头方位角算——08-06 加 VIEW_TURN 之后
    # 这两个数不再相等，拿 az 当脸朝向就会在兔子侧身时误判。
    m_l = re.search(r"'uLight'\s*\),\s*new Float32Array\(\[([^\]]+)\]", src)
    if not (m_l and m_yaw):
        check('W5', False, '找不到主光方向或兔子转角')
    else:
        lx, ly, _lz = [float(x) for x in m_l.group(1).split(',')]
        yaw = num(m_yaw.group(1))
        fx, fy = math.sin(yaw), -math.cos(yaw)        # 兔子脸的朝向
        c = (lx * fx + ly * fy) / math.hypot(lx, ly)
        check('W5', c > 0.2,
              '主光照得到脸？主光·脸朝向 = %.3f（≤0 就是背光，脸会暗一大截）' % c)

    # ---- [W6] 自包含：上了站也不能去外面要东西 ----
    ext = re.findall(r'(?:src|href)\s*=\s*["\']https?://[^"\']+', src)
    ext = [e for e in ext if 'acme' not in e]
    check('W6', not ext, '页面自包含（不向外网要资源）%s'
          % ('' if not ext else '—— 发现 %d 处：%s' % (len(ext), ext[:3])))

    # ---- [W7] 轴名字得收在轴里面，别钉在轴头上 ----
    # 08-06 用户挑出来的：第一版钉在 1.08 × AX（＝1.35）处，一转视角字就飘出画框没了。
    # 扫过整个可拖动的视角范围：1.35 处在宽屏有 10% 的角度看不见、方屏 35%、手机竖屏 47%；
    # 收到 0.72 × AX（＝0.9）之后宽屏和方屏都是 0%。0.8 是留了余量的上限。
    m_r = re.search(r"addLabel\(LA\.vscale\(a\.v,\s*AX\s*\*\s*([0-9.]+)\),\s*a\.letter", src)
    if not m_r:
        check('W7', False, '找不到轴名字的摆放半径')
    else:
        f = float(m_r.group(1))
        check('W7', f <= 0.8,
              '轴名字收在 %.2f × 轴长（要 ≤ 0.80，再往外转起来就飘出画框了）' % f)

    # ---- [W8] "往上抬一个字高"必须在屏幕上抬，不能在三维里抬 ----
    # 用户 08-06："旋转的时候不能旋转这三个字母"。要是把这一抬做成三维里的 +z 偏移，
    # 一转视角偏移方向就跟着转，字会绕着轴甩；做成屏幕像素偏移才永远指向画面正上方。
    lifts = len(re.findall(r'q\[1\]\s*-\s*AXLBL_PX', src))
    pure_anchor = bool(re.search(
        r"addLabel\(LA\.vscale\(a\.v,\s*AX\s*\*\s*[0-9.]+\),\s*a\.letter", src))
    check('W8', lifts >= 2 and pure_anchor,
          '往上抬在屏幕像素里做（描边＋填字共 %d 处用 q[1] − AXLBL_PX）'
          '且三维锚点是纯量倍、没掺偏移向量（%s）'
          % (lifts, '是' if pure_anchor else '否 —— 锚点被加了三维偏移，转视角时字会甩'))

    # ---- [W9] 兔子不许伸出采样盒（伸出去不是消失，是被削平）----
    # 隐式曲面只在 lo..hi 这个盒子里取样，超出的部分被切成一个平面，
    # 而且很难看出来——2026-08-06 才发现**右耳尖一直是平的**（理论 2.835，盒顶只有 2.76）。
    # 光看代码看不出来，必须真的把网格建出来量，所以这条要跑 node。
    if shutil.which('node') is None:
        warn('W9', '本机没有 node，跳过"兔子伸出采样盒"的实测')
    else:
        blk = None
        for b in blocks:
            if 'var RABBIT' in b and 'function build' in b:
                blk = b
                break
        if blk is None:
            check('W9', False, '找不到 RABBIT 模块，量不了')
        else:
            with tempfile.TemporaryDirectory() as d:
                mod = os.path.join(d, 'rab.js')
                open(mod, 'w', encoding='utf-8').write(blk)
                probe = (
                    'const R=require(%r);const m=R.build(0.028);'
                    'const s=%r;const lo=s[0],hi=s[1];const P=m.pos;'
                    'const mn=[9,9,9],mx=[-9,-9,-9];'
                    'for(let i=0;i<P.length;i+=3)for(let t=0;t<3;t++){'
                    'if(P[i+t]<mn[t])mn[t]=P[i+t];if(P[i+t]>mx[t])mx[t]=P[i+t];}'
                    'let g=9,w="";for(let t=0;t<3;t++){'
                    'if(mn[t]-lo[t]<g){g=mn[t]-lo[t];w="xyz"[t]+"下";}'
                    'if(hi[t]-mx[t]<g){g=hi[t]-mx[t];w="xyz"[t]+"上";}}'
                    'console.log(JSON.stringify({gap:g,where:w}));')
                mbox = re.search(
                    r'var lo = \[([^\]]+)\], hi = \[([^\]]+)\]', blk)
                if not mbox:
                    check('W9', False, '找不到采样盒 lo/hi')
                else:
                    box = [[float(x) for x in mbox.group(i).split(',')] for i in (1, 2)]
                    r = subprocess.run(['node', '-e', probe % (mod, box)],
                                       capture_output=True, text=True)
                    if r.returncode != 0:
                        check('W9', False, '建网格失败：' + r.stderr.strip()[-120:])
                    else:
                        g = json.loads(r.stdout)
                        check('W9', g['gap'] > 0.02,
                              '兔子离采样盒最近处还有 %.4f 的余量（最紧在 %s；'
                              '≤0 就是被削平了，而且看不出来）' % (g['gap'], g['where']))

    # ---- [W10] 默认视角下，嘴不许被卡通描边吞掉 ----
    # 2026-08-06 傍晚用户报："俯视高度过高，嘴巴看不清楚。"查出来的机制值得钉成闸：
    # 嘴画在口鼻鼓包的**下侧**，法向本来就朝斜下方；默认仰角越高，那一片就越贴着轮廓掠过去，
    # 而着色器最后一步的卡通描边 smoothstep(0.70, 0.96, 1 − |n·V|) 从 |n·V| < 0.30 起就往上抹黑——
    # 嘴于是先被压扁、再被描边吞掉。**页面照开、控制台不报错、别的九项全绿**，正是教训 12 那一类。
    # 判据取"被抹黑过半的墨迹占比"：el 0.45 是 47%、0.35 是 27%、≤0.22 是 0%。
    # 嘴的形状不抄进这里——直接把着色器里那段 GLSL 搬成 JS 跑，免得一份内容抄两处。
    m_cam_el = re.search(r'cam:\s*\{[^}]*\bel:\s*([-0-9.]+)', src)
    m_band = re.search(r'/\* 嘴：.*?\*/\s*(float m = 0\.0;.*?)\n\s*col = mix\(col, C_INK, [0-9.]+ \* m \* on\);',
                       src, re.S)
    m_on = re.search(r'float on = ss\(([0-9.]+),\s*([0-9.]+), f\);', src)
    m_hc = re.search(r'var HC = \[([^\]]+)\];', src)
    m_hr = re.search(r'headR:\s*([0-9.]+) \* s', src)
    m_edge = re.search(r'smoothstep\(([0-9.]+),\s*([0-9.]+), edge\)', src)
    if shutil.which('node') is None:
        warn('W10', '本机没有 node，跳过"嘴会不会被描边吞掉"的实测')
    elif not (m_cam_el and m_band and m_on and m_hc and m_hr and m_edge and m_yaw and m_turn):
        check('W10', False, '找不到默认仰角／嘴的那段着色器／脑袋参数 —— 量不了')
    else:
        blk = None
        for b in blocks:
            if 'var RABBIT' in b and 'function build' in b:
                blk = b
                break
        # GLSL → JS：五条替换，改不动就让 node 当场语法错（宁可红，不可默默量错）
        js = re.sub(r'length\(vec2\((.*?)\)\)', r'Math.hypot(\1)', m_band.group(1))
        js = (js.replace('float ', 'let ')
                .replace('abs(', 'Math.abs(')
                .replace('max(', 'Math.max(')
                .replace('st.x', 'st[0]').replace('st.y', 'st[1]'))
        el0 = float(m_cam_el.group(1))
        az0 = num(m_yaw.group(1)) - num(m_turn.group(1))
        hc = [float(x) for x in m_hc.group(1).split(',')]
        probe_tpl = '''
const R=require(%%r);const HC=%s, HR=%f, YAW=%f, AZ=%f, EL=%f;
const ON=[%f,%f], EDGE=[%f,%f];
function ss(a,b,x){let t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t);}
function mask(st){%s
 return m;}
const m=R.build(0.018), P=m.pos, N=m.nrm;
const d=[Math.cos(EL)*Math.sin(AZ),-Math.cos(EL)*Math.cos(AZ),Math.sin(EL)];
const c=Math.cos(-YAW), s=Math.sin(-YAW);
const dm=[d[0]*c-d[1]*s, d[0]*s+d[1]*c, d[2]];        // 转回图纸坐标（兔子转了 YAW）
let tot=0, band=0, dark=0, n=0;
for(let i=0;i<P.length;i+=3){
  const h=[P[i]-HC[0],P[i+1]-HC[1],P[i+2]-HC[2]], hl=Math.hypot(h[0],h[1],h[2]);
  if(hl>HR||hl<1e-5) continue;
  const st=[h[0]/hl,h[2]/hl], f=-h[1]/hl;
  if(f<ON[0]) continue;
  const w=mask(st)*ss(ON[0],ON[1],f);
  if(w<0.10) continue;
  const nl=Math.hypot(N[i],N[i+1],N[i+2])||1;
  const vis=Math.abs((N[i]*dm[0]+N[i+1]*dm[1]+N[i+2]*dm[2])/nl);
  tot+=w; n++;
  if(1-vis>EDGE[0]) band+=w;                          // 描边开始往上抹的地方（edge = 1 − |n·V|）
  if(ss(EDGE[0],EDGE[1],1-vis)>0.5) dark+=w;          // 抹掉一半以上，等于没有嘴
}
console.log(JSON.stringify({n:n, band:tot?band/tot:0, dark:tot?dark/tot:0}));
''' % (hc, float(m_hr.group(1)), num(m_yaw.group(1)), az0, el0,
       float(m_on.group(1)), float(m_on.group(2)),
       float(m_edge.group(1)), float(m_edge.group(2)), js)
        if blk is None:
            check('W10', False, '找不到 RABBIT 模块，量不了')
        else:
            with tempfile.TemporaryDirectory() as d:
                mod = os.path.join(d, 'rab.js')
                open(mod, 'w', encoding='utf-8').write(blk)
                r = subprocess.run(['node', '-e', probe_tpl % mod],
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    check('W10', False, '量不成：' + r.stderr.strip()[-160:])
                else:
                    g = json.loads(r.stdout)
                    check('W10', g['n'] > 20 and g['dark'] <= 0.02,
                          '默认仰角 %.2f 下，嘴的 %d 个墨点里 %.0f%% 贴进描边带、'
                          '%.0f%% 被抹黑过半（要 ≤2%%；仰角 0.35 时被抹黑的是 29%%，'
                          '用户当场说"嘴巴看不清楚"）'
                          % (el0, g['n'], 100 * g['band'], 100 * g['dark']))

    # ---- [W11] 默认视角下，三根轴的字必须都在画框里 ----
    # 2026-08-06 用户第二次报同一族毛病（第一次是轴名字 X／Y／Z 飘出去，收进 0.72×AX 解决，
    # 见 [W7]）：这回掉出去的是**轴端那串落点标注**「Y → (0, 1, 0)」——
    # Y 轴几乎水平朝右、又是最长的一根，端点还在框内，画在它右边的字已经出去了。
    # 判据钉在**宽屏那一档画框**上：.wrap max-width 1400 − padding 40 → 1360，
    # 减去 gap 18 之后按 1.35fr : 0.9fr 分，画布宽 ≈ 805；高 min(72vh, 640) → 640。
    # 字宽用估的（13px 无衬线，「X → (1, 0, 0)」这类 13 个字符 ≈ 88px，含 fillRect 的边距）——
    # 估得偏大一点是有意的：宁可早一步报，也不要让字贴着框边过关。
    W_PX, H_PX, TXT_PX = 805, 640, 88
    m_ax = re.search(r'var AX = ([0-9.]+);', src)
    m_dist = re.search(r'cam:\s*\{[^}]*\bdist:\s*([0-9.]+)', src)
    m_tgt = re.search(r'cam:\s*\{[^}]*\btarget:\s*\[([^\]]+)\]', src)
    m_fov = re.search(r'm4perspective\((\d+) \* Math\.PI / 180', src)
    m_lbl = re.search(r"addLabel\(LA\.vscale\(a\.v,\s*AX\s*\*\s*([0-9.]+)\),\s*a\.letter", src)
    m_px = re.search(r'var AXLBL_PX = (\d+);', src)
    if not (m_ax and m_dist and m_tgt and m_fov and m_lbl and m_px and m_cam_el and m_yaw and m_turn):
        check('W11', False, '找不到 AX／cam／fov —— 算不了画框')
    else:
        ax, dist = float(m_ax.group(1)), float(m_dist.group(1))
        tgt = [float(x) for x in m_tgt.group(1).split(',')]
        el, az = float(m_cam_el.group(1)), num(m_yaw.group(1)) - num(m_turn.group(1))
        fov, lblr, lblpx = math.radians(float(m_fov.group(1))), float(m_lbl.group(1)), int(m_px.group(1))
        eye = [tgt[0] + dist * math.cos(el) * math.sin(az),
               tgt[1] - dist * math.cos(el) * math.cos(az),
               tgt[2] + dist * math.sin(el)]
        zc = [eye[i] - tgt[i] for i in range(3)]
        n = math.hypot(*zc); zc = [c / n for c in zc]
        xc = [-zc[1], zc[0], 0.0]                      # up = (0,0,1) 叉 z
        n = math.hypot(*xc); xc = [c / n for c in xc]
        yc = [zc[1] * xc[2] - zc[2] * xc[1], zc[2] * xc[0] - zc[0] * xc[2],
              zc[0] * xc[1] - zc[1] * xc[0]]
        ff = 1 / math.tan(fov / 2)

        def screen(p):
            v = [p[i] - eye[i] for i in range(3)]
            w = -sum(zc[i] * v[i] for i in range(3))
            if w <= 1e-4:
                return None
            sx = sum(xc[i] * v[i] for i in range(3)) * ff / (W_PX / H_PX) / w
            sy = sum(yc[i] * v[i] for i in range(3)) * ff / w
            return ((sx * 0.5 + 0.5) * W_PX, (1 - (sy * 0.5 + 0.5)) * H_PX)

        out, worst = [], 0.0
        for i, letter in enumerate('XYZ'):
            e = [0.0, 0.0, 0.0]; e[i] = 1.0
            tip = screen([c * ax for c in e])           # 轴端：落点标注画在它右边
            nam = screen([c * ax * lblr for c in e])    # 轴名字：居中，再往上抬一个字高
            if tip is None or nam is None:
                out.append(letter + ' 在镜头后'); continue
            right = tip[0] + TXT_PX
            worst = max(worst, right / W_PX)
            if right > W_PX or tip[0] < 0 or not (0 <= tip[1] <= H_PX):
                out.append('%s 的落点标注右边缘 %.0f / 画框 %d' % (letter, right, W_PX))
            if not (14 <= nam[0] <= W_PX - 14) or not (0 <= nam[1] - lblpx <= H_PX):
                out.append('%s 这个字母出框（%.0f, %.0f）' % (letter, nam[0], nam[1] - lblpx))
        check('W11', not out,
              '默认视角（dist %.2f）下三根轴的字都在宽屏画框 %d×%d 里%s；'
              '最挤的一根占到画框宽的 %.0f%%（用户 08-06 报过 Y 被切）'
              % (dist, W_PX, H_PX, '' if not out else ' —— ' + '；'.join(out), 100 * worst))

    print()
    if fails:
        print('✗ %d 项未通过：%s' % (len(fails), ' '.join(fails)))
        return 1
    # 项数从实际跑过的条数点出来，不写死——写死的数字会过期，而且没有任何东西会报警（教训 12）
    print('✓ 全部通过（%d 项检查%s）' % (len(done), '，%d 项跳过' % len(warns) if warns else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT))
