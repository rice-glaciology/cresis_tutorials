# Cross-track picking for multi-element swath data

With a multi-element array we can process each range line and build a **cross-track image** resolving energy as a function of direction of arrival.


## The chain
The processing steps can be broken up into five steps that are descirbed on the cresis wiki.

```
SAR processing            →  array processing        →  collation        →  picking      →  DEM
sar.m                        array.m                    tomo.run_collate    slice_browser   surfdata_to_DEM
                             CSARP_music                 surfdata files
```

!!! note "Before SAR"
    For a segment nobody has processed, we first have to run scripts that remove coherent-noise and equalize receiver channels. See [across-track energy, start to finish](swath-across-track-energy.md).

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
    the slice browser if you want to practice picking.

## Stage 1 — Array processing

`run_array.m` drives `array.m` using the
[array worksheet](https://gitlab.com/openpolarradar/opr/-/wikis/OPR-Toolbox-Guide#array-worksheet)
of the parameter spreadsheet. For 3D imaging you want a beam-forming or
subspace method. MUSIC (`CSARP_music`) is a method we use a lot rather than the
standard periodogram output, but there are other methods that are used to operate on the covariance matrix that characterizes the combined receive waveforms.

These jobs take a long time, so run it through Slurm; see
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

| Surface | Description |
|---|---|
| **Active** | The final two-way traveltime for this surface | 
| **Ground Truth** | Your supplied points, used to steer the tracker | 
| **Mask** | Binary ice mask; true means the surface may differ from air-ice | 
| **Quality** | Binary; false excludes the point from generated products | 
| **Surface** | Two-way traveltime to the air-ice surface |

Picking involves adding ground truth points to the image ground_gt, runing the tracker (apply TRW-S), inspect, add ground truth where it went wrong, re-run. Typically as long as you add ground truth every 5 traces the tracker can automatically deterct the bed.

### The tools

| Tool | Description |
|---|---|
| **TRW-S** | Tree-reweighted sequential tracker. Uses ground truth, ice surface and ice mask to write the active surface. Right-click and drag over a region, then select TRW-S. |
| **Delete** | Removes ground truth in the dragged region. |
| **Quality** | Right-click and drag sets quality to bad; **hold shift** to set good. Press `p` / `P` for a polygon select instead of a box. |

### echogram, across track and surface windows

The slice browser shows a **slice** view (the cross-track image at one range
line), a **surface** view (the tracked surface in map-ish view), and an
**echogram** view. Use your mouse motion to move between trackers.

To toggle between **zoom** mode (the default) and **tool**
mode press z.

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

The copy-forward keys (`n`, `m`, `h`, `j`) are intended to make picking a
long line a lot faster for layers that changes slowly in the across track trace-to-trace.

`step_size` is settable in the constructor or as a property during operation.

### Mouse, by window

**Slice window** — left click sets ground truth where you clicked; left click
and drag paints it along the mouse track; right click toggles selection of a
column; right click and drag selects which elevation bins get operated on.

**Surface window** — left or right click jumps the slice window to that slice.
Double click changes the slice view; **right click and drag applies the active
tool** to the region. Modifier keys shift bewteen quality tool selected (good or bad).

**Echogram window** — any click jumps the slice window to that slice.

## Stage 4 — DEM

`run_surfdata_to_DEM.m` converts the corrected 3D surface into a DEM data
product.

## Reference

- [Generating 3D Images](https://gitlab.com/openpolarradar/opr/-/wikis/Generating-3D-Images)
- [3D Surface Tracking](https://gitlab.com/openpolarradar/opr/-/wikis/3D-Surface-Tracking)
- [3D DEM Generation](https://gitlab.com/openpolarradar/opr/-/wikis/3D-DEM-Generation)
- [Slice browser user guide](https://gitlab.com/openpolarradar/opr/-/wikis/Data-Tracking-Tutorial#slice-browser)
- [Array worksheet](https://gitlab.com/openpolarradar/opr/-/wikis/OPR-Toolbox-Guide#array-worksheet)
