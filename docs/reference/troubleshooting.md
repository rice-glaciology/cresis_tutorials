# Troubleshooting

Every failure mode from these guides in one place. Symptoms are grouped by
where you hit them.

## Connecting

| Symptom | Fix |
|---|---|
| Asked to accept a host key | Expected on first connect. Type `yes`. |
| Password prompt every single time | Set up [key-based authentication](../getting-started/ssh-and-tmux.md#set-up-key-based-authentication). |
| `Permission denied (publickey,password)` | Wrong username, or your key was never copied up. Try `ssh -v cresis` to see which methods were offered. |
| Connection hangs with no prompt | You are probably off the network the node accepts, or the node is down. Check with `opr@openpolarradar.org`. |

## ThinLinc

| Symptom | Fix |
|---|---|
| Connects, then hangs during startup | Usually a stale/corrupt session that must be killed over SSH. Email `opr@openpolarradar.org`. |
| Segmentation fault on macOS | Reported by at least one user. Windows Remote Desktop ("Windows App" in the App Store) is the documented fallback. |
| Ctrl-Alt-T does nothing on a Mac | Use **Control + right-Command + T**. Left Command maps to Alt, right Command to Super. |
| Cannot find ThinLinc's own menu | **F8**, or **Fn-F8** on a Mac. |
| Session lost when you close the window | Use F8 → Disconnect instead of logging out; the session keeps running. |

## Remote Desktop (fallback only)

| Symptom | Fix |
|---|---|
| `protocol error detected at the client (code 0x1104)` | No known fix. Use ThinLinc instead. |
| Asked for credentials twice | Expected. |

## MATLAB

| Symptom | Fix |
|---|---|
| "MathWorks License Update" dialog | Close the window. Do **not** choose Update. |
| `matlab: command not found` | `/opt/sw/matlab/2024b/bin/` is not on your `PATH`. Add it in `~/.bashrc`, then `source ~/.bashrc`. |
| Startup script errors on login | Check the paths it prints — it should add the OPR path and your personal path, then set `gRadar`. |
| Long run dies when your connection drops | Run it inside `tmux`, and use `matlab -nodisplay`. |
| Plot windows are unusably slow | X11 has no compression. Use a ThinLinc session for GUI work. |
| Toolbox function missing | Check which MATLAB toolboxes that code path needs — Signal Processing, Mapping, and Image Processing cover most cases. |

## VS Code

| Symptom | Fix |
|---|---|
| Asks for your password constantly | Set up key-based authentication. |
| MATLAB session dies when you disconnect | Expected — the extension manages one session tied to the connection. Long runs belong in `tmux`. |
| Connects to the wrong node | Change `HostName` under your `Host cresis` entry in `~/.ssh/config` and reconnect. |

## Claude Code

| Symptom | Fix |
|---|---|
| `claude: command not found` after install | `~/.local/bin` is not on your `PATH`. Add it in `~/.bashrc`, then `source ~/.bashrc`. |
| Installer fails to download | Check the node has outbound HTTPS. Ask `opr@openpolarradar.org` rather than working around it. |
| Login cannot open a browser | Expected on a headless server. Copy the printed URL into your laptop's browser and paste the code back. |
| Anything else odd | `claude doctor` — read-only install and settings diagnostics. |
| Shift+Enter submits instead of inserting a newline in tmux | Add the `extended-keys` lines to `~/.tmux.conf`, then `tmux source-file ~/.tmux.conf`. Ctrl+J always works. |
| No notification when a task finishes | Add `allow-passthrough` to `~/.tmux.conf`, or set `"preferredNotifChannel": "terminal_bell"` in `~/.claude/settings.json`. |
| Worried a credential is group-readable | `umask 002` makes new files group-writable. `chmod 600` any key file and `chmod -R go-rwx ~/.claude ~/.claude.json`. |

## File transfer

| Symptom | Fix |
|---|---|
| FileZilla will not connect | Use **SFTP** (not FTP), host `lps3.cresis.ku.edu`, your account username and password. |
| Large transfer interrupted | `rsync` resumes; `curl -C -` resumes a single file. |
| Permission denied writing to a shared directory | Check `umask 002` is set — group-writable is the convention on these systems. |

## Getting help

- **OPR support** — `opr@openpolarradar.org`
- **Accounts** — `paden@ku.edu`
- **OPR wiki** — <https://gitlab.com/openpolarradar/opr/-/wikis/home>
