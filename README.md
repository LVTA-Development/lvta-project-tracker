# LVTA Website: Project Tracker

A password-protected, living project tracker for the LVTA website: completed
work, decisions needed, scope against the Statement of Work, and a change map.
Published with GitHub Pages from `docs/`.

`docs/index.html` is encrypted with [StaticCrypt](https://github.com/robinmoisson/staticrypt)
(AES-256). The readable page and the password are never committed.

## Updating

1. Edit the data in `../report/data.py` (shared with the PDF report).
2. `npm run publish` (reads the password from `TRACKER_PASSWORD` or a local,
   gitignored `.password` file), then commit and push `docs/`.
