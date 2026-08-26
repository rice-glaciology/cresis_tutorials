# Storage and file paths

Where things live, what the toolbox expects, and what not to delete. This is
the page that stops you hand-building paths that break the moment you move
between your laptop and the server.

## `gRadar` and `startup.m`

`startup.m` (`example_startup.m` in the toolbox) creates the global `gRadar`
structure, sets the MATLAB path, and lists hidden dependencies for
`cluster_compile.m`. Several profiles ship with it, and selecting the right
profile for your environment is often all you need.

The fields that matter most:

| Field | What it points at |
|---|---|
| `path` | The OPR toolbox itself |
| `path_override` | **First** on the path, so it overrides everything else. Your personal/temporary files and drivers. |
| `param_path` | Your parameter spreadsheets repo (`opr_params.git`) |
| `tmp_path` | Your personal temporary files |
| `opr_tmp_path` | **Shared** temporary files |
| `support_path` | The `opr_support` tree: `gps`, `records`, `frames` |
| `out_path` | Output data products (`CSARP_*`) |
| `data_path` | Raw radar data (usually unused — `records.base_path` gives the full path) |
| `data_support_path` | Raw metadata: system measurements, GPS/INS |
| `gis_path` | GIS files the toolbox expects |
| `cluster` | Cluster settings — see [running the cluster](cluster.md) |
| `ops.url` | `https://ops.cresis.ku.edu/` |
| `data.url` | `https://data.cresis.ku.edu/` |

!!! warning
    `clear all` and `clear global gRadar` remove `gRadar` from memory
    completely, and `path(pathdef)` resets the path. Both mean re-running
    `startup`. This bites most often at the top of a script that starts with a
    reflexive `clear all`.

## Support files

Raw radar data and metadata are converted into standard formats and stored
under `opr_support`:

```
gps/SEASON/gps_YYYYMMDD.mat
records/RADAR_NAME/SEASON/records_YYYYMMDD_SS.mat
frames/RADAR_NAME/SEASON/frames_YYYYMMDD_SS.mat
```

where `SEASON` is `YYYY_LOCATION_PLATFORM` (e.g. `2011_Greenland_P3`),
`RADAR_NAME` is the system name from `opr_output_dir` (`accum`, `kaband`,
`kuband`, `rds`, `snow`), `YYYYMMDD` is zero-padded, and `SS` is the zero-padded
segment.

## Output products

Under `out_path`, one directory per processing stage:

| Directory | Output of |
|---|---|
| `CSARP_qlook` | `qlook.m` — quick look |
| `CSARP_deconv` | `qlook.m` with deconvolution |
| `CSARP_analysis` | `analysis.m` — coherent noise, equalization, specular/deconvolution |
| `CSARP_sar` | `sar.m` — SAR processing |
| `CSARP_standard` | `array.m` with standard (periodogram) array processing |
| `CSARP_mvdr` | `array.m` with MVDR |
| `CSARP_music` | `array.m` with MUSIC — the 3D volume products |
| `CSARP_post` | `post.m` — posted products |

Custom modules add their own, e.g. `CSARP_polarimetric` and `CSARP_fabric_joint`.

## Build paths with the helpers

Use the `opr_filename_*` functions rather than string concatenation, and always
`fullfile` for cross-platform safety. They take the parameter structure that
`read_param_xls.m` produces.

```matlab
param = struct('radar_name','mcords5', ...
               'season_name','2015_Greenland_Polar6', ...
               'day_seg','20150730_01');

opr_filename_out(param,'qlook','')
% /kucresis/scratch/dataproducts/opr_data/rds/2015_Greenland_Polar6/CSARP_qlook/20150730_01

opr_filename_support(param,'','records')
% …/opr_support/records/rds/2015_Greenland_Polar6/records_20150730_01.mat
```

Full path to a combined echogram, or to a subimage:

```matlab
frm = 1;
fullfile(opr_filename_out(param,'qlook',''), ...
         sprintf('Data_%s_%03d.mat', param.day_seg, frm))

img = 1;
fullfile(opr_filename_out(param,'qlook',''), ...
         sprintf('Data_img_%02d_%s_%03d.mat', img, param.day_seg, frm))
```

The rest: `opr_filename_data` (raw — prefer `get_segment_file_list.m`),
`opr_filename_gis`, `opr_filename_param`, `opr_filename_tmp` (personal temp),
`opr_filename_opr_tmp` (shared temp).

This is the mechanism that makes
[local prototyping](../doing-science/prototyping-loop.md) work: change the roots
in your `gRadar` profile, and the same script addresses your laptop or the
server.

## Filename conventions

If you write files, follow the toolbox conventions so downstream parsers cope:

- `-` and `+` in front of signed numbers.
- `p` for the radix point: `34p5`.
- Fixed significant figures, zero-padded: a signed value 34.5 with 5 digits and
  2 decimals is `+034p50`; an unsigned integer 34 with 4 digits is `0034`.

Use **`ct_save`** rather than `save` for `.mat` files — it checks free disk
space before starting and always writes v7.3 (HDF5). Print the filename before
saving:

```matlab
fprintf('Save %s (%s)\n', out_fn, datestr(now));
```

Results that depend on the standard `param` structure should store it:

```matlab
out.(['param_' mfilename]) = param;
out.param_records = records.param_records;   % if it depends on records
ct_save(fn,'-struct','out');
```

## Deploy edits atomically

On a shared filesystem with jobs running, an editor that truncates and rewrites
a file can corrupt a script a running MATLAB process is still reading. Write to
a new file and move it into place — `mv` within a filesystem is atomic:

```bash
cat > script.m.new && mv script.m.new script.m
```

Never truncate a script a running job depends on.

## Caches and what not to delete

Intermediate caches are often the difference between iterating in an afternoon
and iterating over a week. In the
[fabric chain](../doing-science/fabric-polarimetry.md), coregistration caches
run to roughly 0.7 GB a frame and take inversion reruns down to about twelve
minutes.

- **Do not clear caches to free space** without checking what regenerating them
  costs. That number is usually much larger than the disk you recover.
- **Version your outputs instead of overwriting.** A `z_max` override producing
  `_z<N>`-suffixed outputs never clobbers batch products; writing to
  `fabric_joint` rather than `fabric` keeps the previous solver's results for
  comparison. Disk is cheaper than a re-run you cannot reproduce.
- **`umask 002` means group-writable.** You can delete other people's files.
  Check what a path resolves to before pointing anything destructive at it.

## Scratch versus shared trees

Season trees under `dataproducts` are shared. Your own scratch tree
(`/kucresis/scratch/<username>/…`) is yours.

Batch experiments should write to **your scratch tree**, not the shared season
tree, until the results are worth publishing to everyone. Several of the fabric
batch drivers do exactly this deliberately.

Quotas are not documented here because they change; check with
`opr@openpolarradar.org` before staging anything large.
