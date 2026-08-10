# DaisyProbability 交付

本机 `~/DaisyProbability` 是权威源码。`./publish.sh` 只构建和校验第四册，不碰 Drive；`./publish.sh --upload` 只上传第四册 Doc、第四册稿件、DaisyProbability 手册和本项目源码包。

现有 Google Doc 目标路径由 `project.conf` 固定。不要用全系列旧脚本，也不要替另外两个 Daisy 项目上传。

`--upload` 收尾会把 Drive 上的本项目 Google Doc 导出成 PDF 存进 `数学概念笔记/05-成书PDF/`（md5 自动核对）；不重建、只刷新 PDF 用 `./publish.sh --pdf`。
