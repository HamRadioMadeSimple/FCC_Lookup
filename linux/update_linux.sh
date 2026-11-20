#!/usr/bin/env bash
# FCC Lookup 1.68 - install or update into ~/Applications/FCC-Lookup
# Run it with:  bash update_linux.sh   (the install block in the guide does this for you)
# Safe to run again: an update replaces the program and keeps your database and settings.

set -u

VERSION="1.68"
SRC_PY="FCC_Lookup_Ver_1.68_linux.py"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$HOME/Applications/FCC-Lookup"
OLD_DIR="$HOME/.local/share/fcc-lookup"          # where the earlier setup script installed it
BIN_DIR="$HOME/.local/bin"
MENU_DIR="$HOME/.local/share/applications"
CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/FCC_Lookup"
DB_DIR="$HOME/FCC_DB"
LAUNCHER="$BIN_DIR/fcc-lookup"
MENU_FILE="$MENU_DIR/fcc-lookup.desktop"

DESK_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || true)"
if [ -z "$DESK_DIR" ] || [ "$DESK_DIR" = "$HOME" ]; then DESK_DIR="$HOME/Desktop"; fi
DESK_FILE="$DESK_DIR/FCC Lookup.desktop"

die() { echo; echo "ERROR: $*" >&2; exit 1; }

ask_yes() {   # $1 = prompt, $2 = default (Y or N). Returns 0 for yes.
    local ans=""
    read -r -p "$1" ans || ans=""
    ans="${ans:-$2}"
    case "$ans" in [Yy]*) return 0 ;; *) return 1 ;; esac
}

tk_ok() { python3 -c "import tkinter" >/dev/null 2>&1; }

echo "=== FCC Lookup $VERSION: install / update ==="
echo

# The download from the Releases page carries a ready-made program (folder FCC_Lookup/) with its own
# Python and Tk inside, so nothing else has to be installed. Run from the source code instead (no
# FCC_Lookup/ folder next to this script), it installs the .py file and needs Python 3 with Tk.
if [ -x "$HERE/FCC_Lookup/FCC_Lookup" ]; then
    MODE="bundle"
else
    MODE="python"
    [ -f "$HERE/$SRC_PY" ] || die "Neither the FCC_Lookup program folder nor $SRC_PY was found next to this script ($HERE)."
    command -v python3 >/dev/null 2>&1 || die "python3 is not installed. On Linux Mint run: sudo apt install python3"
fi

# ---- 1. Tk for Python (the window toolkit; only when running from source) --
if [ "$MODE" = "python" ] && ! tk_ok; then
    echo "These packages are needed: python3-tk"
    if ask_yes "Install them now? [Y/n] " Y; then
        if   command -v apt-get >/dev/null 2>&1; then sudo apt-get update && sudo apt-get install -y python3-tk
        elif command -v dnf     >/dev/null 2>&1; then sudo dnf install -y python3-tkinter
        elif command -v pacman  >/dev/null 2>&1; then sudo pacman -S --noconfirm tk
        elif command -v zypper  >/dev/null 2>&1; then sudo zypper install -y python3-tk
        else echo "No known package manager found. Install the Tk package for Python 3 by hand."
        fi
    fi
    if ! tk_ok; then
        die "Tk for Python (tkinter) is still missing. Run: sudo apt install python3-tk   then paste the install block again."
    fi
    echo
fi

# ---- 2. Program files ------------------------------------------------------
mkdir -p "$APP_DIR" || die "Could not create $APP_DIR"
if [ "$MODE" = "bundle" ]; then
    rm -rf "$APP_DIR/FCC_Lookup" "$APP_DIR/FCC_Lookup.py"
    cp -r "$HERE/FCC_Lookup" "$APP_DIR/FCC_Lookup"      || die "Could not copy the program."
    chmod +x "$APP_DIR/FCC_Lookup/FCC_Lookup"
    RUN_CMD="\"$APP_DIR/FCC_Lookup/FCC_Lookup\""
else
    rm -rf "$APP_DIR/FCC_Lookup"
    cp "$HERE/$SRC_PY" "$APP_DIR/FCC_Lookup.py"        || die "Could not copy the program."
    chmod +x "$APP_DIR/FCC_Lookup.py"
    RUN_CMD="python3 \"$APP_DIR/FCC_Lookup.py\""
fi
[ -f "$HERE/fcc_icon.png" ]         && cp "$HERE/fcc_icon.png"         "$APP_DIR/fcc_icon.png"
[ -f "$HERE/FC_launcher_icon.ico" ] && cp "$HERE/FC_launcher_icon.ico" "$APP_DIR/FC_launcher_icon.ico"
cp "$HERE"/*.pdf "$APP_DIR/" 2>/dev/null
cp "$HERE/linux_uninstall.sh" "$APP_DIR/linux_uninstall.sh" 2>/dev/null
printf '%s\n' "$VERSION" > "$APP_DIR/VERSION"
chmod +x "$APP_DIR/linux_uninstall.sh" 2>/dev/null
echo "Program installed in $APP_DIR"

# Earlier copy made by the old setup script: its program files are replaced by the ones above.
if [ -f "$OLD_DIR/FCC_Lookup.py" ]; then
    rm -rf "$OLD_DIR"
    echo "Moved the earlier copy from $OLD_DIR"
fi

# ---- 3. Terminal command ---------------------------------------------------
mkdir -p "$BIN_DIR"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
exec $RUN_CMD "\$@"
EOF
chmod +x "$LAUNCHER"

# ---- 4. Database folder and settings (never touched by an update) ----------
mkdir -p "$DB_DIR" "$CONF_DIR"
if [ ! -f "$CONF_DIR/fcc_lookup.cfg" ]; then
    printf '%s' "$DB_DIR" > "$CONF_DIR/fcc_lookup.cfg"
fi

# ---- 5. Menu and desktop icons --------------------------------------------
mkdir -p "$MENU_DIR" "$DESK_DIR"
ICON="$APP_DIR/fcc_icon.png"
[ -f "$ICON" ] || ICON="applications-utilities"
cat > "$MENU_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=FCC Lookup
Comment=Offline FCC and Canada ham callsign lookup
Exec="$LAUNCHER"
Icon=$ICON
Terminal=false
Categories=Utility;
StartupNotify=true
EOF
chmod +x "$MENU_FILE"
cp "$MENU_FILE" "$DESK_FILE" && chmod +x "$DESK_FILE"
if command -v gio >/dev/null 2>&1; then
    gio set "$DESK_FILE" metadata::trusted true >/dev/null 2>&1 || true
fi
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$MENU_DIR" >/dev/null 2>&1 || true
fi

echo
echo "Done. FCC Lookup $VERSION is installed."
echo "  Program:   $APP_DIR"
echo "  Database:  $DB_DIR"
echo "  Settings:  $CONF_DIR"
echo "  Icons:     the menu (Accessories) and the desktop"
echo "  Terminal:  fcc-lookup"
echo
echo "You can delete the unpacked folder in Downloads: $HERE"
echo

if ask_yes "Open FCC Lookup now? [Y/n] " Y; then
    if command -v setsid >/dev/null 2>&1; then
        setsid "$LAUNCHER" >/dev/null 2>&1 < /dev/null &
    else
        nohup "$LAUNCHER" >/dev/null 2>&1 < /dev/null &
    fi
fi
exit 0
