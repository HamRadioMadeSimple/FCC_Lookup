# FCC Lookup Ver 1.65 Linux Mint

Linux Mint release files for FCC Lookup Ver 1.65.

FCC Lookup is an offline ham radio callsign lookup tool for U.S. FCC amateur records and Canadian amateur records. It can share `ham.db` with JS8Map and includes Browse Records plus optional distance and bearing from a user-set Home callsign.

Created by KW3KW.

## Files

Place these files in the same folder on the Linux Mint PC:

```text
FCC_Lookup_Ver_1.65_linux.py
setup_fcc_lookup_Ver_1.65_linux_mint.sh
run_fcc_lookup_Ver_1.65_linux.sh
build_fcc_lookup_Ver_1.65_appimage_linux.sh
fcc_icon.png
```

Optional files that may also be placed beside the setup script:

```text
ham.db
AM.dat
EN.dat
amateur_delim.txt
zip_latlon.csv
```

The setup script copies existing database/data files into `~/FCC_DB` if they are present and are not already installed.

## Quick test before install

```bash
chmod +x run_fcc_lookup_Ver_1.65_linux.sh
./run_fcc_lookup_Ver_1.65_linux.sh
```

## Install / update on Linux Mint

```bash
chmod +x setup_fcc_lookup_Ver_1.65_linux_mint.sh
./setup_fcc_lookup_Ver_1.65_linux_mint.sh
```

Run after install:

```bash
fcc-lookup
```

The app also appears in the Linux Mint menu as **FCC Lookup**. If the menu entry does not appear immediately, log out/in or run:

```bash
cinnamon --replace
```

## Optional AppImage build

Run this only after the normal Linux version works:

```bash
chmod +x build_fcc_lookup_Ver_1.65_appimage_linux.sh
./build_fcc_lookup_Ver_1.65_appimage_linux.sh
```

Expected output:

```text
FCC_Lookup-Ver_1.63-linux-x86_64.AppImage
```

## First run

1. Click **Update FCC DB** to download U.S. records.
2. Optionally click **Update Canadian DB**.
3. Use **Database > Download / Update ZIP Centers** for better ZIP-to-ZIP distance/bearing.
4. Enter your own Home callsign and click **Set**.
5. Enter a callsign and click **Look Up**.

## Default paths

Database folder:

```text
~/FCC_DB
```

Config file:

```text
~/.config/FCC_Lookup/fcc_lookup.cfg
```

Settings file:

```text
~/.config/FCC_Lookup/fcc_lookup_settings.json
```

Installed app files:

```text
~/.local/share/fcc-lookup
```

Launcher:

```text
~/.local/bin/fcc-lookup
```

## Notes

- Home callsign starts blank for public users.
- KW3KW is used only as a small author credit, not as a Home default.
- ZIP-center distance is an estimate based on ZIP/ZCTA representative points, not an exact street-address distance.
- If ZIP centers are not loaded, the app may use a fallback estimate.
- The app does not require internet after the database and optional ZIP centers have been downloaded.

## Desktop launcher

The Linux Mint setup script creates both a menu launcher and a desktop launcher named `FCC Lookup.desktop` using `fcc_icon.png` when the icon file is present. If Linux Mint asks for permission the first time, right-click the desktop launcher and choose **Allow Launching**.


## Ver 1.65 update fix

Ver 1.65 fixes the FCC and Canadian database update buttons by restoring the required download/temp/zip imports used by the updater.
