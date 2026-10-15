# Cross-track picking for multi-element swath data

A multi-element array resolves each range line into a **cross-track image**:
echo power as a function of range and direction of arrival (DOA). Picking
the bed in that image, slice after slice, is what turns a single flight line
into a swath of bed elevations. This page is about doing that picking well
in `imb.slice_browser`.

It assumes the 3D images and a surfdata file already exist. If they do not,
see [Getting the inputs](#getting-the-inputs) at the bottom and
[across-track energy, start to finish](swath-across-track-energy.md).

!!! tip "Practise on finished data first"
    `workshop_swath_slice_browser.m` copies an already-processed frame into
    place, so you can start picking without running anything heavy.

## What you are looking at

### One slice is one range line

The slice window shows a single range line. The horizontal axis is
cross-track (DOA bin; elevation angle in degrees if `doa_method_flag` is
on), the vertical axis is range bin, increasing downward. Moving to the next
slice moves you one range line along track.

The horizontal axis is drawn **reversed**. Before you reason about "left"
and "right" of the aircraft, hover over a feature and watch where the
cursor lands in the surface window.

### What a flat bed looks like

A flat bed is **not** a flat line in this view. The range to a flat reflector
grows away from nadir:

$$
R(\theta) = \frac{H}{\cos\theta} + \frac{T}{\cos\theta_\text{ice}}
$$

where $H$ is the aircraft height above the ice surface, $T$ the ice
thickness, and $\theta_\text{ice}$ the angle after refraction at the
surface. So a flat bed is an **arch**: shallowest at nadir, curving to later
range bins toward both edges of the swath. The ice surface draws the same
kind of arch higher up.

Read topography as **departure from that arch**:

- A bed that curves down faster than the arch toward one edge is dipping
  away on that side.
- A bed that flattens out or rises toward an edge is rising on that side.
- A bed that bends sharply partway across is a valley wall or a ridge.

This matters because TRW-S's cross-track smoothness term is built around
the flat-bed arch. Left alone, the tracker pulls the pick toward it. Steep
real topography is exactly where it needs your ground truth.

### Things that are not the bed

| What you see | Why it is there | What to do |
|---|---|---|
| A bright arch **above** the bed that comes down close to it toward the edges | The ice surface. Off nadir it arrives later and later, and its sidelobes leak into neighbouring columns | Make sure the pick stays below it. The tracker already pushes the bed away from the first `Surface range` bins below the surface |
| Copies of the bed displaced sideways by a fixed angle | Grating lobes of a sparse array; on the full 15-channel P-3 array they sit near ±6.8° | Do not pick a ghost. The true bed is the one that continues smoothly from nadir and from neighbouring slices |
| Bed that fades to speckle at the swath edges | Little energy and few looks at steep angles | Stop the pick where it fades and mark the rest bad quality rather than guessing |
| A pick that jumps between two bright bands from column to column | Two candidate reflectors, or a bright internal layer near the bed | Put ground truth on the right one in a few columns and re-run |
| A pick that hugs the bottom of the image or the ice surface | Nothing in that column was brighter than the bounds | Ground truth, or mark it bad |

Check against the **echogram window** too. It shows the near-nadir column
along track, which is the same view you know from 2D picking. If the bed
is unclear there, it will not be easier off-nadir.

## The surfaces

The surface list on the left of the slice window holds a group of related
surfaces. Names depend on how the surfdata was made; typically `top`,
`bottom`, `bottom gt`, `ice mask` and `bottom quality`. Press a number key
to select a surface by its position in the list. Right-click the list to
toggle a surface's visibility.

| Surface | What it is | How you change it |
|---|---|---|
| **Active** (e.g. `bottom`) | The pick itself, one value per DOA bin per slice | Only by running a tool. You cannot click it into place |
| **Ground truth** (e.g. `bottom gt`) | Points you place to steer the tracker | Click to add; `delete` key or Delete tool to remove |
| **Top** (e.g. `top`) | The ice surface. The active surface may not go above it | Normally left alone |
| **Ice mask** | Where the bed may differ from the surface. Where it is false, the tracker sets the bed equal to the top | `delete` toggles selected points |
| **Quality** | False excludes a point from the DEM | `q` / `Q`, or polygons with `p` / `P` |

When `bottom` is selected and you click in the slice, the point goes into
its ground-truth surface. You do not need to select `bottom gt` to add
ground truth.

**You are steering an optimizer, not drawing a line.** Place ground truth,
run TRW-S, inspect, add ground truth where it went wrong, run again.

## The picking loop

### 1. Start

```matlab
param = read_param_xls(opr_filename_param('rds_param_2014_Greenland_P3.xls'), '20140401_03');
frm = 39;
out_type = 'music';          % image directory, CSARP_music
surfdata_source = 'surf';    % surfdata directory, CSARP_surf
sb_param.step_size = 5;      % slices moved by h, j, k, l
imb.run_slice_browser;
```

Three windows open: the **slice**, the **surface** view (the selected
surface's range bin as a map of along-track by cross-track), and the
**echogram**. Moving the mouse in the slice window moves a black cross in
the other two, so you always know where in the frame you are.

Run `clear run_slice_browser_fn` before switching frames, or the script
reuses the data it already loaded.

### 2. Switch out of zoom mode

The browser starts in **zoom mode**: clicks zoom rather than pick. Press `z`
to toggle into pointer mode. If clicks seem to do nothing useful, you are in
the wrong mode. Scroll-wheel zoom works in either mode.

### 3. Find a slice where the bed is clear

Look at the echogram and surface windows, left-click in either one to jump
to that slice, and start somewhere the bed is bright and continuous at
nadir. It is easier to work outward from good data than into it.

### 4. Place ground truth across the swath

Select `bottom`, then left-click on the bed in the slice window. Left-click
and drag paints ground truth along the mouse path.

You do not need a point in every column. Put them where they do the most
work:

- One or two **near nadir**, where the bed is brightest.
- A few **toward each edge**, out as far as you trust the bed. This is
  where the flat-bed prior and the low signal pull the tracker off.
- At every **bend** where the bed departs from the flat-bed arch.
- On the **correct band** wherever two reflectors compete.

The tracker is held within `GT Range` bins (default 5) of each ground-truth
point, so a point a bin or two off is fine.

### 5. Select the columns to track

Right-click and drag a box in the slice window to select the DOA bins TRW-S
should work on. Selected points are circled. Hold shift to add to the
selection. A right-click without dragging toggles one column.

This step is easy to forget. TRW-S operates **only on selected columns**
(the `Select` box in its options is checked by default). With nothing
selected, pressing `w` does nothing. Placing ground truth also selects
that column, so a fresh set of clicks is often already a usable selection.

Leave out the columns at the edges of the swath where the bed has faded.

### 6. Run TRW-S

Press `w`, or pick TRW-S in the tool menu and click **Apply**. It runs on the
selected columns over a block of slices around the current one (`-5:6` by
default) and rewrites the active surface there. The console prints the time
per slice.

With the `L` and `R` edge boxes checked (the default), the first and last
slices of the block are held at their current active values. Successive
runs therefore stitch onto what is already there instead of fighting it.
`T` and `B` do the same for the outermost selected columns.

### 7. Inspect

- Step through the block with `,` and `.`. Look at the pick against the
  image in every slice, not just the one you started on.
- Look at the **surface window**. It is the fastest way to see a bad pick.
  A smooth bed shows smooth colour. Stripes along track, speckle, or
  single-slice spikes mean the tracker jumped.
- Toggle the overlays off with `space` to see the image underneath.

### 8. Correct and repeat

Where the pick is wrong, add ground truth on the bed in that slice, select
the columns, and press `w` again. Press `u` to undo a run you do not like
and `r` to redo.

To remove ground truth, select the points (right-click drag) and press
`delete`.

### 9. Move along track

Step forward a block and repeat. The copy-forward keys make this fast for a
bed that changes slowly:

| Key | Does |
|---|---|
| `m` / `n` | Move forward / back one slice and **copy the selected ground truth** to it |
| `j` / `h` | Move forward / back `step_size` slices and copy the selected ground truth |

Only selected ground-truth points inside the current zoom are copied. They
land at the same range bins, so after each jump look at the slice, drag the
points that are now off the bed, and run `w`.

For a long stretch that already has decent ground truth, go to the surface
window, **right-click and drag a box** over the slices and DOA bins you want,
and choose `trws` from the list that appears. TRW-S then runs over the
whole box at once.

### 10. Mark what you could not pick

Some of the swath will not have a bed you can trust: faded edges, clutter,
crevassed surface. Do not leave the tracker's guess in the DEM.

- `q` sets the selected columns in the current slice to **bad** quality;
  `Q` (shift-q) sets them to good.
- In the surface window, `p` lets you draw a polygon (left-click to add
  vertices, right-click to finish) and sets everything inside to bad. `P`
  sets it to good.

With the quality surface visible, bad points are blanked in the surface
window, so you can see what will be left in the product.

### 11. Save

Press `s`. The save button reads `(S)ave*` while there are unsaved changes.
Closing the slice window asks whether to save.

Save often. A long run of picking lives only in memory until you do.

## TRW-S options

Click **Options** with TRW-S selected to open its settings. Most picking is
done on the defaults; these are the ones worth knowing.

| Option | Default | Change it when |
|---|---|---|
| `Slice range` | `-5:6` | Larger to cover more along-track per press of `w` where the bed is easy; smaller where it is hard and you want tight control |
| `GT Range` | 5 | Smaller to pin the pick harder to your points; larger if your points are only approximate |
| `CT Smooth` | 0.07 | Lower where the bed is rough across track and the pick is being flattened; higher where the pick is noisy column to column |
| `AT Smooth` | 0.07 | Same trade-off along track |
| `Surface range` / `Surface weight` | 110 / 30 | How far below the ice surface, in bins, and how strongly the bed is pushed away from it. Lower the range for thin ice, where the bed really is close to the surface |
| `Tomo Layers` | `tomo_top`, `tomo_bottom` | Layers that bound the search in range. If they do not exist for the segment, the search covers the whole column |
| `Max Loops` | 10 | Rarely |
| `Select` | on | Turn off to track every column regardless of selection |
| `L` `R` `T` `B` | on | Turn off an edge to let TRW-S rewrite it, for example when the existing pick at that edge is itself wrong |

The cross-track weight is applied relative to the flat-bed arch and is
automatically looser toward the edges, where the arch is steep. Defaults
can also be set before launch through `trws_param` (`ct_weight`,
`at_weight`, `gt_range`, `max_loops`, `layer_bounds`).

## Keyboard and mouse reference

Press `F1` in any window to print the full list to the console.

### Keys

| Key | Action |
|---|---|
| `z` | Toggle zoom mode / pointer mode |
| `ctrl-z` | Zoom out to the full image |
| `,` / `.` | Back / forward one slice |
| `k` / `l` | Back / forward `step_size` slices |
| `n` / `m` | Back / forward one slice, copying selected ground truth |
| `h` / `j` | Back / forward `step_size` slices, copying selected ground truth |
| `g` | Go to a slice number |
| `1`–`9` | Select a surface by its position in the list |
| `w` | Run TRW-S |
| `q` / `Q` | Selected columns to bad / good quality |
| `p` / `P` | Polygon in the surface window to bad / good quality |
| `delete` | Delete selected ground truth (toggles on mask and quality) |
| `space` | Show / hide the surface overlays |
| `u` / `r` | Undo / redo |
| `s` | Save |
| Arrow keys | Pan |

### Mouse

| Window | Zoom mode | Pointer mode |
|---|---|---|
| **Slice** | Left drag: zoom box. Left click: zoom in. Right click: zoom out | Left click / drag: place ground truth. Right drag: select columns. Right click: toggle one column |
| **Surface** | As above | Left click: go to that slice. Right drag: select slices and DOA bins, then choose a tool to apply |
| **Echogram** | As above | Click: go to that slice |

In every window the scroll wheel zooms, and holding shift while zooming
restricts it to one axis.

## Doing this remotely

The slice browser is three linked, constantly redrawing windows. Use
[ThinLinc](../getting-started/thinlinc.md), not X11 forwarding, which is
too slow for copy-forward picking to be practical.

- **Disconnect rather than log out** (F8 → Disconnect) so the session, the
  loaded frame and any unsaved picks are still there tomorrow. Save anyway.
- On a Mac, right Command is Super and left Command is Alt.

## Getting the inputs

The slice browser needs two files for the frame:

- the 3D image, `CSARP_music/YYYYMMDD_SS/Data_YYYYMMDD_SS_FFF.mat`
- the surfdata, `CSARP_surf/YYYYMMDD_SS/Data_YYYYMMDD_SS_FFF.mat`

If the surfdata does not exist, `run_slice_browser` creates an empty one
from the image. After picking, `run_surfdata_to_DEM.m` turns the corrected
surfdata into a DEM.

??? note "Producing them: array processing and collation"
    | Stage | Script | Produces |
    |---|---|---|
    | [Generating 3D images](https://gitlab.com/openpolarradar/opr/-/wikis/Generating-3D-Images) | `run_array.m` with MUSIC (`CSARP_music`) | `Data_img_II_YYYYMMDD_SS_FFF.mat` per waveform |
    | [3D surface tracking](https://gitlab.com/openpolarradar/opr/-/wikis/3D-Surface-Tracking) | `tomo.run_collate.m` | fused image and an automatically tracked surfdata |
    | Picking (this page) | `imb.run_slice_browser.m` | corrected surfdata |
    | [3D DEM generation](https://gitlab.com/openpolarradar/opr/-/wikis/3D-DEM-Generation) | `run_surfdata_to_DEM.m` | DEM |

    Run array processing and collation through
    [Slurm](../working-remotely/cluster.md), not on a login node. For a
    segment nobody has processed, coherent-noise removal and receiver
    equalization come before any of this and decide whether the angles mean
    anything: see [across-track energy](swath-across-track-energy.md).

    `tomo.run_collate.m` has three steps, each behind a flag:

    - **`fuse_images`** combines waveform images into one.
      `tomo_collate.imgs` lists the images; for a horizontal fuse the order
      is right-looking, nadir, left-looking (e.g. `[2 1 3]`).
      `master_img_idx` sets the image whose axes everything is interpolated
      onto. `vertical_fuse = true` combines waveforms covering different
      depths, with `img_comb` giving the blend times
      (e.g. `[1e-6 2e-6 5e-6 10e-6]` for three waveforms).
    - **`add_icemask_surfacedem`** attaches the ice mask and surface DEM.
    - **`create_surfdata`** runs the automatic tracker and writes the
      surfdata you then correct here.

    The workshop scripts (`workshop_swath_run_array.m`,
    `workshop_swath_tomo_collate.m`, `workshop_swath_DEM.m`) copy their
    inputs from completed runs so each stage can be practised alone.

## Reference

- [Slice browser user guide](https://gitlab.com/openpolarradar/opr/-/wikis/Data-Tracking-Tutorial#slice-browser)
- [3D Surface Tracking](https://gitlab.com/openpolarradar/opr/-/wikis/3D-Surface-Tracking)
- [Generating 3D Images](https://gitlab.com/openpolarradar/opr/-/wikis/Generating-3D-Images)
- [3D DEM Generation](https://gitlab.com/openpolarradar/opr/-/wikis/3D-DEM-Generation)
- Source: `imb.slice_browser`, `imb.slicetool_trws`, `imb.slicetool_quality` in the OPR toolbox
