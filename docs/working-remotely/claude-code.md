# 4. Claude Code in your home directory

Running an AI coding assistant **on the server**, in your home directory, is
what makes remote work feel different. It can read your actual scripts, inspect
real data products, run MATLAB, submit cluster jobs, and read the errors that
come back. Running it on your laptop against a mounted filesystem gets you none
of that.

The install needs no root and lands entirely inside your home directory, so it
is fine on a shared HPC node.

This guide uses [Claude Code](https://code.claude.com/docs). The same shape
applies to other terminal assistants; the install path and login flow differ.

> **Check first:** Claude Code needs a Claude Pro, Max, Team, or Enterprise
> plan, or API credit on a Console account. The free plan does not include it.
> Sort that out before you start.
>
> **Also check** that the node has outbound HTTPS. The CReSIS nodes sit behind
> a gateway, and if outbound access is restricted the installer or the login
> will fail. If it does, ask `opr@openpolarradar.org` rather than working
> around it.

## Install without root

SSH into the server and run the native installer:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

This puts the launcher at `~/.local/bin/claude` and the versions themselves
under `~/.local/share/claude/`. Nothing is written outside your home directory,
and it keeps itself updated in the background.

## Put it on your PATH

The OPR setup already has you editing `~/.bashrc` to add MATLAB. Add
`~/.local/bin` in the same place:

```bash
# CReSIS MATLAB (from the OPR toolbox setup instructions)
export PATH=/opt/sw/matlab/2024b/bin/:$PATH

# Claude Code
export PATH="$HOME/.local/bin:$PATH"
```

Then reload and check:

```bash
source ~/.bashrc
claude --version      # e.g. 2.1.211 (Claude Code)
claude doctor         # read-only diagnostics if anything looks off
```

`claude doctor` prints install health and settings validation without starting
a session — it is the right first move whenever something is wrong.

## Log in from a headless server

Run `claude` and pick your login method. The server has no browser, so instead
of opening one it prints a URL. Copy that URL into the browser on your laptop,
complete the login there, and paste the code it gives you back into the
terminal. After that the session is stored and you will not be asked again.

If you would rather use an API key, set `ANTHROPIC_API_KEY` and Claude Code
prompts you once to approve it instead of opening a browser.

### Careful with API keys on a shared machine

The OPR `.bashrc` recommends `umask 002`, which makes new files
**group-writable** so everyone on the project can work with the same data. That
is exactly right for data products and exactly wrong for a credential.

If you use a key, keep it out of `.bashrc` and lock the file down explicitly:

```bash
printf 'export ANTHROPIC_API_KEY=%s\n' 'sk-...' > ~/.anthropic_key
chmod 600 ~/.anthropic_key
echo '[ -f ~/.anthropic_key ] && . ~/.anthropic_key' >> ~/.bashrc
```

Better still, use the browser login and skip the key entirely. And check the
permissions on `~/.claude` if you have ever run with a loose umask:

```bash
chmod -R go-rwx ~/.claude ~/.claude.json
```

## Make tmux behave

You will be running this inside tmux (see
[guide 2](../getting-started/ssh-and-tmux.md#tmux-dont-lose-a-job-to-a-dropped-connection)).
Two things break by default — Shift+Enter for a newline, and notifications
reaching your local terminal. In `~/.tmux.conf` on the server:

```bash
set -g allow-passthrough on
set -s extended-keys on
set -as terminal-features 'xterm*:extkeys'
```

Then `tmux source-file ~/.tmux.conf`.

Desktop notifications do travel back over SSH, so you can start a long task,
switch to something else, and be told when it wants your attention. Ghostty,
Kitty, and iTerm2 handle this natively. In other terminals, put this in
`~/.claude/settings.json` to ring the terminal bell instead:

```json
{
  "preferredNotifChannel": "terminal_bell"
}
```

## Give it the project context

The highest-leverage thing you can do is write a `CLAUDE.md` at the root of
your project. It is read automatically at the start of every session.

On the CReSIS servers, the things worth writing down are the ones that are
invisible from the code:

```markdown
# <project> — working context

## Operations
- Server: <node>. Work root /kucresis/scratch/<username>/<project>.
- MATLAB on the server is /opt/sw/matlab/2024b/bin/matlab.
  Cap it with maxNumCompThreads(8) and `nice` it — this node is shared.
- All long jobs run nohup-detached inside tmux; batches are idempotent
  so a retry skips frames that are already complete.
- Deploy edits atomically: `cat > file.new && mv file.new file`.
  Never truncate a script that a running job is reading.
- Coregistration caches are expensive to rebuild. Do not delete them.

## Conventions
- <the domain rules that are easy to get wrong>
```

That last section matters more than it looks. Radar processing is full of
conventions that are obvious to you and invisible to a fresh reader — sign
conventions, which angles are mod 180, when to abstain rather than report a
number, which intermediate products are safe to regenerate. Write them down
once and every future session inherits them.

The atomic-deploy rule is worth calling out specifically. On a shared
filesystem with jobs running, a naive editor that truncates and rewrites a file
can corrupt a script that a running MATLAB process is still reading.

## Working politely on a shared node

The login nodes are shared with everyone else on the project.

- **Cap your threads.** `maxNumCompThreads(8)` in MATLAB, and `nice` anything
  long-running. Put it in `CLAUDE.md` and it will happen by default.
- **Read the permission prompts.** Claude Code asks before running shell
  commands. On a shared filesystem holding other people's data, actually read
  them — especially anything with `rm`, and anything writing outside your own
  scratch directory. `umask 002` means you *can* overwrite a colleague's files.
- **Use the cluster for real work.** Interactive nodes are for editing and
  debugging. Processing belongs in Slurm through the toolbox's cluster
  interface.

## What works well, and what doesn't

**Works well:** reading and refactoring toolbox code, writing driver scripts,
interpreting MATLAB errors, batch-processing many frames, wiring up parameter
spreadsheets, and building small tools around the pipeline. The
[OPR cluster monitor](https://gitlab.com/openpolarradar/opr-cluster-monitor) is
a good example of the kind of tooling that is now cheap to build.

**Works badly:** anything that requires *looking* at a figure. The assistant
cannot see your echogram. Layer picking, judging whether a coherence gate is
sensible, deciding whether an inversion result is physically plausible — that
is still you, in `imb.picker`, in a ThinLinc session.

Keep that division honest. The failure mode is not that it writes bad code; it
is that it produces a confident number from a pipeline nobody looked at.
