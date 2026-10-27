#!/usr/bin/env bash
set -euo pipefail
if ! command -v startxfce4 >/dev/null; then echo 'Install XFCE on Linux first.' >&2; exit 1; fi
exec startxfce4
