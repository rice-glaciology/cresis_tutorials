# Working on the CReSIS servers, remotely

A practical guide to doing real radar work on the CReSIS / Open Polar Radar
(OPR) servers at the University of Kansas **when you are not at KU**.

The data are there, the OPR toolbox is there, MATLAB is licensed there, and the
cluster is there. If you are down the hall, that is easy. If you are in Houston,
Bremerhaven, or Cambridge, a set of small frictions — a dropped VPN killing an
eight-hour job, a plot window that takes ten seconds to redraw, a job that fails
at 3 a.m. your time — add up to the difference between using these machines and
avoiding them.

This wiki is about removing those frictions.

## Who this is for

**You have an OPR/CReSIS account and you work remotely.** That is the reader
these pages are written for — including undergraduates joining the group who
have never touched an HPC system before.

If you have no account at all, much of the data is public and you can get a
long way with the [geoportal and the public data
products](doing-science/finding-data.md) — but the rest of this guide assumes
you can log in.

## How this relates to the OPR wiki

[John Paden's OPR wiki](https://gitlab.com/openpolarradar/opr/-/wikis/home) is
the authoritative reference for the toolbox: 353 pages covering file formats,
the parameter spreadsheet, radar internals, and every processing step. It is
excellent and it is not being replaced here.

What it does not have is a coherent story for working *at a distance*. The
setup material is real but scattered across dated workshop pages, and almost
everything else reasonably assumes you are sitting on the internal network with
the filesystem mounted.

So the split is:

| These pages own | The OPR wiki owns |
|---|---|
| Getting connected and staying connected | Raw and processed file formats |
| Surviving dropped links and time zones | The parameter spreadsheet |
| Where things live on disk, and what not to delete | Radar system internals |
| Running and monitoring the cluster from far away | Every processing step in detail |
| AI tooling in your home directory | Season-by-season processing notes |
| Prototyping locally, scaling remotely | Calibration and system time delay |

When you need reference depth, go there. The
[annotated map](reference/opr-wiki-map.md) tells you which page to open for
what, which saves a lot of hunting.

## Start here

New to the group? Read
**[where these data come from](background/history.md)** first. It is fifteen
minutes on CReSIS and Operation IceBridge, and it explains why the files are
shaped the way they are — which makes everything after it easier.

Then:

1. **[Accounts and first day](getting-started/accounts.md)** — a checklist to
   get working.
2. **[SSH and tmux](getting-started/ssh-and-tmux.md)** — the workhorse, and the
   one habit that stops you losing jobs.
3. **[ThinLinc](getting-started/thinlinc.md)** — the graphical desktop, for
   `imb.picker` and anything else with a GUI.
4. **[What the data look like](reference/data-files.md)** — how to read a path,
   and what is inside an echogram file.

After that, [VS Code Remote-SSH](getting-started/vscode-remote-ssh.md) and
[Claude Code](working-remotely/claude-code.md) are the day-to-day setup.

Then two worked examples put it together on real projects:

- **[Fabric from quad-pol accumulation radar](doing-science/fabric-polarimetry.md)**
  — the polarimetric traveltime chain, stage by stage, and the scripts that run
  it.
- **[Cross-track picking for multi-element swath data](doing-science/swath-cross-track-picking.md)**
  — 3D image generation, collation, and picking surfaces in the slice browser.

Both assume the loop in
[prototype locally, scale remotely](doing-science/prototyping-loop.md).

## Contributing

Corrections and additions are welcome — especially if you hit something these
pages got wrong, or a failure mode not in
[troubleshooting](reference/troubleshooting.md). Anything that turns out to be
generally useful rather than remote-specific belongs upstream in the OPR wiki;
send it to `opr@openpolarradar.org`.

## Getting help

- **OPR support** — `opr@openpolarradar.org`
- **Accounts** — `paden@ku.edu`
- Inside the group, ask on Slack before you lose an afternoon to something that
  turns out to be a one-line fix. Someone has almost certainly hit it already.
