#!/usr/bin/env python3
"""Build Colab-ready .ipynb notebooks from the source .qmd files.

Adapted for this course from oreilly-tools/repo-template/scripts/build-notebooks.py.
For each committed qmd we:
  1. `quarto convert` it to a notebook,
  2. drop the YAML front-matter cell and prepend a title cell,
  2b. clean markdown cells: drop HTML-only <style> blocks and rewrite Quarto
      ```{mermaid} fences to plain ```mermaid so GitHub renders the diagrams,
  3. make the pip cell robust for a fresh Colab runtime,
  4. strip Quarto `#|` directive lines (noise in a plain notebook),
  5. clear outputs / execution counts and set a clean kernelspec.

Usage:  python3 scripts/build-notebooks.py
Requires: quarto on PATH.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGETS = [
    ("exercises.qmd", "exercises.ipynb"),
    ("exercises_solutions.qmd", "exercises_solutions.ipynb"),
]


def title_cell():
    return {"cell_type": "markdown", "metadata": {}, "source": [
        "# Walkthroughs and Exercises for Data Analysis with Python\n",
        "\n",
        "**Dr. Chester Ismay**\n",
        "\n",
        "Run the setup cells first, then work top to bottom. On Google Colab the\n",
        "course data files download themselves in the setup cell, so there is\n",
        "nothing to upload.\n",
    ]}


PIP_CELL = [
    "# Run this once if any import below fails.\n",
    "# (Colab already ships most of these packages.)\n",
    "!pip install -q pandas matplotlib seaborn plotly openpyxl\n",
]


def is_yaml_cell(cell):
    src = "".join(cell["source"]).strip()
    return cell["cell_type"] == "markdown" and src.startswith("---") and "title:" in src


def clean(nb_name):
    nb = json.loads(Path(nb_name).read_text())
    cells = [c for c in nb["cells"] if not is_yaml_cell(c)]

    def _fix_mermaid(m):
        body = "\n".join(ln for ln in m.group(1).split("\n")
                         if not ln.lstrip().startswith("%%|"))
        return "```mermaid\n" + body + "\n```"

    kept = []
    for c in cells:
        if c["cell_type"] == "markdown":
            text = "".join(c["source"])
            text = re.sub(r'```\{=html\}\n<style>.*?</style>\n```\n*', '', text, flags=re.S)
            text = re.sub(r'```\{mermaid\}\n(.*?)\n```', _fix_mermaid, text, flags=re.S)
            if not text.strip():
                continue
            c["source"] = text.splitlines(keepends=True)
        kept.append(c)
    cells = kept

    for c in cells:
        if c["cell_type"] == "code":
            c["source"] = [ln for ln in c["source"] if not ln.lstrip().startswith("#|")]
            while c["source"] and c["source"][0].strip() == "":
                c["source"].pop(0)
            c["outputs"] = []
            c["execution_count"] = None

    for c in cells:
        if c["cell_type"] == "code" and any("pip install" in ln for ln in c["source"]):
            c["source"] = list(PIP_CELL)
            break

    cells.insert(0, title_cell())
    nb["cells"] = cells
    nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3"}
    nb["metadata"]["language_info"] = {"name": "python"}
    Path(nb_name).write_text(json.dumps(nb, indent=1))


def main():
    for qmd, ipynb in TARGETS:
        subprocess.run(["quarto", "convert", str(ROOT / qmd),
                        "--output", str(ROOT / ipynb)], check=True)
        clean(ROOT / ipynb)
        print(f"built {ipynb}")


if __name__ == "__main__":
    main()
