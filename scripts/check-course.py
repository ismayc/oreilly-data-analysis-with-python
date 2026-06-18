#!/usr/bin/env python3
"""Lint each O'Reilly course repo against the house conventions in CHECKLIST.md.

This is the structural companion to `check-online-links.py` (which verifies the
Colab/Binder links resolve). It catches the drift that creeps into course repos:
a missing required file, a leftover `<<PLACEHOLDER>>` token from the template, a
Colab badge still pointing at the repo you copied from, or render byproducts
(`*.quarto_ipynb_N`, `Untitled.ipynb`, ...) that got committed by accident.

Findings come at two levels:
  FAIL  breaks the course or ships wrong material  -> non-zero exit
  WARN  drift / clutter worth fixing               -> non-zero exit only with --strict

For each course repo it checks:
  - required files present (the core every course has)
  - recommended files present (netlify.toml, the build-app workflow, built .ipynb, ...)
  - no leftover `<<TOKEN>>` placeholders in the top-level text files
  - every Colab link in README.md / index.html uses THIS repo's slug (not the
    repo it was copied from)
  - no render-byproduct / scratch files committed to git (FAIL) or left in the
    working tree (WARN): *.quarto_ipynb*, Untitled*.ipynb, test.qmd, *with_notes*
  - .gitignore carries the iCloud/Dropbox duplicate-file guard (the `[0-9]` rule)

Usage:
  scripts/check-course.py                  # all sibling oreilly-* course repos
  scripts/check-course.py PATH [PATH ...]  # specific repo dirs
  scripts/check-course.py --strict         # treat WARN as failure too

Exit status is non-zero if any FAIL (or any WARN under --strict). Standard library only.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

GH_OWNER = "ismayc"

# Files every course repo must have. Missing -> FAIL.
REQUIRED_FILES = (
    "README.md",
    "requirements.txt",
    "exercises.qmd",
    "exercises_solutions.qmd",
    "exercises_solutions_with_notes.qmd",
    "slides.pdf",
    ".github/workflows/render-solutions.yml",
)

# Files a complete course has but that vary slightly. Missing -> WARN.
RECOMMENDED_FILES = (
    "exercises.ipynb",
    "exercises_solutions.ipynb",
    "exercises_solutions.html",
)

# Recommended only for in-browser courses (the ones with a Quarto Live / JupyterLite
# app/). A Colab-only / static course like the deep-learning one intentionally has
# neither, so don't warn there. A course is "in-browser" if it has a live/ or app/ dir.
IN_BROWSER_FILES = (
    "netlify.toml",
    ".github/workflows/build-app.yml",
)

# Top-level files to scan for leftover placeholder tokens.
TOKEN_SCAN_NAMES = ("README.md", "index.html", "netlify.toml")
TOKEN_SCAN_GLOBS = ("*.qmd",)
TOKEN_RE = re.compile(r"<<[A-Za-z0-9_]+>>")

# Files we scan for Colab links that must match this repo's slug.
COLAB_SCAN_NAMES = ("README.md", "index.html")
COLAB_RE = re.compile(
    r"https://colab\.research\.google\.com/github/"
    r"(?P<owner>[^/\s]+)/(?P<repo>[^/\s]+)/blob/"
)

# Render byproducts / scratch files that should never be committed. Tracked -> FAIL,
# merely present in the working tree -> WARN. (The template .gitignore already lists
# these; this catches the ones that slipped in before the ignore rule, or got force-added.)
# NOTE: this is deliberately NOT the full .gitignore set -- the *_with_notes.* source and
# the *.pptx deck are legitimate local-only files, so flagging them every run is noise.
JUNK_GLOBS = (
    "*.quarto_ipynb_*",
    "*.quarto_ipynb",
    "Untitled*.ipynb",
    "test.qmd",
)


def repo_default_dirs():
    """Sibling oreilly-* course repos (this script lives in oreilly-tools/scripts/)."""
    workspace = Path(__file__).resolve().parents[2]
    dirs = []
    for p in sorted(workspace.glob("oreilly-*")):
        if p.is_dir() and p.name != "oreilly-tools":
            dirs.append(p)
    return dirs


def read_text(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def tracked_files(repo: Path):
    """Set of paths (relative, as strings) git is tracking, or None if not a git repo."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "ls-files"],
            capture_output=True, text=True, timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return set(line for line in out.stdout.splitlines() if line)


def check_repo(repo: Path):
    """Return a list of (level, message) findings for one course repo."""
    findings = []
    slug = repo.resolve().name   # resolve so a target of "." (CI) yields the real dir name

    # 1. Required / recommended files.
    for rel in REQUIRED_FILES:
        if not (repo / rel).is_file():
            findings.append(("FAIL", f"missing required file: {rel}"))
    for rel in RECOMMENDED_FILES:
        if not (repo / rel).is_file():
            findings.append(("WARN", f"missing recommended file: {rel}"))
    in_browser = (repo / "live").is_dir() or (repo / "app").is_dir()
    if in_browser:
        for rel in IN_BROWSER_FILES:
            if not (repo / rel).is_file():
                findings.append(("WARN", f"missing recommended file (in-browser course): {rel}"))

    # 2. Leftover placeholder tokens.
    scan = [repo / n for n in TOKEN_SCAN_NAMES]
    for pat in TOKEN_SCAN_GLOBS:
        scan.extend(sorted(repo.glob(pat)))
    for f in scan:
        if not f.is_file():
            continue
        tokens = sorted(set(TOKEN_RE.findall(read_text(f))))
        if tokens:
            findings.append(("FAIL", f"leftover template token(s) in {f.name}: {', '.join(tokens)}"))

    # 3. Colab links must use this repo's own slug.
    for name in COLAB_SCAN_NAMES:
        f = repo / name
        if not f.is_file():
            continue
        for m in COLAB_RE.finditer(read_text(f)):
            owner, linked = m["owner"], m["repo"]
            if linked != slug:
                findings.append(
                    ("FAIL", f"Colab link in {name} points at {owner}/{linked}, expected {GH_OWNER}/{slug}")
                )
            elif owner != GH_OWNER:
                findings.append(
                    ("WARN", f"Colab link in {name} uses owner {owner}, expected {GH_OWNER}")
                )

    # 4. Junk / scratch files: FAIL (per file) if tracked, WARN (collapsed) if just
    # sitting in the working tree gitignored.
    tracked = tracked_files(repo)
    committed_junk, loose_junk = [], []
    seen_junk = set()
    for pat in JUNK_GLOBS:
        for f in repo.glob(pat):
            rel = f.relative_to(repo).as_posix()
            if rel in seen_junk:
                continue
            seen_junk.add(rel)
            if tracked is not None and rel in tracked:
                committed_junk.append(rel)
            else:
                loose_junk.append(rel)
    for rel in sorted(committed_junk):
        findings.append(("FAIL", f"render byproduct / scratch file committed: {rel}"))
    if loose_junk:
        sample = ", ".join(sorted(loose_junk)[:3])
        extra = f" (+{len(loose_junk) - 3} more)" if len(loose_junk) > 3 else ""
        findings.append(("WARN", f"{len(loose_junk)} gitignored render byproduct(s) in tree: {sample}{extra}"))

    # 5. .gitignore duplicate-file guard (the iCloud/Dropbox "foo 2.csv" pattern).
    gi = repo / ".gitignore"
    if gi.is_file():
        if "[0-9]" not in read_text(gi):
            findings.append(("WARN", ".gitignore is missing the duplicate-file guard (a `[0-9]` rule)"))
    else:
        findings.append(("WARN", "no .gitignore"))

    return findings


def main(argv):
    args = [a for a in argv[1:] if a != "--strict"]
    strict = "--strict" in argv[1:]

    targets = [Path(a) for a in args] or repo_default_dirs()
    if not targets:
        print("No course repos found to check.", file=sys.stderr)
        return 2

    workspace = Path(__file__).resolve().parents[2]
    total_fail = total_warn = 0
    repos_with_fail = 0

    for repo in targets:
        findings = check_repo(repo)
        try:
            label = repo.relative_to(workspace)
        except ValueError:
            label = repo
        print(label)
        if not findings:
            print("  [OK  ] clean")
        for level, msg in findings:
            print(f"  [{level}] {msg}")
        fails = sum(1 for lvl, _ in findings if lvl == "FAIL")
        warns = sum(1 for lvl, _ in findings if lvl == "WARN")
        total_fail += fails
        total_warn += warns
        if fails:
            repos_with_fail += 1

    print()
    print(f"{len(targets)} repo(s) checked: {total_fail} FAIL, {total_warn} WARN "
          f"({repos_with_fail} repo(s) failing).")

    if total_fail or (strict and total_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
