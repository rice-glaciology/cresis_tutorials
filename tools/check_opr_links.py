#!/usr/bin/env python3
"""Validate every OPR wiki link against the wiki's real page list.

Roughly two thirds of this wiki's outbound links point at John Paden's OPR
wiki. Checking them with HTTP is unreliable: gitlab.com returns 429 after a few
dozen requests and stays throttled, so a link checker reports failures that are
really rate limiting.

Instead this fetches the page list ONCE from the public API and checks slugs
against it. One request, no rate limiting, and it distinguishes "this page was
renamed" from "gitlab is throttling me" — which HTTP status codes cannot.

Usage:
    check_opr_links.py [--cache PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

API = (
    "https://gitlab.com/api/v4/projects/"
    "openpolarradar%2Fopr/wikis"
)
LINK_RE = re.compile(r"https://gitlab\.com/openpolarradar/opr/-/wikis/([^)\s>\"']+)")


def fetch_slugs(cache: Path | None) -> set[str]:
    if cache and cache.exists():
        print(f"using cached page list: {cache}")
        data = json.loads(cache.read_text())
    else:
        print("fetching OPR wiki page list…")
        with urllib.request.urlopen(API, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        if cache:
            cache.write_text(json.dumps(data))
    return {p["slug"] for p in data}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, default=None,
                    help="cache the page list here to avoid refetching")
    args = ap.parse_args()

    try:
        slugs = fetch_slugs(args.cache)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"could not reach the OPR wiki API ({exc}); skipping", file=sys.stderr)
        return 0  # network trouble is not a repo defect

    # Slugs are matched case-insensitively: GitLab resolves /wikis/home to Home.
    lookup = {s.lower() for s in slugs}

    bad: list[tuple[Path, str]] = []
    seen: set[str] = set()

    for page in sorted(DOCS.rglob("*.md")):
        for match in LINK_RE.finditer(page.read_text()):
            slug = urllib.parse.unquote(match.group(1)).split("#")[0].rstrip("/")
            seen.add(slug)
            if slug.lower() not in lookup:
                bad.append((page.relative_to(ROOT), slug))

    for path, slug in bad:
        print(f"OPR wiki page does not exist: {slug}  <- {path}", file=sys.stderr)

    if bad:
        print(
            f"\n{len(bad)} broken OPR wiki link(s). The wiki has "
            f"{len(slugs)} pages; the target was probably renamed.",
            file=sys.stderr,
        )
        return 1

    print(f"OPR links: {len(seen)} distinct slugs, all exist "
          f"({len(slugs)} pages upstream)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
