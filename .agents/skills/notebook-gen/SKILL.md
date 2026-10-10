---
name: notebook-gen
description: Create or revise a Jupyter notebook under notebooks/ using its repository generator, then execute and inspect it. Use for notebook implementation or visualization work, not for reviewing a Markdown note.
---

# Generate notebooks

Edit the appropriate `tools/notebook_generators/make_<topic>.py` and regenerate the `.ipynb`; keep saved notebook outputs empty and cell IDs stable. Follow the nearby notebook generator and folder README for imports, links, and structure. Put substantive numerical logic in reusable functions where the existing folder does so, and check important equations with meaningful assertions.

For Plotly `FigureWidget`, pass Python lists to traces instead of NumPy arrays, and do not reuse a widget variable name for a different figure. After generation, execute the notebook into a temporary output directory with `jupyter nbconvert`, run `tools/check_widget_arrays.py` when widgets are present, and inspect rendered figures or screenshots when visual behavior matters. Keep generated execution outputs out of the tracked notebook.

Report the generator and notebook changed, the execution command and result, and any visualization that was not interactively verified.
