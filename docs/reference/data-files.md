# What the data actually look like

Every path and filename in this system encodes something. Once you can read
them, navigating the archive stops being guesswork. This page walks the
directory tree top to bottom and then opens a file.

## Anatomy of a path

```
/kucresis/scratch/dataproducts/opr_data/accum/2024_Antarctica_Ground2/CSARP_standard/20250108_02/Data_20250108_02_009.mat
└──────────── out_path ────────────────┘ └──┬─┘ └──────────┬────────┘ └──────┬─────┘ └────┬───┘ └──────────┬─────────┘
                                       radar_name       season         product      segment          frame
```

Read right to left, that is: **frame 9**, of **segment 02** collected on **8
January 2025**, from the **standard array-processed** product, of the
**2024 Antarctica Ground2** season, from the **accumulation radar**.

The general form:

```
<out_path>/<radar_name>/<season_name>/<data_product>/<segment>/Data{_img_II}_<segment>_<frame>.mat
```

| Piece | Format | Values |
|---|---|---|
| `radar_name` | | `rds`, `accum`, `snow`, `kuband`, `kaband` — one per frequency family, see [below](#why-there-are-five-radar-directories) |
| `season_name` | `YYYY_LOCATION_PLATFORM` | `2024_Antarctica_Ground2`, `2011_Greenland_P3` |
| `data_product` | `CSARP_*` | see the table below |
| `segment` | `YYYYMMDD_SS` | `20250108_02` — date plus zero-padded segment number |
| `frame` | `FFF` | `009` — zero-padded |
| `_img_II` | optional | present when a product has separate per-waveform images |

`CSARP_` is a historical prefix from "CReSIS SAR Processor". It marks a
processing output directory and nothing more.

## Why there are five radar directories

The top level of the archive splits by **frequency family**, because frequency
is what decides how deep an instrument sees — the reasoning is in
[where these data come from](../background/history.md#the-instruments-and-why-frequency-decides-everything).
On the [public data portal](https://data.cresis.ku.edu/data/) and on the
servers, those are:

| Directory | Band | Frequency | What it sees |
|---|---|---|---|
| `rds` | HF–VHF | ~1–600 MHz | Full ice column, including the bed |
| `accum` | UHF | ~500–2000 MHz | Shallow to deep internal layers |
| `snow` | L- to Ku-band | ~1–18 GHz | Shallow snow layers |
| `kuband` | Ku-band | ~12–18 GHz | Surface altimetry |
| `kaband` | Ka-band | ~ up to 38 GHz | Surface altimetry, snow grain size |

### System name is not directory name

This catches people out. The **`param.radar_name` in a parameter spreadsheet is
a specific hardware generation**, not the directory. `opr_output_dir.m` maps one
to the other, and also reports the transmit architecture:

| `param.radar_name` | → directory | `radar_type` |
|---|---|---|
| `mcords`, `mcords2` … `mcords6`, `mcrds`, `icards`, `acords`, `cords`, `hfrds`, `hfrds2`, `vhfrds`, `wise`, `rds` | `rds` | `pulsed` |
| `accum0` | `accum` | `deramp` |
| `accum` | `accum` | `stepped` |
| `accum2`, `accum3` | `accum` | `pulsed` |
| `snow`, `snow2`, `snow3`, `snow5`, `snow8`, `snow9` | `snow` | `deramp` |
| `kuband`, `kuband2`, `kuband3` | `kuband` | `deramp` |
| `kaband`, `kaband3`, `kaband8` | `kaband` | `deramp` |

So a season processed with `mcords5` writes into `rds/`, and there is no
`mcords5` directory anywhere. Fifteen distinct depth-sounder generations, going
back to ICARDS in the 1990s, all land in the same `rds` tree — which is exactly
what you want when you are searching across three decades of surveys, and
exactly what confuses you the first time you go looking for the folder named
after your radar.

`radar_type` matters because it determines which processing path applies:

- **`pulsed`** — transmits a chirp, records the echo. The depth sounders.
- **`deramp`** — FMCW, mixing the received signal against the outgoing sweep so
  the ADC only has to sample the difference. The snow radars and altimeters.
- **`stepped`** — the bandwidth is split into overlapping sub-bands recorded
  round-robin and stitched afterwards. The original accumulation radar divided
  550–900 MHz into 16 sub-bands (550–600, 570–620, … 850–900) this way.

!!! tip "The hyphen override"
    A `radar_name` may carry a `-` suffix that overrides the output directory:

    ```matlab
    param.radar_name = 'mcords5-accum';
    % → output_dir = 'accum', radar_name = 'mcords5'
    ```

    That is how depth-sounder hardware operated at accumulation-radar
    frequencies gets filed with the accumulation data rather than with the
    depth sounders. If a season is not in the directory you expect, check for
    this.

To resolve any of it in code rather than by eye:

```matlab
[output_dir, radar_type, radar_name] = opr_output_dir(param.radar_name);
```

### Hierarchy

Four levels, and every tool uses the same vocabulary:

- **Season** — one field campaign.
- **Segment** — one continuous data collection, from record start to stop. If
  the radar was switched off and on, that is a new segment.
- **Frame** — a chunk of a segment, of manageable size. Frames are the unit you
  process, load and pick.
- **Record / range line** — a single radar trace. `Nx` of them per frame.

## The product directories

Which `CSARP_*` directories exist tells you which processing stages have been
run for that season:

| Directory | Produced by | Contains |
|---|---|---|
| `CSARP_qlook` | `qlook.m` | Quick look — unfocused SAR. Fast, always there. |
| `CSARP_deconv` | `qlook.m` | Quick look with deconvolution applied |
| `CSARP_sar` | `sar.m` | Focused SAR, single-look complex |
| `CSARP_standard` | `array.m` | SAR + standard (periodogram) array processing |
| `CSARP_mvdr` | `array.m` | SAR + MVDR array processing |
| `CSARP_music` | `array.m` | SAR + MUSIC — the **3D volume** products |
| `CSARP_analysis` | `analysis.m` | Coherent noise, equalization, deconvolution/specular |
| `CSARP_post` | `post.m` | Posted, publication-ready products |
| `CSARP_layer` | picking | Layer picks (see below) |

Custom modules add their own — `CSARP_polarimetric`, `CSARP_fabric_joint` and
so on. If you write a module, it gets a directory here too.

**Start with `CSARP_standard` or `CSARP_qlook`.** Those are ordinary 2D
echograms and are what most analysis uses.

## Inside an echogram file

The `.mat` files are MATLAB v7.3, which is HDF5 underneath — so Python can read
them too (`h5py`, or [xOPR](https://docs.englacial.org/xopr/) which handles the
conventions for you).

With `Nt` fast-time samples and `Nx` records:

| Field | Size | What it is |
|---|---|---|
| `Data` | `Nt × Nx` | **The echogram**, in linear power units |
| `Time` | `Nt × 1` | Fast-time axis — two-way travel time in seconds |
| `GPS_time` | `1 × Nx` | ANSI-C time (seconds since 1 Jan 1970) per record |
| `Latitude` | `1 × Nx` | Degrees |
| `Longitude` | `1 × Nx` | Degrees |
| `Elevation` | `1 × Nx` | Metres above the WGS-84 ellipsoid |
| `Roll`, `Pitch`, `Heading` | `1 × Nx` | Radians |
| `Surface` | `1 × Nx` | Travel time to the ice surface |
| `Bottom` | `1 × Nx` | Travel time to the bed |
| `file_type` | string | `'qlook'` or `'array'` |
| `file_version` | string | `'1'`; an `L` means locked, a `D` means marked for deletion |
| `param_records` | struct | Parameters from `create_records.m`, incl. `gps_source` |
| `param_qlook` / `param_sar` / `param_array` | struct | Parameters of whichever stage produced this file |

Two axes and an image. `Data` is the picture, `Time` is the vertical axis, and
`GPS_time`/`Latitude`/`Longitude` are the horizontal axis.

!!! warning "`Surface` and `Bottom` are not the answer"
    They exist so the processor can combine and process the data. The wiki is
    explicit that they are **generally not the best estimate and do not
    represent the L2 product**. For real surface and bed picks, use the layer
    files. Undergraduates reproduce this mistake constantly: a thickness
    computed from `Bottom - Surface` in an echogram file is not a publishable
    ice thickness.

### The `param_*` structs matter

Every product carries the full parameter structure of the stage that made it,
including `sw_version` with a git hash of the toolbox at the time. That is your
provenance: if two frames disagree, the first thing to compare is their
`param_*` structs. Preserve them when you write derived products —
[File Conventions](https://gitlab.com/openpolarradar/opr/-/wikis/File-Conventions)
covers how.

## Loading one

```matlab
fn = '/kucresis/.../CSARP_standard/20250108_02/Data_20250108_02_009.mat';
mdata = load(fn);

whos('-file', fn)                 % what's in it, without loading

figure;
imagesc([], mdata.Time*1e6, 10*log10(mdata.Data));
xlabel('Range line'); ylabel('Two-way travel time (\mus)');
colormap(1-gray); colorbar;
```

`Data` is linear power, so you almost always want `10*log10()` to see anything.
The toolbox has `echo_*` helpers that handle the axes, geolocation and
layer overlays properly — prefer them for real figures.

In Python:

```python
import h5py
with h5py.File(fn, "r") as f:
    data = f["Data"][:]        # note: HDF5 gives you the transpose of MATLAB
    twtt = f["Time"][:]
```

## Support files

These live under `support_path`, not `out_path`, and are per-segment rather
than per-frame:

```
gps/<season>/gps_YYYYMMDD.mat
records/<radar_name>/<season>/records_YYYYMMDD_SS.mat
frames/<radar_name>/<season>/frames_YYYYMMDD_SS.mat
```

- **`gps`** — the trajectory, one file per day.
- **`records`** — maps raw radar data to time and position. Everything
  downstream depends on it.
- **`frames`** — where the frame boundaries fall. `frame_idxs` gives the record
  index that starts each frame, `gps_time` has `Nfrms+1` entries (the extra one
  is the end of the last frame), and `proc_mode` and `quality` carry per-frame
  flags.

If a segment behaves strangely, check `records` first — a failed radar-time to
GPS sync is a real and recurring failure mode, and it is invisible until you
look.

## Layer files

Picks live in `CSARP_layer/<segment>/Data_<segment>_<frame>.mat`, and take
**two** files to interpret:

- the **layer file** — two-way travel time per layer, per range line
- the **layer organizer file** — metadata for each layer: name, age,
  description

Layer files are sampled much more coarsely along-track than the echogram —
5 m for `accum`, `kuband`, `snow` and `kaband`, 15 m for `rds` — so they do not
index one-to-one against echogram columns. The GPS in a layer file is the
radar's reference point, and the file stores the GPS source, time offset and
lever arm so the geometry can be reconstructed.

For 3D imagery, picks live in **surfdata** files instead — see
[cross-track picking](../doing-science/swath-cross-track-picking.md).

## Building paths in code

Do not concatenate these strings by hand. The toolbox has helpers that take the
parameter structure and produce the right path:

```matlab
param = struct('radar_name','accum', ...
               'season_name','2024_Antarctica_Ground2', ...
               'day_seg','20250108_02');

opr_filename_out(param,'standard','')          % product directory
opr_filename_support(param,'','records')        % records file
```

See [storage and file paths](../working-remotely/storage-and-paths.md) for the
full set and for how `gRadar` decides the roots — which is also what lets the
same script run on your laptop and on the server.

## Reference

The authoritative field-by-field descriptions:

- [Echogram File Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Echogram-File-Guide)
- [Layer File Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Layer-File-Guide)
- [Record File Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Record-File-Guide)
- [Frame File Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Frame-File-guide)
- [GPS File Guide](https://gitlab.com/openpolarradar/opr/-/wikis/GPS-File-Guide)
- [File Conventions](https://gitlab.com/openpolarradar/opr/-/wikis/File-Conventions) — for writing your own

And for the instruments behind the directories:

- [Radar Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Radar-Guide) — the frequency families, with references
- [Depth sounders](https://gitlab.com/openpolarradar/opr/-/wikis/Radar-Guide-rds) — every generation since the 1990s, per season
- [Accumulation radars](https://gitlab.com/openpolarradar/opr/-/wikis/Radar-Guide-accum) · [Snow radars](https://gitlab.com/openpolarradar/opr/-/wikis/Radar-Guide-snow) · [Altimeters](https://gitlab.com/openpolarradar/opr/-/wikis/Radar-Guide-kuband)
