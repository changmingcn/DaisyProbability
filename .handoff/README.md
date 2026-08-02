# .handoff —— 并发会话的交接暂存

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

本目录不在 publish.sh 的打包清单里，不会随源码包发出去。
