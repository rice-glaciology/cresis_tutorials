#!/usr/bin/env python3
"""Check non-OPR external links resolve.

Deliberately tolerant. A docs link checker that fails the build every time a
vendor rate-limits a bot is a check people switch off, so:

  200/2xx, 3xx  -> OK
  403, 429, 405 -> UNVERIFIABLE (bot blocking / throttling), reported not failed
  404, 410      -> FAIL, the page is genuinely gone
  timeout/DNS   -> UNVERIFIABLE after one retry

OPR wiki links are skipped: check_opr_links.py validates those against the API,
which is far more reliable than HTTP for that host.

Usage:
    check_external_links.py [--fail-on-unverifiable] [--timeout SECONDS]
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

URL_RE = re.compile(r"(?:\]\(|<)(https?://[^)>\s\"']+)")
SKIP_HOSTS = ("gitlab.com/openpolarradar/opr/-/wikis",)

UA = "Mozilla/5.0 (compatible; cresis-wiki-linkcheck/1.0)"
HARD_FAIL = {404, 410}
SOFT_FAIL = {401, 403, 405, 429}


def collect() -> dict[str, list[str]]:
    urls: dict[str, list[str]] = {}
    for page in sorted(DOCS.rglob("*.md")):
        rel = str(page.relative_to(ROOT))
        for match in URL_RE.finditer(page.read_text()):
            url = match.group(1).rstrip(".,;")
            if any(s in url for s in SKIP_HOSTS):
                continue
            urls.setdefault(url, []).append(rel)
    return urls


def probe(url: str, timeout: float) -> tuple[str, int | None, str]:
    """Return (verdict, status, detail). verdict in {ok, fail, unverifiable}."""
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return "ok", resp.status, ""
    except urllib.error.HTTPError as exc:
        if exc.code in HARD_FAIL:
            return "fail", exc.code, "page not found"
        if exc.code in SOFT_FAIL:
            return "unverifiable", exc.code, "blocked or throttled"
        return "unverifiable", exc.code, "unexpected status"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return "unverifiable", None, str(exc)[:80]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--fail-on-unverifiable", action="store_true")
    args = ap.parse_args()

    urls = collect()
    print(f"checking {len(urls)} external URLs (OPR wiki handled separately)…\n")

    failures: list[tuple[str, int | None, str, list[str]]] = []
    unverifiable: list[tuple[str, int | None, str]] = []

    for url, pages in sorted(urls.items()):
        verdict, status, detail = probe(url, args.timeout)
        if verdict == "unverifiable":
            # one retry, in case it was transient
            time.sleep(1.0)
            verdict, status, detail = probe(url, args.timeout)

        if verdict == "fail":
            failures.append((url, status, detail, pages))
            print(f"FAIL   {status}  {url}")
        elif verdict == "unverifiable":
            unverifiable.append((url, status, detail))
            print(f"skip   {status or '-'}    {url}  ({detail})")
        time.sleep(0.3)

    print()
    if unverifiable:
        print(f"{len(unverifiable)} unverifiable (bot-blocked, throttled, or "
              f"unreachable) — not treated as failures")
    if failures:
        print(f"\n{len(failures)} dead link(s):", file=sys.stderr)
        for url, status, detail, pages in failures:
            print(f"  {status} {url}\n      in: {', '.join(pages)}", file=sys.stderr)
        return 1

    if args.fail_on_unverifiable and unverifiable:
        return 1

    print(f"{len(urls) - len(unverifiable)} link(s) verified, 0 dead")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
