# Cross-track picking for multi-element swath data

With a multi-element array you are no longer picking a single trace beneath the
aircraft or sled. Array processing turns each range line into a **cross-track
image** — energy resolved by direction of arrival — and the layer you want is a
surface across track and along track, not a line.

This page covers producing those 3D images and picking in them: the run order,
the tools, and the parts that behave differently from `imb.picker`.

!!! info "Different picker"
    2D echograms use `imb.picker`. 3D imagery uses **`imb.slice_browser`**, and
    the two are not yet integrated. Only beam-forming / 3D volume products
    (e.g. `CSARP_music`) are supported for surface tracking.

## The chain

```
SAR processing            →  array processing        →  collation        →  picking      →  DEM
sar.m                        array.m                    tomo.run_collate    slice_browser   surfdata_to_DEM
                             CSARP_music                 surfdata files
```

Four stages, each with an example runner in the toolbox:

| Stage | Script | Produces |
|---|---|---|
| [Generating 3D images](https://gitlab.com/openpolarradar/opr/-/wikis/Generating-3D-Images) | `run_array.m` | `Data_img_II_YYYYMMDD_SS_FFF.mat` per waveform |
| [3D surface tracking](https://gitlab.com/openpolarradar/opr/-/wikis/3D-Surface-Tracking) | `tomo.run_collate.m` | fused image + surfdata |
| Manual picking | `imb.run_slice_browser.m` | corrected surfdata |
| [3D DEM generation](https://gitlab.com/openpolarradar/opr/-/wikis/3D-DEM-Generation) | `run_surfdata_to_DEM.m` | DEM product |

!!! tip "You do not have to run the whole chain to practise"
    The workshop scripts (`workshop_swath_run_array.m`,
    `workshop_swath_tomo_collate.m`, `workshop_swath_slice_browser.m`,
    `workshop_swath_DEM.m`) each copy their inputs from an already-completed
    source, precisely because these stages take a long time. You can start at
    the slice browser.

## Stage 1 — Array processing

`run_array.m` drives `array.m` using the
[array worksheet](https://gitlab.com/openpolarradar/opr/-/wikis/OPR-Toolbox-Guide#array-worksheet)
of the parameter spreadsheet. For 3D imaging you want a beam-forming or
subspace method — MUSIC (`CSARP_music`) is the usual choice — rather than the
standard periodogram output.

This is heavy processing. Run it through Slurm, not on a login node; see
[running the cluster remotely](../working-remotely/cluster.md).

## Stage 2 — Collation

`tomo.run_collate.m` is the only script you should need to edit. It configures
three workers, each toggled by a flag:

### `fuse_images`

Different waveforms capture different parts of the topography and are processed
into separate images. This combines them into one coherent image, using raised
cosine weighting to suppress discontinuities at the seams.

Set `tomo_collate.fuse_images_flag = true`, then:

- **`tomo_collate.imgs`** — indices of the waveform images to include. **Order
  matters.** For a horizontal fuse the first index is weighted toward
  right-looking DOA bins, the second toward nadir, the third toward
  left-looking. So if waveform 1 looks nadir, 2 looks right and 3 looks left:

    ```matlab
    tomo_collate.imgs = [2 1 3];
    ```

- **`tomo_collate.master_img_idx`** — which image is the master. Everything else
  is interpolated onto its time and DOA axes.

- **`tomo_collate.vertical_fuse`** — the dimension to combine in. Waveforms that
  look in different **directions** at constant range → `false`. Waveforms that
  cover different **depths** in the same direction → `true`.

- **`tomo_collate.img_comb`** — only used when `vertical_fuse` is true. A vector
  of length `2*(N-1)` giving the start and end time of each blend. For three
  waveforms covering 0–2 µs, 1–10 µs and 5–100 µs:

    ```matlab
    tomo_collate.img_comb = [1e-6 2e-6 5e-6 10e-6];
    ```

Input `Data_img_II_YYYYMMDD_SS_FFF.mat`, output `Data_YYYYMMDD_SS_FFF.mat`.

### `add_icemask_surfacedem`

Attaches the ice mask and a surface DEM. These become inputs to the tracker —
the ice mask tells it where the returned surface is allowed to differ from the
air-ice surface, which is what keeps it from wandering off over bedrock.

### `create_surfdata`

Runs the automated tracking and writes the surfdata file.

## Stage 3 — Picking in the slice browser

Launch through `imb.run_slice_browser.m`. There are several
`run_slice_browser_*.m` examples in the `run_opr` repository.

### The five surfaces

Each primary surface carries a stack of related surfaces, and knowing which one
you are editing is most of the battle:

| Surface | What it is | Can you edit it? |
|---|---|---|
| **Active** | The final two-way traveltime for this surface | No — only the tracker writes it |
| **Ground Truth** | Your supplied points, used to steer the tracker | Yes — add and delete |
| **Mask** | Binary ice mask; true means the surface may differ from air-ice | Indirectly |
| **Quality** | Binary; false excludes the point from generated products | Yes |
| **Surface** | Two-way traveltime to the air-ice surface | Aids the tracker |

The workflow is therefore **not** "draw the layer". It is: place ground truth,
run the tracker, inspect, add ground truth where it went wrong, re-run. You are
steering an optimizer, not drawing.

### The tools

| Tool | What it does |
|---|---|
| **TRW-S** | Tree-reweighted sequential tracker. Uses ground truth, ice surface and ice mask to write the active surface. Right-click and drag over a region, then select TRW-S. |
| **Delete** | Removes ground truth in the dragged region. |
| **Quality** | Right-click and drag sets quality to bad; **hold shift** to set good. Press `p` / `P` for a polygon select instead of a box. |

### Three windows, one cursor

The slice browser shows a **slice** view (the cross-track image at one range
line), a **surface** view (the tracked surface in map-ish view), and an
**echogram** view. Mouse motion in one moves trackers in the others, which is
how you keep your place.

As in `imb.picker`, `z` toggles between **zoom** mode (the default) and **tool**
mode. Almost every "the clicks are doing nothing useful" moment is being in the
wrong mode.

### Keyboard

Navigation, which you will use constantly:

| Key | Action |
|---|---|
| `,` / `.` | Back / forward one slice |
| `k` / `l` | Back / forward `step_size` slices (default 5) |
| `n` / `m` | Back / forward one slice **and copy selected ground truth to it** |
| `h` / `j` | Back / forward `step_size` slices **and copy ground truth** |
| Arrow keys | Pan |
| `u` / `r` | Undo / redo |
| `ctrl-z` | Zoom to full dataset |
| `F1` | Print all shortcuts to the console |

The copy-forward keys (`n`, `m`, `h`, `j`) are the ones that make picking a
long line tractable — a layer that changes slowly across track can be carried
slice to slice and nudged, rather than re-picked.

`step_size` is settable in the constructor or as a property during operation.

### Mouse, by window

**Slice window** — left click sets ground truth where you clicked; left click
and drag paints it along the mouse track; right click toggles selection of a
column; right click and drag selects which elevation bins get operated on.

**Surface window** — left or right click jumps the slice window to that slice;
double click changes the slice view; **right click and drag applies the active
tool** to the region. Modifier keys change behaviour: shift with the quality
tool sets good instead of bad.

**Echogram window** — any click jumps the slice window to that slice.

## Doing this remotely

The slice browser is a genuinely interactive GUI with three linked windows, so
it is the clearest case in this whole wiki for **using ThinLinc rather than X11
forwarding**. Over X11 the redraws are slow enough that copy-forward picking
stops being viable.

- Run the heavy stages (array processing, collation) through
  [Slurm](../working-remotely/cluster.md), detached, and let them finish while
  you are asleep.
- Do the picking in a [ThinLinc session](../getting-started/thinlinc.md), and
  **disconnect rather than log out** (F8 → Disconnect) so the session and its
  loaded frame are still there tomorrow.
- On a Mac, remember the modifier remapping: right Command is Super, left
  Command is Alt. Shortcuts involving Alt will not do what the docs say
  otherwise.

## Stage 4 — DEM

`run_surfdata_to_DEM.m` converts the corrected 3D surface into a DEM data
product.

## Reference

- [Generating 3D Images](https://gitlab.com/openpolarradar/opr/-/wikis/Generating-3D-Images)
- [3D Surface Tracking](https://gitlab.com/openpolarradar/opr/-/wikis/3D-Surface-Tracking)
- [3D DEM Generation](https://gitlab.com/openpolarradar/opr/-/wikis/3D-DEM-Generation)
- [Slice browser user guide](https://gitlab.com/openpolarradar/opr/-/wikis/Data-Tracking-Tutorial#slice-browser)
- [Array worksheet](https://gitlab.com/openpolarradar/opr/-/wikis/OPR-Toolbox-Guide#array-worksheet)
