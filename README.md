# CReSIS Remote Users Wiki

A practical wiki for doing radar work on the CReSIS / Open Polar Radar (OPR)
servers at the University of Kansas **when you are not at KU**.

It is a curated layer, not a fork. [John Paden's OPR
wiki](https://gitlab.com/openpolarradar/opr/-/wikis/home) stays authoritative
for the toolbox — file formats, the parameter spreadsheet, radar internals, every
processing step. These pages own the part it does not cover: getting connected
and staying connected, surviving dropped links and time zones, running the
cluster from far away, and prototyping locally before scaling remotely.
[`docs/reference/opr-wiki-map.md`](docs/reference/opr-wiki-map.md) is an
annotated index into the upstream wiki so you know which of its 353 pages to
open.

## Contents

```
docs/
  index.md                                    what this is, who it's for
  background/
    history.md                                CReSIS, IceBridge, and why the
                                              radars split by frequency
  getting-started/
    accounts.md                               first-day checklist, shared-node etiquette
    thinlinc.md                               graphical desktop, Mac key mapping
    ssh-and-tmux.md                           ~/.ssh/config, keys, tmux
    vscode-remote-ssh.md                      remote dev + MATLAB extension
    file-transfer.md                          rsync, scp, FileZilla
  working-remotely/
    matlab.md                                 which MATLAB, headless plots, toolboxes
    cluster.md                                Slurm, chains, surviving overnight failures
    storage-and-paths.md                      gRadar, opr_filename_*, caches
    claude-code.md                            AI tooling in your home directory
  doing-science/
    finding-data.md                           geoportal, OPS search, data portal
    prototyping-loop.md                       local → server, same layout
    fabric-polarimetry.md                     quad-pol fabric chain and its scripts
    swath-cross-track-picking.md              3D images and the slice browser
  reference/
    data-files.md                             path anatomy, radar directories,
                                              what is inside an echogram
    troubleshooting.md                        every failure mode in one table
    opr-wiki-map.md                           annotated index into the OPR wiki
  scripts/fetch_frame.sh                      pull a public quad-pol frame
```

Every page is plain markdown and renders fine on GitHub with no build step.

## Build the site

Source is markdown; [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
adds full-text search and navigation.

```bash
make venv     # create .venv and install dependencies
make serve    # live preview at http://127.0.0.1:8000/cresis_tutorials/
make build    # build into site/
make help     # list every target
```

To publish to GitHub Pages:

```bash
.venv/bin/mkdocs gh-deploy
```

`site_url` in `mkdocs.yml` sets the base path (`/cresis_tutorials/`, matching
the repo name so GitHub Pages resolves); the dev server mounts under the same
prefix, so bare `localhost:8000` redirects there.

Note that GitHub Pages does not serve **private** repos on the free plan. While
this repo is private, use `make serve` locally; `gh-deploy` becomes useful once
it is made public.

## Testing

```bash
make check    # fast, offline, deterministic — run before every commit
make links    # outbound links; hits the network, ~1 min
make check-all
```

`make check` runs four things:

| Check | Catches |
|---|---|
| `mkdocs build --strict` | Broken **internal** links, bad config |
| `tools/check_orphans.py` | Pages missing from `nav:`, and `nav:` entries pointing at deleted files |
| `tools/check_anchors.py` | Links to a `#heading-anchor` that no longer exists |
| `bash -n` + `shellcheck` | Broken shell in `docs/scripts/` |

The middle two exist because `--strict` is narrower than it looks, verified
against mkdocs 1.6.1 / material 9.7:

- **It does not catch orphaned pages.** An orphan still builds and is still
  reachable by URL — it just never appears in the navigation, so nobody finds
  it.
- **It does not check anchors.** It validates that a linked *file* exists, not
  the `#fragment` after it, so renaming a heading silently breaks every link
  into it. The page still loads; it just lands at the top. `check_anchors.py`
  runs against the built `site/` so it sees the ids mkdocs actually generated
  rather than guessing at slugification.

> **Do not add `--quiet` to the strict build.** It drops the log level to
> ERROR, and `--strict` aborts on *warnings*, so `--quiet` silently disables
> broken-link detection while still appearing to pass. This bit us once
> already.

`make links` is separate because it depends on other people's servers:

- **OPR wiki links** are validated against the wiki's page list via one API
  call, not by fetching each URL. gitlab.com returns 429 after a few dozen
  requests, so an HTTP checker reports failures that are really rate limiting.
  This distinguishes "the page was renamed" from "I am being throttled".
- **Everything else** is fetched, but tolerantly: 404/410 fails the build, while
  403/429/timeouts are reported as *unverifiable* rather than failures. A link
  checker that goes red whenever a vendor blocks bots is one people turn off.
  MathWorks currently blocks us; that is expected and not a failure.

CI ([`.github/workflows/check.yml`](.github/workflows/check.yml)) runs `make
check` on every push and PR, and `make links` weekly — link rot should not block
someone's pull request.

### Verifying the checks still work

The checks were confirmed to fail on each defect they claim to catch: an orphan
page, a `nav:` entry pointing at a deleted file, a broken internal link, a
renamed heading behind an anchor link, and a shell syntax error. If you change the harness, re-confirm it — a check that
cannot fail is worse than no check, because it buys false confidence.

## Contributing

Corrections welcome, especially failure modes missing from
[troubleshooting](docs/reference/troubleshooting.md).

Anything that turns out to be generally useful rather than remote-specific
belongs **upstream** in the OPR wiki rather than here — send it to
`opr@openpolarradar.org`. Keeping that line clear is what stops this becoming a
2 MB fork that drifts out of date.

When adding a page, add it to the `nav:` block in `mkdocs.yml` — `make check`
will fail on an orphan, but only after you have already written it.

## Getting help

- **OPR support** — `opr@openpolarradar.org`
- **Accounts** — `paden@ku.edu`
