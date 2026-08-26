# Working on the CReSIS servers, remotely

This github page is intended as a practical guide for working with radar data on the CReSIS / Open Polar Radar (OPR) servers at the University of Kansas from Rice.
The cresis servers host OPR data, the OPR toolbox,  MATLAB licenses, and cluster resources to support processing and data analysis that our group uses to understand ice sheets. It's an important tool that folks in our group need to learn how to use responsibly and effectively.


## Who this is for

**You have an OPR/CReSIS account and you work at Rice.** 
If you do not yet have an account, this guide will not be much help to you. email me and we can setup a meeting with folks at CReSIS to get you started.

## How this relates to the OPR wiki
[John Paden's OPR wiki](https://gitlab.com/openpolarradar/opr/-/wikis/home) is a very helpful reference for using the OPR toolbox. 
It describes file formats, the parameter spreadsheet, processing steps, and can be changed as we develop processing capabilities with collaborators at cresis. 

The focus of this tutorial is to get you to the point where you can use these tools effectively. When you need reference depth, go there. 
The [annotated map](reference/opr-wiki-map.md) tells you which page to open for what, which can save a lot of time hunting.

## Start here

New to the group? Read **[where these data come from](background/history.md)** first. 
It gives a breif overview on CReSIS and Operation IceBridge, it explains a little bit about radar observations and how we can use these data to understand ice sheets.

Then:

1. **[Accounts](getting-started/accounts.md)**
2. **[SSH and tmux](getting-started/ssh-and-tmux.md)**
3. **[ThinLinc](getting-started/thinlinc.md)**
4. **[What the data look like](reference/data-files.md)**

After that, [VS Code Remote-SSH](getting-started/vscode-remote-ssh.md) and
[Claude Code](working-remotely/claude-code.md) are the day-to-day setup.

I've also included two working examples developed with Victoria Villagomez at Rice University.

- **[Fabric from quad-pol accumulation radar](doing-science/fabric-polarimetry.md)**
  — the polarimetric traveltime chain, stage by stage, and the scripts that run
  it.
- **[Cross-track picking for multi-element swath data](doing-science/swath-cross-track-picking.md)**
  — 3D image generation, collation, and picking surfaces in the slice browser.


## Contributing

Corrections and additions are welcome — especially if you identify new solutions to problems or challenges identified here, or a failure modes not in [troubleshooting](reference/troubleshooting.md). 
Anything that turns out to be generally useful rather than remote-specific belongs upstream in the OPR wiki; you can email me about this at ah301@rice.edu.

## Getting help

- **OPR support** — `opr@openpolarradar.org`
- **Accounts** — `paden@ku.edu`
- Inside the group. Someone has almost certainly run into what you're struggling with.
