# Finding data

Before you process anything you have to know which season, segment and frame you want to process. 
There are three ways to do this that I use regularly.

## Season and year name

The hierarchy is consistent across all the data that have been collected:

| Level | Description | Example |
|---|---|---|
| **Radar system** | The instrument type | `accum`, `rds`, `snow`, `kuband`, `kaband` |
| **Season** | One field campaign | `2024_Antarctica_Ground2` |
| **Segment** | Continuous collection, record start to stop | `20250108_02` |
| **Frame** | A chunk of a segment | `009` |

Which is why products are addressed as
`CSARP_<product>/<day_seg>/Data_<day_seg>_<frm>.mat`.

Arctic and Antarctic live in **separate databases** organized by hemisphere, which also tells you information about when the data were likely collected (austral summer/boreal summer).

## The geoportal

<https://openpolarradar.org/> — a web map over the Open Polar Server (OPS).
Draw a polygon, get the flight lines and frames inside it. 
This is the right tool for "what has been flown over *here*".

Useful behaviours:

- Leaving **Select Season(s)** blank selects **all** seasons.
- **Double-click ends** a polygon. Hold **shift and drag** for freehand.
- The same polygon works in the MATLAB command-line search functions, so you can
  draw it once and reuse it in a script.
- There is an echogram image browser built in for a quick look before you commit
  to downloading anything.

!!! warning "Two filters that do not talk to each other"
    The **Basic Selection Filters** radar-system choice and the **Map Layer
    Selection** radar-system choice are not synchronized. Set both, or you will
    get a map of one system filtered by another and conclude there is no data.

Other known rough edges: MAT and NetCDF download are not currently supported;
"Echogram full resolution" is not generated for most products; and Previous/Next
frame do not move the map view.

## The MATLAB search functions

The toolbox has an interface to the OPS WMS, WFS and RESTful API, which is what
you want when the selection has to be reproducible or feed straight into
processing.

`workshop_ops_search.m` has three worked polygon searches:

1. Generate a crossover report for a season.
2. List layer points (seasons, segments, frames) inside a polygon.
3. List frames in a polygon, get their segments, **construct the file paths to
   the data products**, and get crossovers per frame.

The third is the one that matters — it goes from a geographic question to the
paths a driver script can consume, with no clicking. Combine it with the
`opr_filename_*` helpers in
[storage and file paths](../working-remotely/storage-and-paths.md).

See
[OPS functions](https://gitlab.com/openpolarradar/opr/-/wikis/OPR-Toolbox-Guide#ops-functions-database-search-and-insert-functions)
in the toolbox guide.

## The data portal

<https://data.cresis.ku.edu/> — plain HTTPS directory listings of the public
data products. No account needed.

Right when you already know exactly what you want and just need the bytes:

```
https://data.cresis.ku.edu/data/accum/2024_Antarctica_Ground2/CSARP_standard_HH/20250108_02/
```

Browsing the tree is also the quickest way to answer "which products exist for
this season?" — the `CSARP_*` directory names tell you which processing stages
have been run and posted.

## Checking a season is usable

Before committing to a batch, check the things that are not recorded anywhere
and are expensive to discover late:

- **Which `CSARP_*` products exist**, and whether the one you need was actually
  produced for the frames you want.
- **Whether qlook products are complex.** If a season was processed with
  `inc_dec` non-zero, the products are detected power and phase is gone — fatal
  for any interferometric or
  [polarimetric](fabric-polarimetry.md) work.
- **Whether the GPS files cover the segment.** Radar-time-to-GPS sync does fail;
  it has failed for every segment but one in at least one season.
- **Whether separate polarization channels exist**, for polarimetric work.

Writing a small inventory script that answers these per frame, and running it
first, is worth the hour. An eleven-hour batch is the wrong place to discover
that a third of the frames were never going to work.

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

It is the fastest route to "load some radar data and look at it" if you are not
already living in MATLAB, and it works entirely against public data — no server
account required.

!!! note
    The OPR wiki's Python Guide is currently an empty stub, so xOPR's own
    [documentation](https://docs.englacial.org/xopr/) is the place to look.
