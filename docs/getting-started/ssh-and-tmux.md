# SSH and tmux

Once ThinLinc is working, most of your actual time will be spent over plain
SSH. This guide sets up a login you can type in three characters, and the one
habit that will save you the most grief: never running a long job outside
`tmux`.

## Logging in

```bash
ssh <username>@lps3.cresis.ku.edu
```

The first time you connect you will be asked to accept the host key — type
`yes`.

## A reusable SSH config

Typing the full hostname every time gets old fast. Put this in `~/.ssh/config`
on your laptop (`C:\Users\<you>\.ssh\config` on Windows):

```
Host cresis
  HostName lps3.cresis.ku.edu
  User <username>
  ForwardX11 yes
  ForwardAgent yes
```

Now `ssh cresis` is the whole command, and `rsync`, `scp` and VS Code all
understand the same alias.

Keeping a single `Host cresis` entry and swapping the `HostName` when you need
a different login node means VS Code and your scripts never need to know or
care which node you are on.

### X11 forwarding

`ForwardX11 yes` lets MATLAB plot windows pop up on your laptop. It works out
of the box on Linux, and needs [XQuartz](https://www.xquartz.org/) on macOS or
an X server such as [VcXsrv](https://vcxsrv.com/) on Windows.

It is genuinely useful for a quick `imagesc`. It is also uncompressed, so it is
slow for anything interactive — keep a ThinLinc session open for `imb.picker`
rather than trying to run it over X11.

The OPR `.bashrc` recommendations include `alias ssh="ssh -Y"` for this reason.

## Set up key-based authentication

Worth five minutes, and close to mandatory before you start using VS Code,
which will otherwise ask for your password repeatedly.

```bash
ssh-keygen -t ed25519            # if you don't already have a key
ssh-copy-id cresis               # uses the Host alias you just defined
```

On Windows PowerShell, if `ssh-copy-id` is unavailable:

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh cresis "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

With `ForwardAgent yes` in your config, your local key is also available on the
server, so you can `git push` from the CReSIS side without copying a private
key onto a shared machine. Never copy a private key to a shared server.

## tmux: don't lose a job to a dropped connection

This is the single most useful habit on a remote machine. `tmux` keeps your
shell — and everything running in it — alive on the server after you
disconnect.

```bash
tmux new -s fabric      # start a named session
# ... launch matlab -nodisplay, start a long processing run ...
# Ctrl-b then d         detach, leaving it running
tmux attach -t fabric   # come back to it later, from anywhere
tmux ls                 # list your sessions
```

Close your laptop, get on a plane, reconnect from a different machine — the job
is still running. Without tmux, a dropped VPN kills whatever you had going.

The usual pattern is: debug interactively in VS Code, then start the long run
inside tmux with

```bash
matlab -nodisplay
```

For jobs that should outlive even the tmux server, `nohup`-detach them and
write the batch so it is idempotent — a rerun then skips everything already
complete instead of starting over.

### tmux config

If you are going to run Claude Code inside tmux (see
[guide 4](../working-remotely/claude-code.md)), add this to `~/.tmux.conf` on the
server now:

```bash
set -g allow-passthrough on
set -s extended-keys on
set -as terminal-features 'xterm*:extkeys'
```

Then `tmux source-file ~/.tmux.conf`. Without it, Shift+Enter and notifications
do not work properly through tmux.

## Your `.bashrc`

The OPR setup instructions have you add MATLAB to your path. The KU CReSIS
lines are:

```bash
export PATH=/opt/sw/matlab/2024b/bin/:$PATH

# Recommended everywhere:
umask 002          # so others in the group can work with files you create

alias cp="cp -i"
alias rm="rm -i"
alias mv="mv -i"
alias ssh="ssh -Y"
```

Re-run it with `source ~/.bashrc` after editing, or log out and back in.

At KU your Linux home directory is also mounted as `H:` on Windows, so you can
edit `.bashrc` from Windows as `H:\.bashrc` if you prefer a graphical editor.
Notepad++ is the recommendation there — plain Notepad will not save files with
long extensions like `.gitconfig`.

> Note `umask 002`: it makes new files group-writable so everyone on the
> project can work with the same data products. That is what you want for data
> and *not* what you want for credentials. See
> [guide 4](../working-remotely/claude-code.md#careful-with-api-keys-on-a-shared-machine).

## File transfer

Once you have keys and a `cresis` host alias, `rsync` over that alias is the
default for everything:

```bash
rsync -avz --progress ./local_dir/ cresis:/kucresis/scratch/<username>/dest/
```

See [moving data in and out](file-transfer.md) for the full picture — pulling
only figures, working through the tunnel, FileZilla, and the `--delete` footgun.
