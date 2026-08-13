# DaisyProbability

Independent repository for 《给小学生讲概率论》.

- Book source: `vol4/`
- Primary book layout: `vol4/html/给小学生讲概率论.html` (generated; all math via MathJax)
- Handoff manual: `manuals/DaisyProbability.md`
- Local verification: `./publish.sh`
- One-volume verification: `./publish.sh --vol vol4`
- Source-content verification: `python3 verify_content.py vol4`
- HTML-only verification: `python3 verify_html.py vol4`

The reader-facing build is HTML only. DOCX, Google Doc conversion, and PDF
generation are retired; older artifacts may remain as history but are not rebuilt.

The former combined repository remains at `~/math-notes` only as a migration rollback copy. It is not an editing source.
