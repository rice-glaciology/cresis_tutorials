# 3. VS Code Remote-SSH

The [Remote-SSH extension](https://code.visualstudio.com/docs/remote/ssh) is
the cleanest remote development experience on these servers. Your local VS Code
connects over SSH, installs a small server-side component automatically, and
from then on editing feels local while everything actually runs on the CReSIS
node.

Almost everything works out of the box. This guide is mostly the handful of
things that do not, and is condensed from Thomas Teisberg's
[VS Code Workflow Tips](https://gitlab.com/openpolarradar/opr/-/wikis/VSCode-Workflow-Tips)
on the OPR wiki.

> Do the [OPR Toolbox Setup](https://gitlab.com/openpolarradar/opr/-/wikis/OPR-Toolbox-Setup)
> first. This guide assumes the toolbox already runs for you on the server.

## Connect

1. Install the **Remote - SSH** extension in VS Code.
2. Set up `~/.ssh/config` and key-based authentication as in
   [guide 2](ssh-and-tmux.md#a-reusable-ssh-config). Do not skip the keys —
   without them VS Code will prompt for your password over and over.
3. Press F1, run **Remote-SSH: Connect to Host**, and pick the `cresis` host you
   defined.
4. Open a folder. Most people use a single workspace pointed at their scripts
   directory, for example `/kucresis/scratch/<username>/scripts/`.

Because the SSH config indirects through a `Host` alias, VS Code neither knows
nor cares which login node it is actually on. Change `HostName` in the config
and reconnect; nothing else needs to change.

## The MATLAB extension

Add the
[MathWorks MATLAB extension](https://github.com/mathworks/MATLAB-extension-for-vscode).
It is more full-featured than you might expect: full autocompletion, debugging,
and the ability to run whole scripts, a selection, or a single section in an
auto-launched MATLAB instance. MathWorks has a
[write-up of the features](https://www.mathworks.com/help/cloudcenter/ug/run-matlab-in-visual-studio-code.html).

For a lot of people this is a better editing experience than the MATLAB IDE
itself.

## What it is not good at

**One MATLAB session, tied to your connection.** The extension manages exactly
one MATLAB session, and it dies with your VS Code remote connection. That is
fine for interactive debugging and wrong for anything long-running.

The workflow that works:

- Debug in the VS Code MATLAB session.
- Start long runs in a `tmux` session with `matlab -nodisplay`, so they survive
  disconnection. See [guide 2](ssh-and-tmux.md#tmux-dont-lose-a-job-to-a-dropped-connection).

**Plots are slow.** You can get MATLAB figure windows onto your laptop through
X11 forwarding, but X11 has no graphics compression, so it is sluggish for
anything you want to interact with. Keep a ThinLinc session open and use it
exclusively for `imb.picker` and other GUI work.

If someone works out how to route this X11 traffic through VNC or another
compressed transport, the OPR maintainers would like to hear about it.

## Monitoring cluster jobs

Once you are submitting real processing, watching Slurm and the OPR chain
output files gets tedious. Thomas Teisberg's
[opr-cluster-monitor](https://gitlab.com/openpolarradar/opr-cluster-monitor) is
a small web tool that reads the chain outputs and the Slurm queue and renders
progress bars, retries, and errors.
