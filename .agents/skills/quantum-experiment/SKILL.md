---
name: quantum-experiment
description: Plan, implement, or analyze a quantum simulation or hardware experiment under experiments/, with reproducible inputs, counterexample tests, and results. Use for quantum experiment work, especially jobs on IBM Quantum or AWS Braket.
---

# Quantum experiments

Read the theme in `docs/research_ideas.md`, the experiment README, and existing scripts before changing the experiment. State the physical question, observable, ideal reference, noise model, and what result would falsify the hypothesis.

- Prefer a small analytical or numerical prediction, then an independent simulator check, before a hardware run. Use tests to fix discovered counterexamples as well as expected behavior.
- Keep calculation code, tests, and result data separate. Record run arguments, seed, library versions, backend and time, shots, transpiled circuit depth and two-qubit gate count, qubit mapping, and calibration data when applicable. Preserve prior outputs and live batch logs.
- Compare the exact ideal value, noiseless circuit value, and noisy or measured value with signed differences and uncertainty. State limits of model identifiability and distinguish fitted from held-out evidence.
- For an IBM or AWS hardware run, first prepare a reviewable dry run, estimated device time or cost, circuit count, shot count, output paths, and any spending limit checks. Submit only after the user explicitly authorizes that run. Credentials stay outside the conversation and repository.

Report the result, verification, and unresolved alternatives. Do not make a hardware or cloud submission as a side effect of analysis.
