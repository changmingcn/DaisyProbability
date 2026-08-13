# DaisyProbability

You are working only on the independent probability project in `~/DaisyProbability`; the book source is at `vol4/`. Read `manuals/DaisyProbability.md` as the sole authoritative handoff.

Hard boundary: do not inspect or change `~/DaisyCalculus`, `~/DaisyAlgebra`, or the archived `~/math-notes` repository unless the user explicitly asks for cross-project work. Do not propagate a new rule, wording, build change, or delivery action to another Daisy project merely for consistency.

Before editing, check this repository's `git status` and recent log. Stage only the paths changed for the current task. Build the MathJax HTML locally with `./publish.sh`; the active pipeline must not generate DOCX, Google Docs, or PDF. Upload the four raw delivery files only when the task authorizes delivery. If the manual is edited, run `./publish.sh --relink` afterward.

The user prefers collaborative design: propose large structural changes first; handle small details directly. Mathematical explanations must pair intuition with rigorous justification, or explicitly record where the debt will be repaid.
