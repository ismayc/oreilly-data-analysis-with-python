#!/usr/bin/env python3
"""Tidy quarto-converted notebooks for a plain Jupyter / JupyterLite audience:

- Replace the leading YAML front-matter cell (quarto convert emits it as a
  markdown cell of literal `--- ... ---`) with a simple title/author cell.
- Strip Quarto cell directives (lines starting with `#|`, e.g. `#| eval: false`,
  `#| include: false`) -- they are meaningful in a .qmd but are just noise in a
  Jupyter notebook. The code cells themselves are kept.

Usage: clean-notebooks.py nb1.ipynb [nb2.ipynb ...]
"""
import json
import re
import sys


def field(name, text):
    m = re.search(rf'^{name}:\s*(.+?)\s*$', text, re.M)
    if not m:
        return ""
    v = m.group(1).strip()
    if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
        v = v[1:-1]
    return v


for path in sys.argv[1:]:
    nb = json.load(open(path, encoding="utf-8"))
    cells = nb.get("cells", [])

    # 1. Replace a leading YAML front-matter markdown cell with a title cell.
    if cells and cells[0].get("cell_type") == "markdown":
        src = "".join(cells[0].get("source", []))
        if src.lstrip().startswith("---"):
            parts = src.split("---")
            yaml = parts[1] if len(parts) > 1 else ""
            title, author = field("title", yaml), field("author", yaml)
            md = []
            if title:
                md.append(f"# {title}\n")
            if author:
                md.append("\n")
                md.append(f"*{author}*\n")
            if md:
                cells[0] = {"cell_type": "markdown", "metadata": {}, "source": md}
            else:
                cells.pop(0)

    # 2. Strip Quarto `#|` directive lines from code cells.
    for c in cells:
        if c.get("cell_type") == "code":
            c["source"] = [ln for ln in c.get("source", [])
                           if not ln.lstrip().startswith("#|")]

    nb["cells"] = cells
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
        f.write("\n")
