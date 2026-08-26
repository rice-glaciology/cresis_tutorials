# Running the cluster remotely

The OPR cluster interface wraps several schedulers behind one API. What changes
when you are remote is not how you submit, but what happens when a job fails at
3 a.m. your time and nobody is awake to look at it.

## Cluster types

Set `cluster.type` in `gRadar` or a `param_override`:

| Type | Needs compiler | Notes |
|---|---|---|
| `'debug'` | Optional | Runs tasks in your current MATLAB session. **Start here.** |
| `'slurm'` | Yes | `sbatch`/`squeue`/`scancel`. The production path at KU. |
| `'torque'` | Yes | PBS/Torque via `qsub`/`qstat`/`qdel`. |
| `'matlab'` | No | MATLAB Parallel Toolbox local cluster. |

Under `'debug'`, `cluster.run_mode` picks how tasks execute: `1` runs
`cluster_job.m` directly, `2` runs a compiled version, `3` runs
`cluster_job.sh`.

!!! tip "Always get one frame through `'debug'` first"
    It needs no compilation and fails in your session where you can see the
    stack. Compiling and queueing to discover a typo is a slow way to find it.

## Structure

Tasks are grouped into **jobs**, jobs into **batches**, batches into **chains**.
Nothing advances until every job in the batch completes. All the commands live
in the `cluster` directory of the toolbox and are named `cluster_*`.

## Submitting

```matlab
cluster_compile                                  % only when code changed
out = cluster_submit_batch('hanning',true,{10},1,60,500e6);
```

The arguments after the function name are: block until done, input arguments,
number of tasks, CPU time estimate, memory estimate.

For anything long, use the **non-blocking** form so you can detach and poll:

```matlab
ctrl = cluster_submit_batch('hanning',false,{10},1,60,500e6);
ctrl_chain = {{ctrl}};
[~,chain_id] = cluster_save_chain(ctrl_chain);
```

`cluster_save_chain` prints the two lines needed to pick the chain back up in a
fresh session:

```matlab
[ctrl_chain,chain_fn] = cluster_load_chain([],1);
ctrl_chain = cluster_run(ctrl_chain);
```

**This is the part that matters remotely.** A saved chain survives your session
dying. Losing your VPN does not lose the run — you reconnect, load the chain and
carry on.

## Polling

```matlab
while true
  ctrl_chain = cluster_run(chain_id,false);
  cluster_save_chain(ctrl_chain,chain_id,false);
  if ~any(isfinite(cluster_chain_stage(ctrl_chain)))
    break    % everything completed or failed
  end
  pause(10);
end
```

Run this inside [`tmux`](../getting-started/ssh-and-tmux.md) so it survives
disconnection. Then:

```matlab
[in,out] = cluster_print(ctrl_chain{1}{1}.batch_id,1,0);
cluster_cleanup(ctrl_chain{1}{1}.batch_id);
```

`cluster_print` is how you read a failed job's stdout — the first thing to
reach for when something died overnight.

## Slurm commands worth knowing

```bash
squeue -u <username>                     # your jobs
squeue --job JOBID                       # one job
scontrol show job JOBID                  # everything about a job
sacct -u <username> --format=JobID,JobName,MaxRSS,Elapsed
sinfo                                    # nodes and states
scancel JOBID                            # kill one
scancel -u <username>                    # kill all of yours
sacctmgr list qos                        # your limits: max jobs, cores, cpu time
```

`MaxRSS` from `sacct` is how you find out what a job *actually* used, which is
the input to fixing a memory-exceeded failure rather than guessing.

An interactive node, useful for debugging something that only fails under the
scheduler:

```bash
srun --partition=cresis --nodes=1 --ntasks-per-node=1 --time=01:00:00 --pty bash -i
```

## Designing batches to survive the night

You are usually asleep when a long batch fails. Three properties make that a
non-event:

**Idempotent.** A rerun skips any frame whose output already exists. Then
recovery is re-running the same command, not reconstructing which frames were
left. Cache the expensive intermediates so the skip is cheap.

**Capped retries.** Write fail markers so one pathological frame cannot consume
the run. The toolbox does this for cluster retries; do the same in your own
batch loops.

**Warn and continue.** A single bad frame should not abort a fifty-frame batch —
warn, skip, and **name every skipped frame in the log tail**. A downstream
figure that says "missing" cannot distinguish a frame that failed from one you
never requested.

```bash
matlab -batch "run_my_batch" > logs/batch_$(date +%F).log 2>&1 &
```

Detach it, then read the log in the morning.

## Common failures

**CPU or wall time exceeded.** Raise the multiplier and re-run:

```matlab
ctrl_chain = cluster_set_chain(ctrl_chain,'cluster.cpu_time_mult',2);
ctrl_chain = cluster_reset(ctrl_chain);   % if it ran out of retries
ctrl_chain = cluster_run(ctrl_chain);
```

To measure rather than guess, run the job locally under
`bash/watch_cpu_mem.sh`.

**Stale NFS / deploy lock.** Symptoms in the stdout of a failed job:

```
terminate called after throwing an instance of 'dsFileBasedLockError'
  what():  Exclusive create failed on …/.deploy_lock.1 (reason: Stale NFS file handle)
```

Often transient — `dbcont` at the `cluster_run` keyboard prompt resubmits and
works. Check the lock is gone first: `ls -la ~/.matlab/mcr_v716/`. A persistent
permission problem in that directory is fixed by `rm -rf ~/.matlab/mcr*`.

**Compiled code out of date.** The compiler cannot detect a MATLAB version
change or new hidden dependencies. Force a recompile by running
`cluster_compile` with no arguments.

**Task function inside a package.** The `_task` function may **not** live in a
`+package` directory, though everything it calls may. Relatedly, never run the
compiler from inside a package directory — dependencies come out wrong.
`torque_compile` tries to catch this.

## Monitoring without staring at a terminal

[opr-cluster-monitor](https://gitlab.com/openpolarradar/opr-cluster-monitor)
reads the OPR chain output files and the Slurm queue and renders progress bars,
retries and errors as a web page. Forward its port over your SSH connection and
it is a far better way to check on a run from a phone than `squeue`.

## Reference

- [Cluster Guide](https://gitlab.com/openpolarradar/opr/-/wikis/Cluster-Guide) —
  every `cluster_*` function, settings, input/output file formats
