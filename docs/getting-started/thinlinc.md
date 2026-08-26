# ThinLinc: the graphical desktop

ThinLinc gives you a full Linux desktop in a window on your own machine. It is
the right tool for `imb.picker`, the
[slice browser](../doing-science/swath-cross-track-picking.md), and anything
else where you need to see and click on echograms.

It compresses graphics properly, which X11 forwarding over SSH does not, so
layer picking is actually responsive rather than a slideshow.

> Replace `<username>` with your account name and `<node>` with your login node
> (e.g. `lps3.cresis.ku.edu`).

## Install the client

Download from [cendio.com/thinlinc/download](https://www.cendio.com/thinlinc/download/).

- **Windows** — run the downloaded `.exe`.
- **macOS** — double-click the `.iso` to mount it, then drag the contents of the
  mounted volume into your Applications folder.
- **Linux** — install the `.deb` or `.rpm` with your package manager, e.g.
  `sudo apt install FILE.deb` or `sudo yum install FILE.rpm`.

## Connect

Launch the ThinLinc client and enter:

| Field | Value |
|---|---|
| Server | `<node>` — e.g. `lps3.cresis.ku.edu` |
| Username | `<username>` |
| Password | your account password |

Click **Connect**.

The first time you log in you will be walked through the GNOME desktop
first-run wizard — choose **Skip** or **Done** in the top right and accept all
the defaults.

That is the whole setup. If you have used the OPR workshop instructions before
and remember an SSH tunnel and a `HOST_ALIASES` file, none of that applies
here: that is only needed for temporary workshop accounts on the field nodes,
which is not how our accounts work. It is documented on the
[OPR workshop page](https://gitlab.com/openpolarradar/opr/-/wikis/workshop/2025#thinlinc-setup)
if you ever need it.

## Keyboard mapping

This trips up Mac users constantly, because the Linux desktop inside ThinLinc
expects keys your Mac does not have:

| You press (Mac) | Linux receives |
|---|---|
| right Command | Super |
| Control | Control |
| left Command | Alt |

On Windows and Linux the mapping is the obvious one: the Start-menu key is
Super, Control is Control, Alt is Alt.

So on a Mac the standard "open a terminal" shortcut is
**Control + right-Command + T**, not Control-Alt-T.

The same mapping applies inside `imb.picker` and the slice browser, both of
which lean heavily on modifier keys. Keyboard shortcuts are configurable in the
Linux window manager, in MATLAB, and in the terminal program, and opening those
settings is a good way to learn what the shortcuts actually are.

## The command menu

Press **F8** inside a ThinLinc session — **Fn-F8** on a Mac — for ThinLinc's
own menu. From there you can:

- Set full-screen behaviour under **Options…**
- **Disconnect** from the session, which leaves everything running on the
  server so you can reconnect later exactly where you left off
- Minimise the window

**Disconnect rather than log out.** A MATLAB session with a loaded echogram
will still be there tomorrow, on whatever machine you reconnect from. This is
the single most useful thing about ThinLinc.

### Full screen by default

Create `$HOME/thinlinc/client.conf` on your **local** machine with:

```
FULL_SCREEN_MODE=1
FULL_SCREEN_MONITOR_MODE=current
```

then launch the client with `-C "$HOME/thinlinc/client.conf"`. The file
accepts any ThinLinc client configuration parameter, so it is also where other
client defaults go.

## Starting MATLAB

Open a terminal inside the session (Control-Alt-T on Windows/Linux,
Control + right-Command + T on a Mac) and run:

```bash
matlab
```

A healthy startup prints:

```
Startup Script Running: /local_home/<username>/startup
  Resetting path
  Adding cresis path: /local_home/<username>/scripts/opr/matlab
  Adding personal path: /local_home/<username>/scripts/run_opr
  Setting global preferences in global variable gRadar
```

If a **"MathWorks License Update"** dialog appears, close the window — do not
choose "Update".

See the OPR wiki for the
[recommended MATLAB keyboard shortcuts and preferences](https://gitlab.com/openpolarradar/opr/-/wikis/OPR-Toolbox-Setup#setup---matlab-keyboard-shortcuts-and-preferences).

## If ThinLinc misbehaves

- **Hangs during startup** — usually a corrupt leftover session, which has to be
  killed over SSH. Email `opr@openpolarradar.org` for help.
- **Segmentation fault on macOS** — reported by at least one user. Windows
  Remote Desktop is a documented fallback; on macOS the client is the "Windows
  App" in the App Store (formerly "Microsoft Remote Desktop"). Note that Remote
  Desktop has its own known failure, `protocol error detected at the client
  (code 0x1104)`, with no known fix — in which case ThinLinc is the
  recommendation.

Remote Desktop also has a different Mac key mapping from ThinLinc: both Command
keys and Control all act as Linux Control, and Option/Alt acts as Alt.
