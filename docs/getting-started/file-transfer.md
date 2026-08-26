# Moving data in and out

Remote work means bandwidth is a real constraint. A quad-pol frame is about
400 MB; a season is not something you casually copy. The general rule is
**move computation to the data, not data to the computation** — and when you do
move something, move the smallest useful thing.

## Public data: just download it

Many processed products are public and need no credentials at all:

```
https://data.cresis.ku.edu/data/<radar>/<SEASON>/CSARP_<product>/<day_seg>/Data_<day_seg>_<frm>.mat
```

```bash
curl -sS --fail -O -C - \
  "https://data.cresis.ku.edu/data/accum/2024_Antarctica_Ground2/CSARP_standard_HH/20250108_02/Data_20250108_02_009.mat"
```

`-C -` resumes an interrupted download rather than starting over, which matters
at 100 MB a file on a bad connection.

For pulling a whole quad-pol frame in the server's directory layout, see
[`fetch_frame.sh`](../doing-science/prototyping-loop.md#get-a-frame).

## rsync: the default for everything else

Once you have [SSH keys and a `cresis` host alias](ssh-and-tmux.md#a-reusable-ssh-config):

```bash
# up
rsync -avz --progress ./local_dir/ cresis:/kucresis/scratch/<username>/dest/

# down
rsync -avz --progress cresis:/kucresis/scratch/<username>/figs/ ./figs/
```

Useful flags:

| Flag | Why |
|---|---|
| `-z` | Compress in transit. Big win on `.mat` and text, little on already-compressed data. |
| `--progress` | You will want it on anything over a few hundred MB. |
| `--partial` | Keep partial transfers so an interrupted run resumes. |
| `--dry-run` | Always, the first time you write a `--delete` command. |
| `--include`/`--exclude` | Pull only what you need — see below. |

!!! danger "`--delete` deletes"
    `rsync --delete` makes the destination match the source, removing anything
    else. On a shared filesystem with `umask 002` you have permission to delete
    other people's files. Run it with `--dry-run` first, every time.

### Pull only the small things

The usual mistake is syncing a product tree to look at figures. Don't:

```bash
# figures only, preserving directory structure
rsync -avz --include='*/' --include='*.png' --exclude='*' \
  cresis:/kucresis/scratch/<username>/proj/ ./review/
```

Reviewing a hundred frames as PNGs pulled down in one go is far faster than
paging through them over a remote display. See
[MATLAB from a distance](../working-remotely/matlab.md#plots) for writing
figures headlessly.

## scp, for one file

```bash
scp cresis:/kucresis/scratch/<username>/figs/frame_009.png .
```

Fine for a single file. For anything bigger or repeated, use `rsync` — it
resumes, and it will not re-copy what is already there.

## FileZilla

A GUI client, and what the OPR setup instructions recommend for people who
would rather not use the command line. It works on Windows, macOS and Linux.

Point it at your login node — host `lps3.cresis.ku.edu`, your username and
password. Use **SFTP**, not FTP.

## Big transfers

- **Run them in [`tmux`](ssh-and-tmux.md#tmux-dont-lose-a-job-to-a-dropped-connection)**
  on the server side if the server is initiating, so a dropped connection does
  not kill the copy.
- **`rsync` is restartable.** Re-running the same command after an interruption
  picks up where it left off. Prefer it to `scp` for anything large.
- **Check free space first**, especially before staging inputs. `ct_save` checks
  before writing `.mat` files, but `rsync` will happily fill a filesystem.
- **Ask before staging something very large.** Quotas change; check with
  `opr@openpolarradar.org`.

## Keeping code in sync

Do not `rsync` your source tree. Use git:

```bash
# on the server, with ForwardAgent yes in your SSH config
git pull
```

`ForwardAgent yes` means your local SSH key authenticates the pull, so you never
copy a private key onto a shared machine. See
[storage and file paths](../working-remotely/storage-and-paths.md#deploy-edits-atomically)
for deploying single-file edits atomically while jobs are running.
