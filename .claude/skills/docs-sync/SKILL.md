---
name: docs-sync
description: Instruction of how to do the comparison between code and documentation. Use this skill every time when asked to compare readme, claude, or any PRD file against the code and/or tests.
compatibility: markdown, python, uv
---

When asked to run a doc sync, do the following:

[ ] Read the documentation files in scope (README.md, CLAUDE.md, and any files under `prd-implementation/` or `prd`)
[ ] Read the relevant source files in `src/` and `tests/`
[ ] Identify every mismatch between the docs and the code
[ ] Report all findings before making any edits — see Reporting Format below
[ ] Wait for confirmation, then apply only the approved fixes

---

## Rules

- Update the respective doc to match the code — never the other way around.
- If specific doc files are named in the request, load only those and ignore the rest.
- Do not modify source code or test files.
- Do not infer intent from comments or git history — only compare what is written in the docs against what the code actually does.
- If a discrepancy is ambiguous (docs and code could both be "right"), flag it as needs-human-review instead of auto-fixing.

---

## Reporting Format

Group findings by document. Within each document, show the exact diff needed to fix each mismatch.

After confirmation, apply fixes, then output a short changelog listing each item resolved.
