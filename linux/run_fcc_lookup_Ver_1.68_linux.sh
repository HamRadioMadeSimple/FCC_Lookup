#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! python3 - <<'PY' >/dev/null 2>&1
import tkinter
PY
then
    echo "python3-tk is missing. On Linux Mint install it with: sudo apt install python3-tk"
    exit 1
fi

exec python3 "$SCRIPT_DIR/FCC_Lookup_Ver_1.68_linux.py"
