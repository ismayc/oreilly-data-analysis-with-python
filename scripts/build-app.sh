#!/usr/bin/env bash
#
# Rebuild the in-browser course apps from the source notebooks and assemble
# them into app/.
#
#   app/
#   ├── index.html      landing page (from scripts/app-index.html)
#   ├── quarto/         Quarto Live site   (rendered from live/)
#   └── jupyterlite/    JupyterLite site   (built from the .ipynb)
#
# Used both locally and by .github/workflows/build-app.yml.
# Requires: quarto, and a Python 3 (override with PYTHON=/path/to/python3).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYBIN="${PYTHON:-python3}"

# --- 1. Source qmd -> Quarto Live pages (swap python->pyodide, neutralize pip) ---
echo "==> Generating Quarto Live pages"
transform_body () {
  perl -0777 -pe '
    s/\A---\n.*?\n---\n//s;                                               # drop YAML front matter
    s/```\{python[^}\n]*\}/```{pyodide}/g;                                # python cells -> pyodide
    s/^(\s*)!\s*pip install.*/$1# pip install not needed in-browser (packages auto-load)/mg;  # neutralize pip
    s/\A\n+//;                                                            # trim leading blank lines
  ' "$1"
}
cat scripts/headers/exercises-header.md <(echo) <(transform_body exercises.qmd)            > live/exercises.qmd
cat scripts/headers/solutions-header.md <(echo) <(transform_body exercises_solutions.qmd)  > live/solutions.qmd
cp economies.csv economies_indexed.csv populations.csv economies.xlsx populations.xlsx live/

echo "==> Rendering Quarto Live site"
( cd live && rm -rf _site .quarto && quarto render )

# --- 2. Source qmd -> notebooks -> JupyterLite ---
echo "==> Converting qmd -> ipynb (no execution)"
mkdir -p jupyterlite/contents
quarto convert exercises.qmd            --output jupyterlite/contents/exercises.ipynb
quarto convert exercises_solutions.qmd  --output jupyterlite/contents/exercises_solutions.ipynb
# In-browser kernel has no shell: rewrite the !pip cell as an in-kernel %pip install
# (piplite). The Pyodide kernel does NOT auto-load non-core packages (seaborn,
# statsmodels, scikit-learn, plotly, ...), so they must be installed; drop any package
# with no Pyodide/PyPI wheel (e.g. jupyter).
perl -0777 -i -pe 's{!\s*pip install ([^"\\]*)}{my $p=$1;$p=~s/\s+/ /g;$p=~s/^ | $//g;my @k=grep{length&&!/^(jupyter|jupyterlab|notebook|ipykernel)$/}split(/ /,$p);"%pip install -q ".join(" ",@k)}ge' \
  jupyterlite/contents/exercises.ipynb jupyterlite/contents/exercises_solutions.ipynb


# Tidy notebooks for plain Jupyter: drop the YAML cell, strip #| directives
"$PYBIN" scripts/clean-notebooks.py \
  jupyterlite/contents/exercises.ipynb jupyterlite/contents/exercises_solutions.ipynb
cp economies.csv economies_indexed.csv populations.csv economies.xlsx populations.xlsx jupyterlite/contents/

echo "==> Building JupyterLite site"
"$PYBIN" -m venv jupyterlite/.venv
jupyterlite/.venv/bin/python -m pip install -q --upgrade pip \
  jupyterlite-core jupyterlite-pyodide-kernel jupyter-server
rm -rf jupyterlite/_output jupyterlite/.jupyterlite.doit.db
jupyterlite/.venv/bin/jupyter lite build \
  --contents jupyterlite/contents --output-dir jupyterlite/_output

# --- 3. Assemble app/ ---
echo "==> Assembling app/"
rm -rf app/quarto app/jupyterlite app/index.html
mkdir -p app
cp scripts/app-index.html app/index.html
cp -R live/_site        app/quarto
cp -R jupyterlite/_output app/jupyterlite

echo "==> Done. app/ updated ($(find app -type f | wc -l | tr -d ' ') files)."
