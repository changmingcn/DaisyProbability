# DaisyProbability project boundary

This directory is the complete and independent source repository for the probability project. Its book source is under `vol4/`.

- The only authoritative handoff manual is `manuals/DaisyProbability.md`.
- Do not read or modify `../DaisyCalculus`, `../DaisyAlgebra`, or the legacy `../math-notes` monorepo unless the user explicitly requests cross-project work.
- A request about consistency, terminology, or delivery applies only here unless the user explicitly names another Daisy project.
- Run Git only in this repository. Stage explicit paths; never use `git add -A` as a default.
- `./publish.sh` and `./publish.sh --vol vol4` build and verify the MathJax HTML book only; they never generate DOCX or PDF. `./publish.sh --upload` uploads only this project's four raw delivery files (HTML, manuscript, manual, source package).
- DOCX, Google Doc conversion, and PDF publication are retired. Historical artifacts and legacy code may remain, but must not be invoked by the active pipeline.
- `~/.claude/agents/DaisyProbability.md` must be hard-linked only to `manuals/DaisyProbability.md`; repair it with `./publish.sh --relink`.

Historical statements in the manual such as “three manuals use the same rule” record a past decision. They do not authorize reading or synchronizing sibling repositories now.
