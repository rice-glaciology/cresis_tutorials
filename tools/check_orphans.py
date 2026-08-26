#!/usr/bin/env python3
"""Fail if a page under docs/ is missing from the `nav:` block in mkdocs.yml.

`mkdocs build --strict` does NOT catch this: an orphaned page still builds and
is still reachable by URL, it just never appears in the navigation, so nobody
finds it. Verified against mkdocs 1.6.1 / material 9.7.

Non-page assets (scripts, images, javascript) are ignored.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CONFIG = ROOT / "mkdocs.yml"

# Directories under docs/ that hold assets rather than nav pages.
ASSET_DIRS = {"scripts", "javascripts", "stylesheets", "images", "assets"}


class _Loader(yaml.SafeLoader):
    """Tolerate mkdocs' custom YAML tags (e.g. !!python/name:)."""


def _ignore_unknown(loader, tag_suffix, node):  # noqa: ANN001
    return None


_Loader.add_multi_constructor("tag:yaml.org,2002:python/name:", _ignore_unknown)
_Loader.add_multi_constructor("!", _ignore_unknown)


def nav_targets(nav) -> set[str]:
    """Collect every markdown path referenced anywhere in the nav tree."""
    found: set[str] = set()
    if isinstance(nav, str):
        if nav.endswith(".md"):
            found.add(nav)
    elif isinstance(nav, list):
        for item in nav:
            found |= nav_targets(item)
    elif isinstance(nav, dict):
        for value in nav.values():
            found |= nav_targets(value)
    return found


def main() -> int:
    config = yaml.load(CONFIG.read_text(), Loader=_Loader)
    listed = nav_targets(config.get("nav", []))

    on_disk = {
        str(p.relative_to(DOCS))
        for p in DOCS.rglob("*.md")
        if not set(p.relative_to(DOCS).parts[:-1]) & ASSET_DIRS
    }

    orphans = sorted(on_disk - listed)
    dangling = sorted(listed - on_disk)

    for path in dangling:
        print(f"nav references a missing file: {path}", file=sys.stderr)
    for path in orphans:
        print(f"page is not in the nav: docs/{path}", file=sys.stderr)

    if orphans or dangling:
        print(
            f"\n{len(orphans)} orphaned page(s), {len(dangling)} dangling nav entry"
            f"(ies). Add them to `nav:` in mkdocs.yml or delete them.",
            file=sys.stderr,
        )
        return 1

    print(f"nav check: {len(on_disk)} pages, all in nav")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
