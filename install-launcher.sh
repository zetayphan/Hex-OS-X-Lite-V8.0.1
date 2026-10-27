#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/hex-os-web.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=HEX OS X Web Desktop
Exec=xdg-open $ROOT/web/index.html
Terminal=false
Categories=Utility;
DESKTOP
echo 'HEX OS web launcher installed in Linux application menu.'
