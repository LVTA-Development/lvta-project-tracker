#!/usr/bin/env bash
# Encrypts src/index.html into docs/index.html with StaticCrypt (AES-256).
# The password is never stored in the repo: pass it in TRACKER_PASSWORD, or
# keep it in .password (gitignored). The salt in .staticrypt.json is not
# secret; keeping it means "remember me" survives re-publishing.
set -euo pipefail
cd "$(dirname "$0")"
PW="${TRACKER_PASSWORD:-$(cat .password 2>/dev/null || true)}"
[ -n "$PW" ] || { echo "Set TRACKER_PASSWORD or create .password" >&2; exit 1; }
mkdir -p docs
npx staticrypt src/index.html -d docs --short -p "$PW" \
  --remember 30 \
  --template-title "LVTA Website: Project Tracker" \
  --template-instructions "This tracker is private to the LVTA team. Enter the password you were sent." \
  --template-button "Open tracker" \
  --template-placeholder "Password" \
  --template-remember "Remember me on this device for 30 days" \
  --template-color-primary "#1c2f6e" \
  --template-color-secondary "#f7f6f2"
touch docs/.nojekyll
echo "docs/index.html encrypted"
