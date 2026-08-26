# MATLAB from a distance

MATLAB is the toolbox's native environment and it is licensed on the servers.
The remote question is *which* MATLAB you should be talking to, and through
what.

## Four ways to run it

| How | Good for | Survives disconnection? |
|---|---|---|
| ThinLinc desktop | GUIs: `imb.picker`, slice browser | Yes (disconnect, don't log out) |
| VS Code MATLAB extension | Interactive debugging | **No** |
| `matlab -nodisplay` in tmux | Long runs, batches | Yes |
| `matlab -batch "script"` | Unattended jobs | Yes, with `nohup` |

The mistake to avoid is running a six-hour job in the VS Code session because
that is where you were debugging. It dies with the connection.

## Starting up

Add MATLAB to your path in `~/.bashrc`:

```bash
export PATH=/opt/sw/matlab/2024b/bin/:$PATH
```

A healthy start prints the startup script's work:

```
Startup Script Running: /local_home/<username>/startup
  Resetting path
  Adding cresis path: /local_home/<username>/scripts/opr/matlab
  Adding personal path: /local_home/<username>/scripts/run_opr
  Setting global preferences in global variable gRadar
```

If you do not see `gRadar` being set, nothing downstream will find its files.
See [storage and file paths](storage-and-paths.md).

!!! warning "MathWorks License Update dialog"
    If it appears, **close the window**. Do not choose "Update".

## Long runs

```bash
tmux new -s processing
matlab -nodisplay
```

`Ctrl-b d` to detach, `tmux attach -t processing` to return. For fully
unattended work:

```bash
nohup matlab -batch "run_my_batch" > logs/batch_$(date +%F).log 2>&1 &
```

`-batch` runs the script, exits on completion, and returns a non-zero status on
error — which makes it scriptable in a way that `-r` is not.

## Be a good citizen on shared nodes

The login nodes are shared. MATLAB will otherwise happily take every core:

```matlab
maxNumCompThreads(8);
```

and `nice` anything long-running:

```bash
nice -n 10 matlab -batch "run_my_batch"
```

Put both in your [`CLAUDE.md`](claude-code.md#give-it-the-project-context) if
you are using an assistant, so it happens by default rather than when you
remember.

Real processing belongs on the [cluster](cluster.md), not the login node.

## Plots

Two options, and the choice matters more remotely than locally:

- **X11 forwarding** (`ssh -Y`, `ForwardX11 yes`) — figures appear on your
  laptop. Fine for a quick `imagesc`. **Uncompressed**, so genuinely painful for
  anything interactive.
- **ThinLinc** — compressed, responsive. Use it for `imb.picker`, the
  [slice browser](../doing-science/swath-cross-track-picking.md), and any
  figure you intend to click on.

For batch work, skip the display entirely and write files:

```matlab
h = figure('Visible','off');
% ...
print(h,'-dpng','-r150',out_fn);
```

Then pull the PNGs down with `rsync`. This is usually the fastest way to review
a hundred frames' worth of output from another continent — far faster than
paging through them over a remote display.

## Toolbox dependencies

Most users need none of these, but when something fails with an undefined
function it is usually one of:

| Toolbox | Needed for |
|---|---|
| Signal Processing | Most real processing and many support functions |
| Mapping | Any map besides blank geodetic; coordinate conversions in processing and posting |
| Image Processing | Parts of 3D processing (`medfilt2`, `bwdist`, `bwboundaries`) |
| Compiler | `mcc` for Torque/Slurm — only when cluster code changes |
| Optimization + Global Optimization | Parametric estimation in 3D imaging |
| Parallel | `cluster.type = 'matlab'` and GPU work only |

`ct_remove_toolboxes.m` tests whether code depends on toolbox routines. If you
find toolbox usage that was committed accidentally, email
`opr@openpolarradar.org`.

## Without a license

For local prototyping you do not need the server at all — see
[prototype locally, scale remotely](../doing-science/prototyping-loop.md) for
browser-based MATLAB in Docker and the Octave route.

Note also that once `cluster_job.m` is compiled, the **compiled code runs
without a MATLAB license**, needing only the freely distributable MATLAB
Compiler Runtime. Compiled output is cross-platform.

## Learning MATLAB

The toolbox ships three tutorials in its `matlab` directory —
`matlab_tutorial1_general.m`, `matlab_tutorial2_general.m`,
`matlab_tutorial3_radar.m`. Open one with `edit`, set a breakpoint on the first
code line, and step through with F10 watching the workspace.

Tutorials 4, 5, 6, 11 and 12 of the first file need
[support files](https://data.cresis.ku.edu/data/temp/MATLAB_tutorial_files.zip),
unzipped to `/tmp/MATLAB_tutorial_files/` (or `C:\tmp\…` on Windows). Note that
the second tutorial file still assumes the CReSIS HPC environment.

New to MATLAB entirely? MathWorks'
[onramp course](https://matlabacademy.mathworks.com/details/matlab-onramp/gettingstarted)
is a better starting point than the toolbox tutorials.
