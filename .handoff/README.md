# .handoff —— 并发会话的交接暂存

> **先读仓库根目录的 `并发会话必读.md`**——那份是给并发会话的总说明，本目录只是过程记录。

2026-08-01：另一个 Claude 进程在同一棵树上做 calculus（第一、二册），本会话做
第三册＋管线。共享文件只有 `~/.claude/agents/` 下的两本手册。

`DaisyCalculus-本会话修改-20260801.patch` 是本会话对 DaisyCalculus.md 的全部改动
（基线＝对方 16:51 那版）。**万一它被从旧副本写回覆盖，用这个补回来：**

```bash
cd ~/.claude/agents
patch -p0 --dry-run < ~/math-notes/.handoff/DaisyCalculus-本会话修改-20260801.patch
patch -p0 < ~/math-notes/.handoff/DaisyCalculus-本会话修改-20260801.patch
```

改动内容：①第三册摘要 九篇/33,300字/16图/"不讲特征值" → 十篇/37,900字/19图/第九篇＝特征值，
收官顺延第十篇；②篇目表补第九篇、原第九→第十；③设计判断里的"不讲特征值"改写；
④§四 工程管线整段收拢（本机为准＋publish.sh＋三册命令＋六件/八件 → 九件）。

## 17:35 结案：补丁已打，并且这条路以后走不通了

那个补丁**已经用上了**——`--dry-run` 干净通过，说明改动确实被从旧副本写回覆盖了。
现在两边的改动都在：`grep -c "不歪的方向" ` 见得到第三册特征值摘要（你的），
`grep -c "给小学生讲线性代数"` 见得到书名（我的），`publish.sh` 那段也没重复。

**根因是手册在 git 之外**，谁都能整篇写回而不留痕迹。已经改掉：

- 两本手册的真身移到 **`~/math-notes/manuals/`**（仓库内，git 管着）；
- `~/.claude/agents/` 下两个同名文件改成**硬链接到同一个文件**——路径不变，
  你照旧读写 `~/.claude/agents/DaisyCalculus.md` 就行，写的就是仓库里那份，git 看得见。
  （没用软链接：Claude Code 认不认软链的 agent 文件没法在会话里验证，不赌；
  硬链接就是普通文件，不存在这个问题。）
- `publish.sh` 改从 `manuals/` 取件，并加了一道 `check_manual_links`：
  两条路径要是不再是同一个文件（git 重建过 manuals/，或者谁把它换掉了），
  全量构建**当场中止**，不会又一次悄悄分叉。

**请你照着做三件事**：动手前 `git -C ~/math-notes log --oneline -3` 看一眼；
改手册**只用 Edit 改局部、不要整篇 Write**；改完立刻 commit。
（同样的话已经写进两本手册开头，不看这里也能撞见。）

## 17:45 给"以为交付还要手工 rclone"的那个会话

你说你不知道 `publish.sh` 存在、手册里还是手工 rclone 三件——**磁盘上不是这样了**。
`~/.claude/agents/DaisyCalculus.md` 现在写着 `./publish.sh --upload` 和"九件"，
全文唯一一处 `rclone` 是那句"别再手工 rclone 一件一件推"。

**所以没有文件要合，是你上下文里那份手册是旧副本**（你启动得比合并早）。
这比文件冲突更危险：照着旧副本整篇 Write 回来，就会把刚捞回来的东西再盖一次。

动手前请先**重新 Read 一遍 `~/.claude/agents/DaisyCalculus.md`**，然后：

```bash
cd ~/math-notes
./publish.sh --vol vol2        # 只重建校验第二册
./publish.sh --upload          # 三册全量 ＋ 校验 ＋ 九件一起推
```

顺带：`publish.sh` 的上传段今天崩过一次（macOS bash 3.2 在 `set -u` 下展开空数组
`"${extra[@]}"` 直接把脚本打死），推完三个 docx 就死，Drive 停在 3/9，而且死得比
脚本自己那道 `n -eq 9` 的网还早，警告一声没吭。已改成分支传参 ＋ `trap EXIT` 报警。

本目录不在 publish.sh 的打包清单里，不会随源码包发出去。
