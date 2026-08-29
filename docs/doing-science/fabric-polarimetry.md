# Fabric from quad-pol accumulation radar

Here we walk through a tutorial that shows how we can infer horizontal ice-crystal orientation fabric from polarimetric radar traveltimes using the CReSIS ground-based accumulation radar.
This page walks through the processing steps, demonstrates how to run the model and the figures that it writes.

The method follows Rathmann (2026), *Inferring glacier ice-crystal orientation
fabrics from oblique polarimetric radar* (Proc. R. Soc. A), implemented in a
`+ptt` MATLAB package with a thin OPR adapter around it.
f

## What we are measuring

A birefringent ice column splits an incident wave into two orthogonally polarized modes travelling at slightly different speeds. 
Over depth this accumulates a **traveltime difference** between HH and VV, and the size of that difference constrains the horizontal fabric

$$\Delta\lambda = \lambda_x - \lambda_y$$

The chain measures $\Delta\tau(\text{twtt}, x)$ and inverts it for $\Delta\lambda$ over depth intervals.

For this example, we'll be focused on a season that has been processed with **separate per-polarization products**. 
For `2024_Antarctica_Ground2` that is:

```
CSARP_standard_HH/   CSARP_standard_VV/
CSARP_standard_HV/   CSARP_standard_VH/
```

These products are generated running `qlook` / `sar` / `array` in the OPR processor for each polarization channel.
See `run_polarimetric.m` in the toolbox and the
[Parameter Spreadsheet Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Parameter-Spreadsheet-Guide) for more information on this.

!!! warning "The qlook products must be complex"
    If a season was processed with `inc_dec` non-zero, the products are
    detected power and the imaginary component of HH/VV which descibes the phase difference is gone. 

## Stage 1 — Polarimetric synthesis and coregistration

`polarimetric.m` (existing toolbox step) synthesizes a rotated basis, coregisters
the reference and secondary channels, forms the multilooked interferogram and
coherence, and optionally unwraps the phase with SNAPHU.

You can run this 

```matlab
coregistration.en = true
snaphu_en         = true    % strongly preferred
```

The ouout will be located at `CSARP_polarimetric` (or whatever you set `out_path`. The next stage's `in_path` must match).

This is the expensive stage. Coregistration runs tens of minutes per frame.

## Stage 2 — Fabric inversion

`fabric.m` / `fabric_task.m` is the OPR adapter; the numerics live in `+ptt`.
Per frame it:

1. **Estimates $\Delta\tau$** by one of three routes, set by
   `fabric.dtau_source`:

    | `dtau_source` | Description |
    |---|---|
    | `'phase'` (default) | Blends coregistration row offsets (fixes sign and the integer fringe ambiguity) with interferogram phase (sub-ns precision). Uses SNAPHU-unwrapped phase when present. |
    | `'coreg'` | Row offsets alone. Uses detected-power products and no phase survives. |
    | `'deltak'` | Split-spectrum ladder over the ref/sec SLC spectra, coarse-to-fine in synthetic wavelength. **Absolute** $\Delta\tau$, no unwrapping. Low-coherence sites where SNAPHU produces region errors. This is also a useful unwrap-free cross-check anywhere. |

    !!! danger "delta-k must use the raw `sec`, not `sec_reg`"
        `sec_reg` has been envelope-shifted by coregistration and carries no
        group delay. Delta-k needs the unregistered secondary SLC in the
        product, which roughly doubles task memory.

2. **References $\Delta\tau$ to zero over a coherent band** just below the
   surface return, removing channel timing and phase biases and the unwrapping
   constant.

3. **Averages into along-track blocks** with coherence weighting.

4. **Inverts** through a Maxwell-Garnett firn model for piecewise-constant
   $\Delta\lambda$ over `num_intervals` depth intervals:

    - `inversion = 'joint'` — smoothness-regularized joint solve. The module
      default, and robust to noisy data.
    - `inversion = 'stripping'` — exact layer stripping.

Output: `CSARP_<out_path>/<day_seg>/Data_*.mat` plus overview images.

## Running it

### One frame, interactively

`run_fabric.m` is the driver. The shape of it:

```matlab
params = read_param_xls(opr_filename_param('accum_param_2024_Antarctica_Ground2.xlsx'));

params = opr_set_params(params,'cmd.generic',0);
params = opr_set_params(params,'cmd.generic',1,'day_seg','20250108_02');
params = opr_set_params(params,'cmd.frms',[9]);

% in_path MUST match the polarimetric out_path from stage 1
params = opr_set_params(params,'fabric.in_path','polarimetric_unwrap');
params = opr_set_params(params,'fabric.out_path','fabric_joint');

% traveltime difference
params = opr_set_params(params,'fabric.coherence_threshold',0.5);
params = opr_set_params(params,'fabric.use_snaphu_phase',true);
params = opr_set_params(params,'fabric.blend_coreg_en',true);
params = opr_set_params(params,'fabric.phase_sign',0);   % 0 = auto from coregistration
params = opr_set_params(params,'fabric.block_size',1000);

% inversion
params = opr_set_params(params,'fabric.inversion','joint');
params = opr_set_params(params,'fabric.num_intervals',10);
params = opr_set_params(params,'fabric.half_offset',0);

% firn-ice column model (see ptt.defaultParams)
params = opr_set_params(params,'fabric.ptt',struct( ...
  'H',2000,'bco_depth',60,'lam_z_sfc',1/3,'lam_z_bed',1/3));
```

Writing to `fabric_joint` rather than `fabric` keeps earlier stripping outputs
in place for side-by-side comparison — worth doing whenever you change the
solver.

Start with `cluster.type = 'debug'`, which needs no compilation. Move to
`'slurm'` only once a single frame runs clean.

### Whole seasons

For batches that bypass `master.m` and the parameter spreadsheets entirely,
`server/run_fabric_scratch.m` runs `fabric_task` over every frame of each input
product in a per-product season table, writing to a **user scratch tree** rather
than the shared season tree. `server/run_deltak_scratch.m` is the same shape
with `dtau_source = 'deltak'`, restricted to products that carry the complex
ref/sec SLCs, so the two can be compared side by side.

Launch by hand from a `tmux` session:

```bash
matlab -batch "run_fabric_scratch" > logs/fabric_$(date +%F).log 2>&1 &
```

!!! tip "A bad frame must not cost the run"
    Runtimes are long by nature — tens of minutes per frame for
    coregistration, longer for a tiled SNAPHU unwrap, over surveys of dozens of
    frames. Every batch here **warns and continues** per frame rather than
    aborting, and names the skipped frames in the log tail. A figure that says
    only "missing extract" cannot distinguish a failed frame from one that was
    never requested.

See [running the cluster remotely](../working-remotely/cluster.md) for
detaching, monitoring, and picking up after an overnight failure.

## Caching

Coregistration caches (`stages/quadpol/coreg_cache/creg_<tag>.mat`) run to
roughly 0.7 GB per frame and take inversion reruns down to about twelve minutes
a frame. **Do not delete them casually** — they are the difference between
iterating on the inversion in an afternoon and iterating over a week.

Deep or special runs use a `z_max` override, which produces `_z<N>`-suffixed
outputs that never clobber batch products.

## Deploying the module on the servers

- `fabric.m`, `fabric_task.m` → `opr/matlab/processing/`, or keep them on your
  personal path.
- `run_fabric.m` → your `run_opr` repo (`gRadar.path_override`), edited per
  season.
- `+ptt` → on the MATLAB path, e.g. `opr/matlab/+ptt` or your `run_opr` repo.
- For **compiled cluster modes**, add `{'fabric_task.m' 2}` to
  `gRadar.cluster.hidden_depend_funs` in `startup.m` and re-run
  `cluster_compile`. `cluster.type = 'debug'` needs none of this.
- Parameter spreadsheet: add a `fabric` worksheet (row 1 field names, row 2 type
  codes, one row per segment matching the `cmd` sheet order) with e.g.
  `out_path`(t), `in_path`(t), `fc`(r), `block_size`(r), `num_intervals`(r),
  `ptt.H`(r), `ptt.bco_depth`(r). Enable per segment via the `cmd` sheet
  `generic` column: `{{'fabric','fabric'}}`.

!!! note
    `master.m` currently only propagates `ctrl_chain`s for `analysis` generic
    steps, so drive this through `run_fabric.m` until that one-line change is
    upstreamed.

Remember to [deploy edits atomically](../working-remotely/storage-and-paths.md#deploy-edits-atomically)
— never truncate a script a running job is reading.

## Validation habits

These are the ones that have actually caught errors:

- **Reproduce the failure on a synthetic before fixing it**, then re-run the
  real validation frames from cache. A fix validated only on the data that
  motivated it is not validated.
- **Check the chain against raw fringe density**, which is proportional to
  $\Delta\lambda$ with no inversion involved. Calibrate against
  `ptt.twttDifference` directly rather than a hand-derived constant — hand
  deriving it drops the two-way factor that lives inside `twttDifference` and
  produces a spurious factor of 2 that looks exactly like a real bug.
- **Sweep the coherence gate on adjacent-block agreement, not misfit RMS.** RMS
  is a post-regularization residual that always improves with more free
  parameters, so it will happily endorse an overfit.
- **Test whether a deep feature is a domain edge.** Sweep interval count,
  column-model bed depth `H`, and record truncation depth. The decisive test:
  an edge effect propagates inward, so values well above the cut must not move
  when the cut moves.
- **Never unwrap axis angles.** Smooth or interpolate the doubled-angle phasor
  instead. A 0/180 heading wrap in an interpolation is easy to introduce and
  very hard to see.
- **Abstain rather than report the prior.** Returning `NaN` where the data
  cannot support an answer is far more useful downstream than a plausible
  number, and $\theta_0$ should never be depth-averaged through a region where
  the axes rotate with depth.

## Next

[Cross-track picking for swath data](swath-cross-track-picking.md) — the other
half of multi-element work, where you pick in the across-track dimension rather
than inverting for a column property.
