---
name: research-note-review
description: Independently review a mathematical or physical Markdown note in 研究ノート/ for incorrect equations, hidden assumptions, numerical mismatches, and gaps in explanation. Use for a requested note review; do not edit the note.
---

# Review a research note

Read the target note, the relevant experiment or notebook, and any cited local derivation. Review in read-only mode.

1. Re-derive important equations independently. Check signs, factors, indices, operator order, basis conventions, and assumptions. Look for counterexamples to words such as "always", "monotone", or "therefore".
2. Recompute representative numbers with a small independent calculation where practical. Separate exact identities, asymptotic estimates, empirical fits, and claims supported only by citations. A passed numerical check is not a proof.
3. Compare cited experimental values and conclusions with the generating code, stored results, and current README. Distinguish a toy model from a hardware conclusion. Verify external scientific claims against primary sources when needed.
4. Check explanation gaps, notation and equation references. For mechanical checks, use `研究ノート/tools/build_toc.py --check`, `tools/linkcheck.py`, and `tools/scan_bars.py` when relevant; treat scanner output as candidates to inspect.

Report actionable findings first, with file:line, the reason, evidence or counterexample, and a precise revision suggestion. End with what was checked and what remains unverified. Do not manufacture findings or silently edit the note.
