---
name: note-figures
description: Create or revise matplotlib figures for a Markdown research note in 研究ノート/, including the generating script and visual check. Use when the requested note work needs a new or changed figure.
---

# Figures for research notes

Keep the generating script beside its note in `figures/make_<topic>_figures.py` and use a distinct prefix for output names. Follow nearby scripts for Japanese fonts, mathtext, sizing, and naming.

Check values in the figure against the cited equation or numerical result before saving. Use assertions for deterministic quantities when helpful; choose statistical tolerances from the calculation. Record the relevant equation number near its code so later renumbering can be traced.

Generate only the requested figures, then inspect the actual image for clipped labels, crowded ticks, overlapping text, and incorrect formulas. Confirm the Markdown link resolves. Report the generating command and what the numerical and visual checks established.
