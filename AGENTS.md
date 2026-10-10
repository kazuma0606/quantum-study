# Codex guidance for quantum

This repository connects mathematical notes, executable checks, visualizations, quantum experiments, and Lean proofs. Start with `README.md` and the relevant local README; use `REQUIREMENTS.md` for the note and notebook map.

## Layout and commands

- `研究ノート/`: mathematical and physical explanations in Markdown.
- `notebooks/`: generated Jupyter notebooks and supporting implementations.
- `experiments/`: simulation, hardware data, tests, and result logs.
- `lean4/`: Lean 4 / Mathlib project; its README records the toolchain and build commands.
- `docs/`: plans and research context; `tools/`: local checks and generators.
- Python dependencies are managed with `uv`; run focused checks with `uv run ...` when needed. Some experiment batches and notebooks are costly, so inspect their scope before running them.

## Working in a shared tree

- Claude Code and the user may edit this tree concurrently. Inspect `git status` and the target diff before editing. Preserve unrelated edits and live experiment outputs; avoid writing to `experiments/**/results/` during a review.
- When reviewing a note, report findings with file and line, a derivation or counterexample, and a proposed correction. Distinguish a checked equation, a numerical spot check, a cited theorem, and an unverified claim. Keep reviews read-only unless the user requests edits.
- For numerical claims, compare the note with the implementation and stored result that produced the number. State assumptions and the range in which an approximation or scaling law applies.
- Do not submit quantum hardware jobs or incur cloud charges without the user's explicit authorization for the specific run. Prepare the circuit, costs or time estimate, dry run, and output plan first.
- Do not commit or push unless requested. Stage only files belonging to the requested change.
- `研究ノート/02_微分幾何/christoffel_riemann_intro.md` is under manual review; edit it only when specifically requested.

## Task-specific workflows

Use the repository skills in `.agents/skills/` for note review, note writing, notebook generation, figures, and quantum experiments when their descriptions match the task. The project agents in `.codex/agents/` are optional specialists for bounded delegated work, not a required step for ordinary tasks.
