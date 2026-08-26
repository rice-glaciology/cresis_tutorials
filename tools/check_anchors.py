#!/usr/bin/env python3
"""Fail if an in-repo link points at a heading anchor that does not exist.

`mkdocs build --strict` validates that a linked *file* exists, but not that the
`#fragment` after it does. So renaming a heading silently breaks every link
into it — the page still loads, it just lands at the top instead of the
section, which nobody notices.

This runs against the BUILT site (site/), so it sees the anchor ids mkdocs
actually generated rather than guessing at slugification rules.

Run `mkdocs build` first; `make check` does this for you.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

ID_RE = re.compile(r'id="([^"]+)"')
HREF_RE = re.compile(r'href="([^"]+#[^"]+)"')


def main() -> int:
    if not SITE.is_dir():
        print("site/ not found — run `mkdocs build` first", file=sys.stderr)
        return 1

    pages = list(SITE.rglob("*.html"))
    ids = {p: set(ID_RE.findall(p.read_text(errors="replace"))) for p in pages}

    broken: list[tuple[str, str]] = []
    checked = 0

    for page in pages:
        html = page.read_text(errors="replace")
        for href in HREF_RE.findall(html):
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, frag = href.partition("#")

            if path in ("", "."):
                target = page
            else:
                candidate = Path(os.path.normpath(page.parent / path))
                target = candidate / "index.html" if candidate.is_dir() else candidate

            if target not in ids:
                continue  # file-level links are mkdocs --strict's job

            checked += 1
            if frag not in ids[target]:
                broken.append((str(page.relative_to(SITE)), href))

    for page, href in broken:
        print(f"anchor does not exist: {href}  <- {page}", file=sys.stderr)

    if broken:
        print(
            f"\n{len(broken)} broken anchor link(s). A heading was probably "
            f"renamed; update the '#fragment' to match.",
            file=sys.stderr,
        )
        return 1

    print(f"anchors: {checked} in-repo anchor link(s), all resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
