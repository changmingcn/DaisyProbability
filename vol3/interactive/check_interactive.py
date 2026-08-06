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
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, '兔子的线性变换-三维版.html')

fails, warns = [], []


def check(tag, ok, msg):
    print(('  ✓ ' if ok else '  ✗ ') + '[%s] %s' % (tag, msg))
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

    # ---- [W3] 兔子的转角 ＝ 默认镜头方位角 ----
    # 这是"兔子正面朝我们"的全部依据。图纸里兔子脸朝 −y，绕 z 转 YAW 之后
    # 脸朝 (sin YAW, −cos YAW)；镜头在方位角 az 时位于 (sin az, −cos az) 那一侧。
    # 两个数相等，脸才正对镜头。
    m_yaw = re.search(r'var YAW\s*=\s*([^;]+);', src)
    m_az = re.search(r'cam:\s*\{\s*az:\s*([^,]+),', src)
    if not (m_yaw and m_az):
        check('W3', False, '找不到 YAW 或默认 cam.az —— 这两个数是这一页的命门')
    else:
        yaw, az = num(m_yaw.group(1)), num(m_az.group(1))
        d = abs((math.degrees(yaw - az) + 180) % 360 - 180)
        cosface = math.cos(yaw - az)
        check('W3', d < 1e-6,
              '兔子转角 %.3f° ＝ 默认镜头方位角 %.3f°？差 %.4f°（脸朝向·镜头 = %.4f，'
              '差一度兔子就开始转过去）' % (math.degrees(yaw), math.degrees(az), d, cosface))

    # ---- [W4] 视角按钮的基准角也得跟上 ----
    m_btn = re.search(r'var YAW_AZ\s*=\s*([^;]+);', src)
    if not m_btn:
        check('W4', False, '找不到 YAW_AZ —— 三个视角按钮就会各转各的')
    elif m_yaw:
        d = abs(math.degrees(num(m_btn.group(1)) - num(m_yaw.group(1))))
        check('W4', d < 1e-6, '视角按钮基准角对齐兔子转角？差 %.4f°' % d)

    # ---- [W5] 主光在镜头这一侧，脸不能背光 ----
    m_l = re.search(r"'uLight'\s*\),\s*new Float32Array\(\[([^\]]+)\]", src)
    if not (m_l and m_az):
        check('W5', False, '找不到主光方向或镜头方位角')
    else:
        lx, ly, _lz = [float(x) for x in m_l.group(1).split(',')]
        az = num(m_az.group(1))
        fx, fy = math.sin(az), -math.cos(az)          # 兔子脸朝向 ＝ 镜头方位
        c = (lx * fx + ly * fy) / math.hypot(lx, ly)
        check('W5', c > 0.2,
              '主光照得到脸？主光·脸朝向 = %.3f（≤0 就是背光，脸会暗一大截）' % c)

    # ---- [W6] 自包含：上了站也不能去外面要东西 ----
    ext = re.findall(r'(?:src|href)\s*=\s*["\']https?://[^"\']+', src)
    ext = [e for e in ext if 'acme' not in e]
    check('W6', not ext, '页面自包含（不向外网要资源）%s'
          % ('' if not ext else '—— 发现 %d 处：%s' % (len(ext), ext[:3])))

    print()
    if fails:
        print('✗ %d 项未通过：%s' % (len(fails), ' '.join(fails)))
        return 1
    print('✓ 全部通过（%d 项检查%s）' % (6 - len(warns), '，%d 项跳过' % len(warns) if warns else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT))
