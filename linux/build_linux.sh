#!/bin/bash
# FCC Lookup - make the Linux download.
#   bash linux/build_linux.sh   ->  output/FCC-Lookup-<version>-Linux.tar.gz
#
# The download holds a ready-made program (folder FCC_Lookup/) with its own Python and Tk inside,
# so people don't have to install python3-tk or anything else. GitHub builds it on Ubuntu 22.04:
# a program built on a Linux runs on that Linux and newer ones (Mint 21+, Ubuntu 22.04+, Debian 12+,
# Fedora 36+ ...). Building it on a newer Linux (e.g. Mint 22) makes it need that newer Linux.
#
# Needs: python3 with Tk (sudo apt install python3-tk python3-venv). PyInstaller is installed into a
# throwaway virtual environment under build/.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
cd "$HERE"

VERSION="$(sed -n 's/^APP_VERSION = "Ver \([0-9.]*\).*/\1/p' FCC_Lookup_Ver_1.65_linux.py)"
[ -n "$VERSION" ] || { echo "Could not read APP_VERSION from FCC_Lookup_Ver_1.65_linux.py"; exit 1; }
NAME="FCC-Lookup-${VERSION}-Linux"
BUILD="$ROOT/build/linux"
STAGE="$BUILD/$NAME"
OUT="$ROOT/output"
echo "=== Building ${NAME} ==="

python3 -c "import tkinter" 2>/dev/null || { echo "Tk for Python is missing: sudo apt install python3-tk"; exit 1; }

rm -rf "$BUILD"
mkdir -p "$BUILD" "$OUT"
python3 -m venv "$BUILD/venv"
"$BUILD/venv/bin/python" -m pip install --quiet --upgrade pip pyinstaller

"$BUILD/venv/bin/pyinstaller" --noconfirm --clean \
    --distpath "$BUILD/dist" --workpath "$BUILD/work" FCC_Lookup_linux.spec

mkdir -p "$STAGE"
cp -r "$BUILD/dist/FCC_Lookup" "$STAGE/FCC_Lookup"
cp update_linux.sh linux_uninstall.sh fcc_icon.png FC_launcher_icon.ico "$STAGE/"
cp README-Linux.txt "$STAGE/README.txt"
for pdf in FCC_Lookup_Linux_Install_Guide.pdf FCC_Lookup_User_Guide.pdf; do
    [ -f "$ROOT/docs/$pdf" ] && cp "$ROOT/docs/$pdf" "$STAGE/"
done
cp "$ROOT/LICENSE" "$STAGE/LICENSE.txt"

# .sh files must have Linux (LF) line endings - a Windows (CRLF) save gives confusing errors on Linux.
for f in "$STAGE"/*.sh; do
    if grep -q $'\r' "$f"; then
        echo "WARNING: $(basename "$f") had Windows line endings - fixed in the download (fix the project copy too)."
        sed -i 's/\r$//' "$f"
    fi
done
chmod +x "$STAGE"/*.sh "$STAGE/FCC_Lookup/FCC_Lookup"

# Newest C library the program needs (tells which Linux versions it runs on).
NEED="$(find "$STAGE/FCC_Lookup" -type f \( -name '*.so*' -o -name FCC_Lookup \) -exec objdump -T {} + 2>/dev/null \
        | grep -o 'GLIBC_[0-9.]*' | sort -Vu | tail -n 1)"
echo "Needs ${NEED:-unknown} or newer (Ubuntu 22.04 / Mint 21 have GLIBC_2.35)."

tar -C "$BUILD" -czf "$OUT/${NAME}.tar.gz" "$NAME"
echo ""
echo "Done:  output/${NAME}.tar.gz  ($(du -h "$OUT/${NAME}.tar.gz" | cut -f1))"
