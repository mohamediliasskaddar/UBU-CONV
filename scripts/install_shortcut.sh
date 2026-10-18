#!/usr/bin/env bash
set -euo pipefail

CMD="${1:-$(cd "$(dirname "$0")/.." && pwd)/.venv/bin/fileconv-menu}"
BINDING="${2:-<Super><Shift>c}"

KEY=org.gnome.settings-daemon.plugins.media-keys
NEW_PATH=/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/fileconv/

current=$(gsettings get "$KEY" custom-keybindings)
if [[ "$current" != *"$NEW_PATH"* ]]; then
  if [[ "$current" == "@as []" || "$current" == "[]" ]]; then
    new="['$NEW_PATH']"
  else
    new="${current%]}, '$NEW_PATH']"
  fi
  gsettings set "$KEY" custom-keybindings "$new"
fi

SCHEMA="$KEY.custom-keybinding:$NEW_PATH"
gsettings set "$SCHEMA" name "fileconv menu"
gsettings set "$SCHEMA" command "$CMD"
gsettings set "$SCHEMA" binding "$BINDING"

echo "Shortcut set: $BINDING -> $CMD"