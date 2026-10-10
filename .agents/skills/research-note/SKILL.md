---
name: research-note
description: Create or revise a mathematical or physical Markdown note in 研究ノート/, including derivations, examples, references, and repository links. Use for note writing or editing, not for a read-only review.
---

# Write a research note

Read the relevant notes and `REQUIREMENTS.md` before changing the target. Preserve the established Japanese `です・ます` style and work through steps that a learner needs to follow. Name matrix entries such as `a_{12}` explicitly; define conventions and the domain of each claim.

- Check central identities before presenting them, using hand derivation and a small symbolic or numerical calculation where useful. State which results are proved, numerically checked, or cited; avoid making a finite check sound universal.
- Follow the target note's structure: title; creation/update dates and short summary; related files; notation; generated table of contents; numbered Parts and equation tags such as `\tag{II-3}`. Keep references to equation numbers in figures and related notes consistent.
- Place figures and notebook work in their own skills when that work is part of the request. Link related notes, implementations, tests, and Lean proofs that actually exist.
- Validate the target with `研究ノート/tools/build_toc.py --check`; run `tools/linkcheck.py` and `tools/scan_bars.py` where relevant. If new sections change the TOC, generate it with `研究ノート/tools/build_toc.py <file>` before checking.
- Update the relevant README entry for a new note. Use `tools/update_md_headers.py --check` to find stale dates; avoid rewriting unrelated files merely to normalize headers.

Report what changed, checks performed, cited but unproved facts, and remaining uncertainty. Preserve concurrent edits; commit or push only on request.
