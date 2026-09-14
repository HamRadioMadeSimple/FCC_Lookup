#!/usr/bin/env bash
set -euo pipefail

APP_TITLE="FCC Lookup"
APP_ID="fcc-lookup"
APP_SOURCE="FCC_Lookup_Ver_1.65_linux.py"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/share/fcc-lookup"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/FCC_Lookup"
DB_DIR="$HOME/FCC_DB"
RUNNER="$BIN_DIR/fcc-lookup"
DESKTOP_FILE="$DESKTOP_DIR/fcc-lookup.desktop"
USER_DESKTOP_DIR="${XDG_DESKTOP_DIR:-$HOME/Desktop}"
USER_DESKTOP_FILE="$USER_DESKTOP_DIR/FCC Lookup.desktop"

cd "$SCRIPT_DIR"

echo "=== FCC Lookup Ver 1.65 Linux Mint setup ==="

if [[ ! -f "$APP_SOURCE" ]]; then
    echo "ERROR: $APP_SOURCE was not found in: $SCRIPT_DIR"
    echo "Put this setup script in the same folder as $APP_SOURCE and fcc_icon.png, then run it again."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is not installed. On Linux Mint run: sudo apt install python3"
    exit 1
fi

# Tkinter is the only required GUI dependency. It is sometimes not installed by default.
if ! python3 - <<'PY' >/dev/null 2>&1
import tkinter
PY
then
    echo "python3-tk is missing. Installing it with apt..."
    sudo apt-get update
    sudo apt-get install -y python3-tk
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$DESKTOP_DIR" "$CONFIG_DIR" "$DB_DIR"

cp "$APP_SOURCE" "$INSTALL_DIR/FCC_Lookup.py"
chmod +x "$INSTALL_DIR/FCC_Lookup.py"

if [[ -f "fcc_icon.png" ]]; then
    cp "fcc_icon.png" "$INSTALL_DIR/fcc_icon.png"
fi
if [[ -f "FC_launcher_icon.ico" ]]; then
    cp "FC_launcher_icon.ico" "$INSTALL_DIR/FC_launcher_icon.ico"
fi

# Save the default database folder. The app also lets you change this from Database > Select DB Folder.
printf '%s' "$DB_DIR" > "$CONFIG_DIR/fcc_lookup.cfg"

# If a ham.db is sitting beside the installer files, copy it into ~/FCC_DB for this Linux install.
# Existing database files are not overwritten.
copy_db_file() {
    local src="$1"
    local dst="$DB_DIR/$(basename "$src")"
    if [[ -f "$src" && ! -f "$dst" ]]; then
        echo "Copying $(basename "$src") to $DB_DIR ..."
        cp "$src" "$dst"
    fi
}
copy_db_file "$SCRIPT_DIR/ham.db"
copy_db_file "$SCRIPT_DIR/FCC_DB/ham.db"
copy_db_file "$SCRIPT_DIR/AM.dat"
copy_db_file "$SCRIPT_DIR/EN.dat"
copy_db_file "$SCRIPT_DIR/amateur_delim.txt"
copy_db_file "$SCRIPT_DIR/FCC_DB/AM.dat"
copy_db_file "$SCRIPT_DIR/FCC_DB/EN.dat"
copy_db_file "$SCRIPT_DIR/FCC_DB/amateur_delim.txt"
copy_db_file "$SCRIPT_DIR/zip_latlon.csv"
copy_db_file "$SCRIPT_DIR/FCC_DB/zip_latlon.csv"

cat > "$RUNNER" <<EOF
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/FCC_Lookup.py" "\$@"
EOF
chmod +x "$RUNNER"

ICON_PATH="$INSTALL_DIR/fcc_icon.png"
if [[ ! -f "$ICON_PATH" ]]; then
    ICON_PATH="applications-utilities"
fi

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=FCC Lookup
Comment=Offline FCC and Canada ham callsign lookup
Exec=$RUNNER
Icon=$ICON_PATH
Terminal=false
Categories=Utility;
StartupNotify=true
EOF
chmod +x "$DESKTOP_FILE"

# Also create a normal desktop launcher with the same icon. Linux Mint may
# still ask the user to trust/allow the launcher the first time it is clicked.
mkdir -p "$USER_DESKTOP_DIR"
cp "$DESKTOP_FILE" "$USER_DESKTOP_FILE"
chmod +x "$USER_DESKTOP_FILE"
if command -v gio >/dev/null 2>&1; then
    gio set "$USER_DESKTOP_FILE" metadata::trusted true >/dev/null 2>&1 || true
fi

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi

echo
echo "Installed FCC Lookup."
echo "App files:        $INSTALL_DIR"
echo "Database dir:     $DB_DIR"
echo "Config file:      $CONFIG_DIR/fcc_lookup.cfg"
echo "Menu launcher:    $DESKTOP_FILE"
echo "Desktop launcher: $USER_DESKTOP_FILE"
echo
echo "Run it with:      fcc-lookup"
echo "or open it from the Linux Mint menu / desktop icon as: FCC Lookup"
echo
echo "If the menu entry does not show immediately, log out/in or run: cinnamon --replace"
