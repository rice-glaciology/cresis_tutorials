# Map into the OPR wiki

[John Paden's OPR wiki](https://gitlab.com/openpolarradar/opr/-/wikis/home) is
353 pages and roughly 2 MB of text. It is the authoritative reference for the
toolbox, and it is large enough that knowing which page to open is most of the
skill.

This is an annotated index for the pages a remote user actually reaches for.

## Start here

| Page | Why |
|---|---|
| [Home](https://gitlab.com/openpolarradar/opr/-/wikis/home) | Links to every service and repository, plus the citation and acknowledgment text you owe them |
| [OPR Toolbox Setup](https://gitlab.com/openpolarradar/opr/-/wikis/OPR-Toolbox-Setup) | Git, MATLAB toolboxes, `.bashrc`, `.gitconfig`. Do this once, properly. |
| [OPR Toolbox Guide](https://gitlab.com/openpolarradar/opr/-/wikis/OPR-Toolbox-Guide) | The 131 KB monolith. Everything, in one page — use your browser's find. |

!!! tip "Cite it"
    > Open Polar Radar. (2023). opr (Version 3.0.1) \[Computer software\].
    > <https://doi.org/10.5281/zenodo.5683959>

    The acknowledgment text listing the NASA and NSF grant numbers is on the
    [Home](https://gitlab.com/openpolarradar/opr/-/wikis/home#acknowledgment)
    page. Use it.

## Processing

| Page | Covers |
|---|---|
| [Processing Steps](https://gitlab.com/openpolarradar/opr/-/wikis/Processing-Steps) | The full chain, step by step |
| [Parameter Spreadsheet Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Parameter-Spreadsheet-Guide) | The worksheets and what each column does |
| [Cluster Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Cluster-Guide) | Every `cluster_*` function, settings, Slurm and Torque |
| [Analysis](https://gitlab.com/openpolarradar/opr/-/wikis/Analysis) | Coherent noise, specular, deconvolution, equalization |
| [Deconvolution](https://gitlab.com/openpolarradar/opr/-/wikis/Deconvolution) | 44 KB on deconvolution alone |
| [Coherent Noise](https://gitlab.com/openpolarradar/opr/-/wikis/Coherent-Noise) | Removal methods and their parameters |

## File formats

Reach for these when a `.mat` file has a field you do not recognise.

| Page | File |
|---|---|
| [Echogram File Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Echogram-File-Guide) | `Data_*.mat` products |
| [Layer File Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Layer-File-Guide) | Layer data |
| [Record File Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Record-File-Guide) | `records_*.mat` |
| [Frame File Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Frame-File-guide) | `frames_*.mat` |
| [GPS File Guide](https://gitlab.com/openpolarradar/opr/-/wikis/GPS-File-Guide) | `gps_*.mat` |
| [Raw File Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Raw-File-Guide) | Raw radar data, 69 KB |
| [File Conventions](https://gitlab.com/openpolarradar/opr/-/wikis/File-Conventions) | How to *write* files: naming, `ct_save`, storing `param` |

## Picking and tracking

| Page | Covers |
|---|---|
| [Data Tracking Tutorial](https://gitlab.com/openpolarradar/opr/-/wikis/Data-Tracking-Tutorial) | `imb.picker` in depth, and the [slice browser](https://gitlab.com/openpolarradar/opr/-/wikis/Data-Tracking-Tutorial#slice-browser) |
| [Layer tracker](https://gitlab.com/openpolarradar/opr/-/wikis/Layer-tracker) | Automated 2D tracking |
| [Machine Learning Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Machine-Learning-Guide) | ML layer tracking |

## 3D and multi-element

See [cross-track picking](../doing-science/swath-cross-track-picking.md) for the
run order; these are the references.

| Page | Covers |
|---|---|
| [Generating 3D Images](https://gitlab.com/openpolarradar/opr/-/wikis/Generating-3D-Images) | Array processing into 3D volumes |
| [3D Surface Tracking](https://gitlab.com/openpolarradar/opr/-/wikis/3D-Surface-Tracking) | `tomo.run_collate.m`, fusing, surfdata |
| [3D DEM Generation](https://gitlab.com/openpolarradar/opr/-/wikis/3D-DEM-Generation) | surfdata to DEM |
| [Multipass](https://gitlab.com/openpolarradar/opr/-/wikis/Multipass) | Coherent and incoherent repeat-pass |
| [Array proc](https://gitlab.com/openpolarradar/opr/-/wikis/Array-proc) | Array processing internals |

## Radar systems

| Page | Covers |
|---|---|
| [Radar Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Radar-Guide) | Index of systems |
| [Radar Depth Sounder](https://gitlab.com/openpolarradar/opr/-/wikis/Radar-Depth-Sounder) | 88 KB, the largest system page |
| [Radar Guide: accum](https://gitlab.com/openpolarradar/opr/-/wikis/Radar-Guide-accum) / [rds](https://gitlab.com/openpolarradar/opr/-/wikis/Radar-Guide-rds) / [snow](https://gitlab.com/openpolarradar/opr/-/wikis/Radar-Guide-snow) / [kuband](https://gitlab.com/openpolarradar/opr/-/wikis/Radar-Guide-kuband) | Per-system detail |
| [System Time Delay](https://gitlab.com/openpolarradar/opr/-/wikis/System-Time-Delay) | Calibration you will eventually need |
| [Receiver equalization](https://gitlab.com/openpolarradar/opr/-/wikis/Receiver-equalization) | Channel calibration |

## Per-season quirks

| Page | Covers |
|---|---|
| [Dataset Notes](https://gitlab.com/openpolarradar/opr/-/wikis/Dataset-Notes) | Known issues per dataset |
| [Processing Notes](https://gitlab.com/openpolarradar/opr/-/wikis/Processing-Notes) | Per-season notes, with sub-pages |

Read these before starting a season you have not touched. They are where "this
segment's GPS sync failed" is written down.

## Workshops

The workshop pages are the closest thing to a guided course, and the recordings
are genuinely useful.

| Page | Covers |
|---|---|
| [2026 workshop](https://gitlab.com/openpolarradar/opr/-/wikis/workshop/2026) | Agenda, Zoom recordings for days 1 and 2 |
| [2025 workshop](https://gitlab.com/openpolarradar/opr/-/wikis/workshop/2025) | Same, plus the [connection setup instructions](https://gitlab.com/openpolarradar/opr/-/wikis/workshop/2025#support-documentation-and-information) these pages build on |
| [Account setup video](https://www.youtube.com/watch?v=455BxOmdmO0) | ThinLinc and SSH, walked through |

Per-topic workshop pages exist for OPS search, the image browser, echo and
layer functions, swath, multipass, polarimetric processing and ML tracking.

## Development

| Page | Covers |
|---|---|
| [Git](https://gitlab.com/openpolarradar/opr/-/wikis/Git) | Their git workflow |
| [MATLAB Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Matlab-Guide) | The three toolbox MATLAB tutorials |
| [Function Conventions](https://gitlab.com/openpolarradar/opr/-/wikis/Function-Conventions) | House style for contributions |
| [Debug outputs conventions](https://gitlab.com/openpolarradar/opr/-/wikis/Debug-outputs-conventions) | Debug plot conventions |

## Gaps worth knowing about

Honest notes, so you do not waste time looking:

- **Python Guide** is an empty stub. Use
  [xOPR's documentation](https://docs.englacial.org/xopr/) instead.
- **Remote access** is documented only inside dated workshop pages, which is
  part of why this wiki exists.
- Several **Old-** prefixed pages (Old Cluster Guide, Old FMCW Processing Guide,
  the picker archive) are superseded. Check for a current equivalent first.

## Contributing upstream

If you write something that is generally useful rather than remote-specific, it
belongs in the OPR wiki, not here. Request access through GitLab or email
`opr@openpolarradar.org`.
