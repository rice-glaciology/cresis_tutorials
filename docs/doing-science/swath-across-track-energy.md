# Across-track energy from a segment nobody has processed

The [cross-track picking](swath-cross-track-picking.md) page starts at SAR.
This page covers what has to happen **before** SAR, and what to check at
each step, when you want to measure how much energy comes back from each
direction across track. It is written from reprocessing multi-element P-3
MCoRDS segments (2013, 2014 and 2019 Greenland) from raw data.
Everything went wrong at least once.

The OPR wiki pages
[Coherent Noise](https://gitlab.com/openpolarradar/opr/-/wikis/Coherent-Noise),
[Receiver equalization](https://gitlab.com/openpolarradar/opr/-/wikis/Receiver-equalization)
and [Generating 3D Images](https://gitlab.com/openpolarradar/opr/-/wikis/Generating-3D-Images)
describe each tool. They do not say how the tools fit together for this
measurement, how to run them without a display, or what a bad result looks
like. That is what this page adds.

!!! warning "Why the order matters for this measurement"
    Angular spread is the quantity you want, and every uncorrected error
    shows up as angular spread.

    - **Coherent noise** that is left in is the same in every channel, so
      it fills all angles.
    - **Channel phase and gain errors** raise the array's sidelobes and
      move the beam centroid.
    - **Wrong array geometry** puts energy at the wrong angle.

    None of this makes a MUSIC image look obviously broken, which is why
    the checks below exist.

## 0. Decide whether the segment can do it at all

Do these before you queue anything.

**Count the receive channels.** Read `rx_paths` on the `radar` worksheet
of the season's parameter spreadsheet, and `imgs` on the `array`
worksheet. Then check `lever_arm.m` for the same season.

- The P-3 has 7 fuselage dipoles and 4 receive-only dipoles under each
  wing.
- The fuselage alone gives about a 15° beam. With the wings it narrows to
  about 2.4°.
- Some seasons flew without the wings: 2013 and 2019 are fuselage only.
- 2016 P-3 recorded 2 channels, so it cannot be processed this way at
  all.

**Know the waveforms.** On the same worksheet, read `Tpd`, `f0` and `f1`
for each waveform, and the flying height from the surface layer. You will
need them in step 3.

**Find where the season's calibration really lives.** The spreadsheet is
not always it.

- In 2019, the spreadsheet holds all-zero `chan_equal` and `Tsys` for the
  Image Thick Ice Mode segments.
- The real values are in that season's branch of
  `opr/matlab/missions/rds_settings.m`, and the released `CSARP_sar` was
  made with those.
- Always compare against the `param_sar` stored in an existing product.
  Load one chunk and read `param_sar.radar.wfs`.

**Check that paths still resolve.** Old spreadsheets name raw-data
directories that no longer exist. For example, the 2014 P-3 sheet names
`/cresis/snfs1/...`, but on mem1 the data is under
`/cresis/data/MCoRDS/2014_Greenland_P3/`. Override
`records.file.base_dir` rather than editing the shared spreadsheet.

**Check for existing products.** Someone may already have made SAR for
your frames. Look under `CSARP_sar*`, including suffixed copies such as
`CSARP_sar_ndh`. Before you reuse one, compare three things in its
`param_sar` with what you intend to use:

- `chan_equal_dB`, `chan_equal_deg` and `Tsys`;
- `Tadc_adjust`;
- whether coherent noise was removed.

`array` corrects the difference in `chan_equal` between SAR and the array
step. It does not correct a different `Tadc_adjust`, and it cannot add
coherent-noise removal after the fact.

**See how others calibrated the same season.** Do this even when their
products do not cover your segment. It is the precedent you will be
compared against, and it tells you which channels others trusted.

- `param_sar` and `param_array` in each product record the calibration
  used.
- `CSARP_equal` holds any per-segment equalization someone ran.
- The file's `param_equal` shows the reference channel, the waveform and
  the `rlines` they chose.
- For 2013 P-3, every existing multichannel product used the
  spreadsheet's season-wide values, identical for both waveforms. One
  segment's products also left out a channel.
- The only per-segment equalization in the 2013 tree used the 10 µs
  waveform over a 1,001-line calm stretch, with a different reference
  channel and an updated `Tsys`. It never made it into the spreadsheet.

## 1. The order

Every analysis step runs over the **whole segment**, whatever frames you
ask for, because that is how OPR estimates noise and calibration. On a
70-frame P-3 segment that is roughly 1,500 blocks of about 5 minutes each,
per pass.

| # | Step | OPR call | Writes | Runs | Check before moving on |
|---|---|---|---|---|---|
| 0 | Surface layer | `imb.picker` | `CSARP_layer` | you | The surface pick is continuous. Steps 4-5 extract a window around it. |
| 1 | Coherent noise, pass 1 | `analysis`, cmd `coh_noise` (`analysis_noise` worksheet) | `CSARP_analysis/coh_noise_*` | cluster | none |
| 2 | Collate pass 1 | `collate_coh_noise` | `coh_noise_simp_*` + threshold | session | `cn_plot`, `threshold_plot`: is the noise stable, and is it contaminated by the surface? |
| 3 | Coherent noise, pass 2 | `analysis` with `cmd.threshold` from pass 1 | `CSARP_analysis_threshold/coh_noise_*` | cluster | none |
| 4 | Collate pass 2 | `collate_coh_noise` | the noise SAR subtracts | session | Point `radar.wfs.coh_noise_arg.fn` at this directory. |
| 5 | Surface waveforms | `analysis`, cmd `waveform` (`analysis_equal` worksheet) | `CSARP_analysis_equal/waveform_*` | cluster | none |
| 6 | Equalization | `collate_equal` | `CSARP_equal/Equal_imglist_*` | session | **The table. See [section 2](#2-equalization-in-depth).** Do not run SAR until someone has looked at it. |
| 7 | SAR | `sar` | `CSARP_sar` | cluster | New `chan_equal` in `radar.wfs`, old `Tsys` kept |
| 8 | Array | `array`, `tomo_en = true` | `CSARP_music`, plus a power cube | cluster | [Section 4](#4-array-products-and-reading-energy) |
| 9 | Collate | `tomo.collate` | fused image, surfData (TRW-S) | cluster | Needs finished step 8. Queue it after, not in the same chain. |
| 10 | Check the bed | `imb.slice_browser` | corrected surfData | you | [Picking page](swath-cross-track-picking.md) |
| 11 | DEM | `tomo.surfdata_to_DEM` | `CSARP_DEM` | session | none |
| 12 | Across-track energy | your analysis of the **power** cube | - | anywhere | [Section 4](#4-array-products-and-reading-energy) |

Steps 2, 4, 6 and 11 are scripts or functions that run in your MATLAB
session and read what the step before wrote. They cannot be queued in the
same cluster chain as that step, because their input does not exist yet
when the chain is built. For the same reason, `tomo.collate` opens a
finished array frame while it builds its batch.

If the season was released without coherent-noise removal (2013 and 2019
P-3 were), you can skip steps 1-4. Then set
`radar.wfs(wf).coh_noise_method = ''`.

## 2. Equalization, in depth

Step 6 decides whether the array sees one plane wave or seven slightly
different ones. It is also the step most likely to fail quietly on a new
segment.

### Pick the right echo

`collate_equal` assumes a flat, single, nadir interface: one impulse from
straight down. The OPR wiki recommends flat water (lakes, ocean, or the
radiometric-calibration passes). Over an ice sheet you get the ice
surface, and the result is only as good as the stretch you use.

- **Do not use the whole segment by default.** Leaving
  `collate_equal.rlines` empty averages over turns, rough terrain and
  bad surface picks.
    - On 20130415_01, the noisy stretches in the relative-phase plot line up
      exactly with roll excursions of ±15° and jumps in the surface range.
    - Choose `rlines` where the relative phase is flat and roll is small.
      This is the step the upstream page asks for, and it is easy to skip in
      a scripted run.
- **Check that the surface echo is outside the transmit pulse.** The
  surface must be farther than `c·Tpd/2`. That is 150 m for a 1 µs pulse
  and **1.5 km for a 10 µs pulse**.
    - 2013 P-3 flew 20130415_01 low enough that the surface range stayed
      under 1 km. Its 10 µs waveform saw the surface through its own
      transmit pulse.
    - `collate_equal` still returned numbers. They were 17 dB and 123°
      changes on one channel, with timing scatter of about 100 ns.
    - Equalize long-pulse waveforms on something else: a deeper strong
      layer, the bed, or a flight segment at altitude.
    - Or decide explicitly to reuse a short pulse's coefficients. That is
      not free: in 2019, the 1 µs and 3 µs waveforms with the same
      transmitters differ by up to 78° on one channel.

### Waveforms that share an array image must share an equalization list

`collate_equal` works per **image list** (`collate_equal.img_lists`). It
estimates offsets against one reference channel (`collate_equal.ref`, a
row of the combined `[wf adc]` list). Then it subtracts that channel's
value from **every waveform in the list**.

- **If each waveform is its own list,** each is re-referenced to its own
  reference channel. Any calibration **between** waveforms is thrown away.
- **Why it matters for 2019 P-3.** Odd waveforms transmit on elements 1-3
  and even ones on 4, 6 and 7. Each pulse length's pair is processed as one
  14-channel virtual array. `rds_settings.m` gives waveform 2's reference
  element 1.4 dB and -58.5° relative to waveform 1. Equalizing waveform 2
  alone zeroes that, and the paired array image is then miscalibrated by a
  constant phase between its halves.
- **Do this instead:** `img_lists = {[1 2],[3 4],[5 6]}` with `ref = 3`,
  row 3 of the combined list, which is waveform 1's element 3. The
  analysis in step 5 can still run one image per waveform. The waveform
  files are per waveform and ADC, so regrouping needs no rerun.

!!! tip "Read changes net of the list's shift"
    If the list's own reference element started non-zero, the whole list
    moves by one constant. That is harmless inside one array image. In
    2019, the 3 µs pair moved by 85° and the 10 µs pair by -15.6°. Take the
    constant out before judging per-channel changes, or every channel looks
    as if it moved by 80°. The real hazard is a waveform that shares an
    array image with a waveform in a different list. Then the constants
    differ, and the image is miscalibrated.

### Tsys: read it, usually do not apply it

`collate_equal` also estimates a per-channel time offset (`Tsys_offset`).
Changing `Tsys` moves pulse compression. The waveforms you just analysed
were extracted with the old `Tsys`, so a new `Tsys` needs the analysis
rerun.

- **Keeping `Tsys`:** use `chan_equal_deg`, not
  `chan_equal_deg_with_Tsys`.
- **Reading the spread:** `Tsys_offset_std` in the tens of nanoseconds
  means the surface peak was not found consistently. Treat the whole
  table as suspect, not just the timing. On 20130415_01 it was about
  50 ns on the good waveform and about 100 ns on the bad one.

### Read the table like this

For each waveform, compare old and new `chan_equal_dB` and
`chan_equal_deg` per element.

| Pattern | What it usually means |
|---|---|
| Every element shifts by about the same phase, e.g. -12° to -21° | The **reference** channel moved. That is real, and fine. |
| Changes of a few tenths of a dB and a few degrees | A normal refinement. |
| One element 5-7 dB hot, with spikes to 30 dB in the amplitude plot | That channel misbehaves on the surface: coupling, saturation or a fault. Decide whether to use it. Do not just apply the number. |
| Changes of tens of dB or more than 90° | The estimate is noise. Check pulse length against range, and the `rlines`. |
| Every channel moved by about the same large phase, and the reference element went to 0 | The list shifted as a whole. Judge the changes net of that constant. |

Finally, rerun `collate_equal` with the new coefficients. As the upstream
page says, the offsets should come back near zero.

### Running collate_equal without a display

`collate_equal` is written to be run interactively. Under
`matlab -batch`, or any session without a display:

- **`'visible'`** in `debug_plots` stops at `keyboard`, and a batch run
  hangs.
- **`'comp_image'`** always docks its figures, and dies with
  `Cannot set WindowStyle to 'docked' when MATLAB is started with no display`.
  The upstream first-run recommendation includes both.
- **`'final'`** prints the coefficient table, but only after drawing a
  "phase filtered" figure. That figure smooths each channel with a filter
  about (range lines / 8) taps long, applied once per range line.
    - For a 750,000-line segment that is about 94,000 taps, and about
      **26 minutes per channel**, so hours per image.
    - Estimating the coefficients themselves took about 30 minutes per
      image.

What works:

1. **The first time, run it in a [ThinLinc](../getting-started/thinlinc.md)
   session** on a chosen `rlines` subset, with `'final'`, and look at the
   amplitude and phase plots.
2. **For scripted runs,** set `debug_plots = {'before_comp','after_comp','surf'}`.
   Then print the table yourself from the saved file. Every field is in
   it, whether or not `'final'` ran:

```matlab
E = load(fullfile(out_dir, 'CSARP_equal', sprintf('Equal_imglist_01_%s.mat', day_seg)));
for wf = find(~cellfun(@isempty, E.chan_equal_dB))
  old = E.param_equal.radar.wfs(wf);           % what the analysis started from
  fprintf('wf %d\n', wf);
  fprintf('  change dB   %s\n', mat2str(round((E.chan_equal_dB{wf} - old.chan_equal_dB)*10)/10));
  fprintf('  change deg  %s\n', mat2str(round(mod(E.chan_equal_deg{wf} - old.chan_equal_deg + 180, 360) - 180)));
  fprintf('  Tsys off ns %s\n', mat2str(round(1e9*E.Tsys_offset{wf}*10)/10));
  fprintf('  Tsys std ns %s\n', mat2str(round(1e9*E.Tsys_offset_std{wf})));
  fprintf('  sheet dB    %s\n  sheet deg   %s\n', E.chan_equal_dB_str{wf}, E.chan_equal_deg_str{wf});
end
```

`collate_equal` is a script. It reads `param` and `param_override` from
the workspace that calls it, and it leaves many variables behind. Call it
inside a small function, so it cannot overwrite your own variables.

## 3. On the cluster, while this runs

These are the things that cost time on mem1. The mechanics are in
[Running the cluster](../working-remotely/cluster.md).

- **Pack the small tasks.** Analysis blocks take about 5 minutes. Without
  `cluster.desired_time_per_job`, OPR submits one Slurm job per block, and
  its submit loop keeps only about half of `max_jobs_active` busy. Setting
  `desired_time_per_job = 7200` puts about 5 blocks in each job.
- **Keep finished blocks on a restart.** Set `cluster.rerun_only = true`.
  Without it, a restart deletes and redoes blocks that already finished.
- **The combine step is one job.** After the blocks, `analysis` runs a
  single combine job that writes one file per waveform and ADC.
    - It is submitted only when all blocks finish, so it waits behind
      everything else you queued.
    - For 2013 it took about 16 minutes per file, 14 files in all.
    - Plan for it. It is often the longest single wait.
- **Most warnings are benign.**
    - "Max memory potentially exceeded, automatically 1.5x" is OPR resizing
      the request.
    - A "syntax error in expression" in `error_N.txt` comes from the
      memory sampler in `cluster_job.sh`.
    - Neither means the task failed. Check that `out_N.mat` exists.
- **A killed job is not always a failed task.** One job finished all five
  of its tasks and then hung until its wall-time limit. OPR marked the
  tasks done. Check the `out/` files before you rerun anything.
- **Node availability varies.** During this run, 17 of 31 debug-partition
  nodes were drained and 8 were down. Check `sinfo` before you estimate
  how long anything will take.
- **Watch the heavy array jobs.** TRW-S (`tomo.collate`) and MVDR can run
  past OPR's own wall-time estimate. Raise `cluster.cpu_time_mult`, to 3-4
  for these, rather than letting a job die and retry with the same limit.

## 4. Array products and reading energy

**Make a power cube as well as MUSIC.**

- MUSIC (`method = 'music'`, `CSARP_music`) is what TRW-S tracks the bed
  on. Its pseudo-spectrum measures how well a direction separates from
  the noise subspace, not how much energy came from there. **Do not read
  amplitudes from it.**
- For energy, also run `method = 'standard'`, which is Bartlett
  delay-and-sum power. Optionally add `method = 'mvdr'`, which suppresses
  sidelobes from strong reflectors.
- Use the same `Nsv`, `bin_rng`, `line_rng`, `dline` and images for every
  method, so the cubes line up bin for bin. Give each its own `out_path`.
- For 15 P-3 channels: `Nsv = 128`, `bin_rng = -1:1`, `line_rng = -10:10`
  (63 looks). The OPR wiki's rule is looks "many times" the channel count.

**Steer from phase centres, not element positions.** The geometry
`lever_arm.m` returns is each channel's phase centre,
`(rx + tx_centroid)/2`, used with the two-way wavenumber `4πf/c`. Using
raw receive positions doubles every baseline, and every angle comes out
wrong by a factor of two.

**Know the array's own response before you read the ice's.**

| P-3 layout at 195 MHz | -3 dB main lobe | Grating lobes |
|---|---|---|
| Full array (15 channels, 2014) | 2.35° | **-1.5 dB at ±6.8°**, -6.3 dB at ±13.8° |
| Fuselage only (7 channels, 2013) | 15.4° | none |
| 2019 transmit pairs (14 virtual channels) | 11.4° | none |

- **What this means for the full array.** A perfectly specular flat
  reflector puts about two thirds of its power in the grating lobes,
  outside ±3° of nadir. A raw "fraction near nadir", or a raw angular
  spread, is mostly the array.
- **Compare against a flat specular reflector.** Take the same window and
  the same beamformer, and report the excess over it. For example,
  `sqrt(spread² - spread_ref²)`, and nadir power relative to the
  reference's.
- **Centre the window on the return, not on nadir.** A fixed window
  centred on nadir clips the lobes unevenly for a dipping layer and pulls
  the centroid toward nadir.

**Average over equal time, not equal height.**

- For each slab above the bed, average every angle over the **same
  fast-time samples**. The array's response acts at one fast time, the
  same at every angle, so only equal-time slabs let you subtract the
  reference exactly.
- Per-angle windows by height along each ray gave false spread wherever
  thin bright layers crossed a slab edge.
- The cost is that an off-nadir echo at the same time sits higher than the
  nadir height axis says: by `(D - h)(1 - cos θ_ice)`. That is about 35 m
  at 2.5 km depth and 10° in ice.

**Subtract the noise floor first.** Noise is white across the channels,
so it fills every angle and reads as spread. Estimate it per angle from
samples well below the bed, for example more than 1 µs below, and
subtract it before any weighting.

## Checklist for a new segment

- [ ] Enough receive channels, and the array geometry matches `lever_arm.m`
- [ ] Calibration source identified: spreadsheet, `rds_settings.m`, or an existing product's `param_sar`
- [ ] Raw-data path resolves; surface layer is clean
- [ ] Coherent noise: two passes, plots checked, `coh_noise_arg.fn` points at pass 2
- [ ] Equalization: `rlines` chosen on a calm stretch; every waveform's surface outside its transmit pulse
- [ ] Waveforms that share an array image are in one `img_lists` entry
- [ ] Equalization table read: pattern understood, bad channels decided on, rerun offsets near zero
- [ ] SAR run with the new `chan_equal` and the old `Tsys`
- [ ] MUSIC for tracking, a power cube for energy, same grid
- [ ] Energy read against the array's own response, in equal-time slabs, after the noise floor

## Reference

- [Receiver equalization](https://gitlab.com/openpolarradar/opr/-/wikis/Receiver-equalization): `collate_equal` fields, choosing `rlines`, applying Tsys
- [Coherent Noise](https://gitlab.com/openpolarradar/opr/-/wikis/Coherent-Noise): the two-pass method and its plots
- [Generating 3D Images](https://gitlab.com/openpolarradar/opr/-/wikis/Generating-3D-Images): `array` settings for 3D
- [Cross-track swath picking](swath-cross-track-picking.md): SAR onward, and the slice browser
- Paden et al. 2010, *J. Glaciol.*, MUSIC 3-D bed tomography. doi:10.3189/002214310791190811
- Byers et al. 2012, *IEEE TIM* 61(5), the P-3 dipole array
- Rodriguez-Morales et al. 2014, *IEEE TGRS*, the MCoRDS instruments. doi:10.1109/TGRS.2013.2266415
