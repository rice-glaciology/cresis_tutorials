# Accounts and first day

You need an OPR/CReSIS account on one of the login nodes. In this group that
normally means a `*_sta` username and a login node such as
`lps3.cresis.ku.edu`, reachable directly, 24 hours a day.

If you do not have one yet, ask your advisor to request it through
`opr@openpolarradar.org`. Do not start the rest of this until you can log in.

## Conventions in these guides

Throughout, replace:

- `<username>` — your account name
- `<node>` — your login node, e.g. `lps3.cresis.ku.edu`

**Your account setup email always wins.** If a hostname in it differs from an
example here, use the email.

## First-day checklist

Work through these in order. Each links to the guide that covers it. Expect
this to take an afternoon, not ten minutes.

1. **Get a shell.** [SSH](ssh-and-tmux.md) — prove you can log in before
   anything else. If this fails, nothing downstream will work.
2. **Set up keys and an SSH config.**
   [Guide](ssh-and-tmux.md#a-reusable-ssh-config) — five minutes now, saves
   hundreds of password prompts later, and VS Code effectively requires it.
3. **Get a desktop.** [ThinLinc](thinlinc.md) — you will need it for
   `imb.picker`, and it is better to set it up before the day you actually need
   a GUI.
4. **Learn `tmux` before you need it.**
   [Guide](ssh-and-tmux.md#tmux-dont-lose-a-job-to-a-dropped-connection) — the
   first long job you lose to a dropped connection will teach you this anyway.
   Better to learn it cheaply.
5. **Check MATLAB starts cleanly.** [Guide](../working-remotely/matlab.md) — a
   healthy startup prints the OPR path, your personal path, and sets `gRadar`.
6. **Look at a data file.** [What the data look like](../reference/data-files.md)
   — load one echogram and plot it. This is the point where the whole thing
   starts feeling real.
7. **Set up your editor.** [VS Code Remote-SSH](vscode-remote-ssh.md).
8. **Optionally, install an assistant.**
   [Claude Code](../working-remotely/claude-code.md) in your home directory.

Then do the [OPR Toolbox Setup](https://gitlab.com/openpolarradar/opr/-/wikis/OPR-Toolbox-Setup)
proper, which covers git configuration, the `startup.m` profile, and the
parameter spreadsheets. These pages deliberately do not duplicate it.

New to the radar side of this? Read
[what CReSIS and IceBridge are](../background/history.md) first — it is fifteen
minutes and it explains why the data are shaped the way they are.

## Working across time zones

We are in Central Time with KU, which is easy. The wider OPR community is not,
and some of the same discipline pays off anyway:

- **Jobs fail while you are asleep.** Make batches idempotent and capped — see
  [running the cluster remotely](../working-remotely/cluster.md). A rerun that
  skips completed work turns an overnight failure into a five-second fix
  instead of a lost day.
- **OPR support works US Central hours.** Batch your questions; a
  well-described problem sent at the end of your day usually has an answer by
  the start of the next.

## Etiquette on a shared system

The login nodes are shared with everyone else on the project, and `umask 002`
means files you create are group-writable **by design** — that is how the group
shares data products.

- Cap threads in MATLAB (`maxNumCompThreads(8)`) and `nice` anything
  long-running on an interactive node.
- Do real processing through the [cluster](../working-remotely/cluster.md), not
  on the login node.
- You *can* overwrite other people's files. Pay attention to what you point
  scripts at, especially anything with `rm`.

See [storage and file paths](../working-remotely/storage-and-paths.md) for where
things live and what is safe to touch.
