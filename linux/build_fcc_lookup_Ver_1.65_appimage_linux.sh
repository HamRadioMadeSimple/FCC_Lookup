#!/usr/bin/env bash
set -euo pipefail

# Optional portable Linux AppImage builder.
# Run this on Linux Mint from the folder containing FCC_Lookup_Ver_1.65_linux.py and fcc_icon.png.

APP_SOURCE="FCC_Lookup_Ver_1.65_linux.py"
APP_NAME="FCC_Lookup"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -f "$APP_SOURCE" ]]; then
    echo "ERROR: $APP_SOURCE not found."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required."
    exit 1
fi

if ! python3 - <<'PY' >/dev/null 2>&1
import tkinter
PY
then
    echo "python3-tk is missing. Installing it with apt..."
    sudo apt-get update
    sudo apt-get install -y python3-tk python3-venv
fi

if ! command -v wget >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y wget
fi

python3 -m venv .fcc_lookup_build_venv
source .fcc_lookup_build_venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pyinstaller

rm -rf build dist AppDir FCC_Lookup.spec
pyinstaller --noconfirm --clean --windowed --onefile \
    --name "$APP_NAME" \
    --add-data "fcc_icon.png:." \
    "$APP_SOURCE"

mkdir -p AppDir/usr/bin AppDir/usr/share/applications AppDir/usr/share/icons/hicolor/256x256/apps
cp "dist/$APP_NAME" "AppDir/usr/bin/$APP_NAME"
chmod +x "AppDir/usr/bin/$APP_NAME"

if [[ -f fcc_icon.png ]]; then
    cp fcc_icon.png "AppDir/usr/share/icons/hicolor/256x256/apps/fcc-lookup.png"
    cp fcc_icon.png "AppDir/fcc-lookup.png"
fi

cat > AppDir/AppRun <<'EOF'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "$HERE/usr/bin/FCC_Lookup" "$@"
EOF
chmod +x AppDir/AppRun

cat > AppDir/fcc-lookup.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=FCC Lookup
Comment=Offline FCC and Canada ham callsign lookup
Exec=FCC_Lookup
Icon=fcc-lookup
Terminal=false
Categories=Utility;
EOF
cp AppDir/fcc-lookup.desktop AppDir/usr/share/applications/fcc-lookup.desktop

APPIMAGETOOL="./appimagetool-x86_64.AppImage"
if [[ ! -x "$APPIMAGETOOL" ]]; then
    echo "Downloading appimagetool..."
    wget -O "$APPIMAGETOOL" "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

ARCH=x86_64 "$APPIMAGETOOL" AppDir "FCC_Lookup-Ver_1.65-linux-x86_64.AppImage"
echo "Built: $SCRIPT_DIR/FCC_Lookup-Ver_1.65-linux-x86_64.AppImage"
