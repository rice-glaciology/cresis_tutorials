# CReSIS Remote Users Wiki

A practical wiki for doing radar work on the CReSIS / Open Polar Radar (OPR)
servers at the University of Kansas **when you are not at KU**.

This is intended as a curated layer to help folks in the Rice Glaciology group learn how to use our computing resources and work with radar data stored at CReSIS. 
[The OPR wiki](https://gitlab.com/openpolarradar/opr/-/wikis/home) is an authoritative reference for the toolbox — file formats, the parameter spreadsheet, radar internals, every processing step. 
These pages will help you get connected and staying connected, surviving dropped links, running the cluster from machines here at Rice, and prototyping locally.
[`docs/reference/opr-wiki-map.md`](docs/reference/opr-wiki-map.md) is an annotated index into the upstream wiki.

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
