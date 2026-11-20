#!/usr/bin/env bash
# Remove FCC Lookup. It removes the program and its menu and desktop icons,
# then asks whether to delete your database and settings (Enter alone keeps them).
# The whole script sits inside braces so it is read in full before it deletes its own folder.
{
set -u
if [ -z "${HOME:-}" ]; then echo "ERROR: HOME is not set." >&2; exit 1; fi

APP_DIR="$HOME/Applications/FCC-Lookup"
OLD_DIR="$HOME/.local/share/fcc-lookup"
LAUNCHER="$HOME/.local/bin/fcc-lookup"
MENU_FILE="$HOME/.local/share/applications/fcc-lookup.desktop"
CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/FCC_Lookup"
DB_DIR="$HOME/FCC_DB"

DESK_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || true)"
if [ -z "$DESK_DIR" ] || [ "$DESK_DIR" = "$HOME" ]; then DESK_DIR="$HOME/Desktop"; fi
DESK_FILE="$DESK_DIR/FCC Lookup.desktop"

echo "=== Remove FCC Lookup ==="
echo "This removes:"
echo "  $APP_DIR"
echo "  $LAUNCHER"
echo "  $MENU_FILE"
echo "  $DESK_FILE"
echo

rm -rf "$APP_DIR"
[ -f "$OLD_DIR/FCC_Lookup.py" ] && rm -rf "$OLD_DIR"
rm -f "$LAUNCHER" "$MENU_FILE" "$DESK_FILE"
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi
echo "The program and its icons are removed."
echo

echo "Your database and settings are kept in:"
echo "  $DB_DIR"
echo "  $CONF_DIR"
ans=""
read -r -p "Delete them too? [y/N] " ans || ans=""
case "$ans" in
    [Yy]*)
        rm -rf "$DB_DIR" "$CONF_DIR"
        echo "Database and settings deleted."
        ;;
    *)
        echo "Database and settings kept."
        ;;
esac
echo
echo "FCC Lookup has been removed."
exit 0
}
