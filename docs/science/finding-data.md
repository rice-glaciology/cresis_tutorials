# Finding data

Before you process any data you have to know which season, segment and frame you want to process. 

## Season and year name

The hierarchy is consistent across all the data that have been collected:

| Level | Description | Example |
|---|---|---|
| **Radar system** | The instrument type | `accum`, `rds`, `snow`, `kuband`, `kaband` |
| **Season** | One field campaign | `2024_Antarctica_Ground2` |
| **Segment** | Continuous collection, record start to stop | `20250108_02` |
| **Frame** | A chunk of a segment | `009` |

These map to project directories following the convention:
`CSARP_<product>/<day_seg>/Data_<day_seg>_<frm>.mat`.

Arctic and Antarctic live in **databases** organized by hemisphere. All data has been collected in either the austral summer or boreal summer.

## The OPR portal

<https://openpolarradar.org/> is a web map over the Open Polar Server (OPS). You can draw a polygon, get the flight lines and frames inside it. 
This is the right tool for understanding "what has been flown over *here*".

The .mat and .nc downloads are not supported for the OPR portal and the "Echogram full resolution" is not generated for most products so it's best to interact with the data you find using the portal on the cresis servers.

## The MATLAB search functions

The toolbox has an interface to the OPS WMS, WFS and RESTful API.

`workshop_ops_search.m` has three worked polygon searches:

1. Generate a crossover report for a season.
2. List layer points (seasons, segments, frames) inside a polygon.
3. List frames in a polygon, get their segments, **construct the file paths to
   the data products**, and get crossovers per frame.

Combining the third capability with
`opr_filename_*` helpers in [storage and file paths](../working-remotely/storage-and-paths.md) we can identify locations for crossover analysis.

See
[OPS functions](https://gitlab.com/openpolarradar/opr/-/wikis/OPR-Toolbox-Guide#ops-functions-database-search-and-insert-functions)
in the toolbox guide.

## The data portal

<https://data.cresis.ku.edu/> — plain HTTPS directory listings of the public data products. No account needed.

Right when you already know exactly what you want and just need the bytes:

```
https://data.cresis.ku.edu/data/accum/2024_Antarctica_Ground2/CSARP_standard_HH/20250108_02/
```

Browsing the directory is the quickest way way learn which products exist for a given season. The `CSARP_*` directory names tell you which processing stages have been run and posted.

## Checking a season is usable

- First check **which `CSARP_*` products exist**, and whether the one you need was actually
  produced for the frames you want.
- Next check **whether qlook products are complex.** If a season was processed with
  `inc_dec` non-zero, the products are detected power and phase information is not recorded.
- Next check **whether the GPS files cover the segment.** Radar-time-to-GPS sync does fail occasionally.
- Then check **whether separate polarization channels exist**, for polarimetric work.

## Season notes

[Dataset Notes](https://gitlab.com/openpolarradar/opr/-/wikis/Dataset-Notes) and
the per-season
[Processing Notes](https://gitlab.com/openpolarradar/opr/-/wikis/Processing-Notes)
on the OPR wiki record known quirks per campaign. Worth reading before a new
season, and the natural place to contribute what your inventory script found.

## Python

[xOPR](https://docs.englacial.org/xopr/) finds and loads OPR data products in
Python, with `xarray` output:

```bash
pip install git+https://github.com/thomasteisberg/xopr
```

xOPR is an ongoing project. It's not yet complete. The fastest route to "load some radar data and look at it" if you are not already living in MATLAB, and it works entirely against public data.

!!! note
    The OPR wiki's Python Guide is currently an empty stub, so xOPR's own [documentation](https://docs.englacial.org/xopr/) is the place to look.
