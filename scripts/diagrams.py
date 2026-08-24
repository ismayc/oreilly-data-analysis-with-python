#!/usr/bin/env python3
"""Turn the .qmd's Quarto ```{mermaid} diagrams into PNGs the notebooks can show.

The HTML site renders mermaid natively (vector, live), so the .qmd stays on
native ```{mermaid}``` fences. Notebook front-ends are the problem: Colab's
markdown engine has no mermaid support at all, so a fenced block there shows as
raw text. This module pre-renders each diagram to a PNG and swaps in an <img>.

- PNGs live in assets/diagrams/, named by content hash (diagram-<sha256[:12]>.png),
  so identical diagrams dedupe and a rebuild produces the same name unless the
  diagram source actually changed.
- Notebooks reference them from raw.githubusercontent.com on the `main` branch,
  which is what Colab, GitHub, and nbviewer all resolve. The links go live once
  the PNGs are pushed to main.
- Each is wrapped centered at DIAGRAM_DISPLAY_SCALE of its natural width:
  diagrams render at 2x for crisp text, then display smaller so they don't
  dominate the notebook.

A diagram is only re-rendered when its PNG is MISSING, so a routine rebuild needs
no browser. Rendering a new or changed diagram needs mermaid-cli (`mmdc`) plus a
Chrome/Chromium:

    npm install -g @mermaid-js/mermaid-cli       # provides `mmdc`
    npx puppeteer browsers install chrome        # or point at a system Chrome
    export PUPPETEER_EXECUTABLE_PATH=/path/to/chrome   # if not auto-detected

Override the mmdc binary with the MMDC env var if it isn't on PATH.
"""
import hashlib
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

REPO = "ismayc/oreilly-data-analysis-with-python"
BRANCH = "main"
ROOT = Path(__file__).resolve().parent.parent
DIAGRAMS_DIR = ROOT / "assets" / "diagrams"
DIAGRAM_DISPLAY_SCALE = 0.6
PUPPETEER_CFG = ROOT / "scripts" / "puppeteer-config.json"


def diagram_name(code):
    return "diagram-" + hashlib.sha256(code.encode("utf-8")).hexdigest()[:12] + ".png"


def diagram_raw_url(name):
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/assets/diagrams/{name}"


def render_diagram(code, out_path):
    """Render mermaid source to a PNG with mermaid-cli."""
    mmdc = os.environ.get("MMDC", "mmdc")
    DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    src = out_path.with_suffix(".mmd")
    src.write_text(code + "\n")
    cmd = [mmdc, "-i", str(src), "-o", str(out_path), "-b", "white", "-s", "2"]
    if PUPPETEER_CFG.exists():
        cmd += ["-p", str(PUPPETEER_CFG)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit(f"error: '{mmdc}' not found. Install mermaid-cli to render new "
                 f"diagrams (see this module's header), or set MMDC.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"error rendering {out_path.name}:\n{e.stderr or e.stdout}")
    finally:
        src.unlink(missing_ok=True)


def png_width(path):
    """Pixel width from the PNG IHDR header (avoids a Pillow dependency)."""
    return struct.unpack(">I", path.read_bytes()[16:20])[0]


def mermaid_to_image(code, allow_render=True):
    """Return a centered <img> for `code`, rendering its PNG if it is missing.

    With allow_render=False a missing PNG returns None instead of shelling out
    to mermaid-cli, so a caller running somewhere without a browser (CI) can
    fall back rather than fail.
    """
    name = diagram_name(code)
    out_path = DIAGRAMS_DIR / name
    if not out_path.exists():
        if not allow_render:
            return None
        render_diagram(code, out_path)
    width = round(png_width(out_path) * DIAGRAM_DISPLAY_SCALE)
    return (f'<div align="center"><img src="{diagram_raw_url(name)}" '
            f'alt="Mermaid diagram" width="{width}"></div>')


def rewrite_markdown(text, allow_render=True):
    """Strip the HTML-only <style> block and swap mermaid fences for images.

    Returns the rewritten text; an empty result means the cell held nothing but
    the CSS block and the caller should drop it. When a PNG is missing and
    allow_render is False, the fence is left as plain ```mermaid, which at least
    renders on GitHub and in JupyterLab.
    """
    def _fix(m):
        body = "\n".join(ln for ln in m.group(1).split("\n")
                         if not ln.lstrip().startswith("%%|")).strip("\n")
        img = mermaid_to_image(body, allow_render)
        return img if img else "```mermaid\n" + body + "\n```"

    text = re.sub(r'```\{=html\}\n<style>.*?</style>\n```\n*', '', text, flags=re.S)
    return re.sub(r'```\{mermaid\}\n(.*?)\n```', _fix, text, flags=re.S)
