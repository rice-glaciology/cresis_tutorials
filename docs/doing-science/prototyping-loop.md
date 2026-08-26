# Prototype locally, scale remotely

The most useful habit for remote work is keeping a **short loop on your own
machine** and a **long loop on the servers**, with the same code running in
both. Iterating on numerics over a 200 ms round trip, against a shared node,
inside a GUI session, is miserable. Iterating on one frame locally is not.

The trick that makes this work is trivial and worth being strict about: **make
your local directory layout mirror the server's.**

## Get a frame

Many processed products are public, so you can start before you have server
access at all, and keep a local copy of anything you are actively working on.

[`scripts/fetch_frame.sh`](../scripts/fetch_frame.sh) pulls one quad-pol frame
into the server's layout:

```bash
./scripts/fetch_frame.sh                 # defaults: 20250108_02, frame 9
./scripts/fetch_frame.sh 20250108_02 12  # a different frame
```

```bash title="scripts/fetch_frame.sh"
DAY_SEG="${1:-20250108_02}"
FRM="${2:-9}"
SEASON="2024_Antarctica_Ground2"
DEST_ROOT="${3:-$HOME/data/opr/accum/$SEASON}"
BASE="https://data.cresis.ku.edu/data/accum/$SEASON"

FN=$(printf "Data_%s_%03d.mat" "$DAY_SEG" "$FRM")

for pol in HH VV HV VH; do
  dir="$DEST_ROOT/CSARP_standard_${pol}/$DAY_SEG"
  mkdir -p "$dir"
  curl -sS --fail -o "$dir/$FN" -C - "$BASE/CSARP_standard_${pol}/$DAY_SEG/$FN"
done
```

Each polarization is about 100 MB, so a quad-pol frame is roughly 400 MB. The
files are MATLAB v7.3 (HDF5). `curl -C -` resumes, so an interrupted download
picks up rather than starting over.

See [finding data](finding-data.md) for choosing *which* frame.

## MATLAB without a KU license

You do not need a license on the server to develop against these files.

- **Browser-based MATLAB in Docker** (`matlab-proxy`). Mount your repository
  into the container so host edits appear in MATLAB immediately and outputs
  survive restarts. Match the release to the servers' (`/opt/sw/matlab/2024b`)
  to avoid version surprises.
- **Octave** for the parts that do not need MathWorks toolboxes:

    ```bash
    docker run --rm --platform linux/amd64 \
      -v "$PWD":/work -w /work/scripts gnuoctave/octave:latest \
      octave --no-gui my_script.m
    ```

Note which toolboxes a code path actually needs — Signal Processing for most
real processing, Mapping for projections and maps, Image Processing for parts
of 3D work. Most analysis code needs none of them.

## Keep the layouts identical

```
~/data/opr/accum/2024_Antarctica_Ground2/CSARP_standard_HH/20250108_02/
/kucresis/scratch/<username>/…/CSARP_standard_HH/20250108_02/
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                              same from here down
```

With the tail identical, a script that takes a root and builds paths below it
runs unchanged in both places. No `if isunix`, no path juggling, no separate
"local" fork of the driver that quietly drifts from the real one.

The toolbox already supports this properly — set the roots in `gRadar` through
your `startup.m` profile and use the `opr_filename_*` helpers rather than
hand-built paths. See
[storage and file paths](../working-remotely/storage-and-paths.md).

## The loop

1. **Prototype locally** on one frame until the method is right. Short cycles,
   no queue, no shared node, and you can be offline.
2. **Mirror to the server.** Keep a copy of the repo under your scratch tree and
   [deploy edits atomically](../working-remotely/storage-and-paths.md#deploy-edits-atomically).
3. **Run one frame on the server** with `cluster.type = 'debug'`. This catches
   the environment differences — paths, toolbox versions, missing dependencies —
   while the failure is still cheap.
4. **Run at scale** through Slurm, detached, idempotent. See
   [running the cluster remotely](../working-remotely/cluster.md).
5. **Look at the results yourself**, in a
   [ThinLinc session](../getting-started/thinlinc.md).

Steps 1–4 are where tooling — including
[an assistant](../working-remotely/claude-code.md) — earns its keep. Step 5 is
not.

## Why step 5 does not get skipped

A pipeline that runs cleanly and produces a confident number nobody has looked
at is the failure mode to watch for. It is not that the code breaks; it is that
it does not, and the number is wrong anyway.

Some habits that catch this:

- Validate an estimator change on a **synthetic that reproduces the failure**
  before fixing it, then re-run the real validation frames from cache.
- Prefer soft weights to hard gates, and check every threshold against the
  frame's own distribution rather than a number you picked once.
- **Abstain rather than report the prior.** `NaN` where the data cannot support
  an answer is more useful downstream than a plausible number.

## Worked examples

- [Fabric from quad-pol accumulation radar](fabric-polarimetry.md)
- [Cross-track picking for multi-element swath data](swath-cross-track-picking.md)
