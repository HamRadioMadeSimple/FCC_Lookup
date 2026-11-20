# FCC Lookup

An offline callsign lookup for U.S. FCC and Canadian amateur radio licenses. No internet connection needed once the database is built.

**Windows and Linux** · [Download](https://github.com/HamRadioMadeSimple/FCC_Lookup/releases/latest) · [Guides](docs) · [Website](https://hamradiomadesimple.github.io/)

## What it does

Type a callsign, get the licensee. The lookup runs against a local database on your own machine, so it works without an internet connection — useful in the field, during an outage, or anywhere the connection is unreliable.

- U.S. FCC amateur records and Canadian amateur records in one database
- Browse Records for working through the data rather than looking up one call at a time
- Optional distance and bearing from a Home callsign you set
- Builds and updates its own database, downloading directly from the FCC and ISED Canada

## Building the database

On first run, the app downloads the FCC amateur archive and the Canadian amateur data file, extracts them, and imports them into a local SQLite database called `ham.db`.

The database lives in:

- **Windows:** `C:\FCC_DB`
- **Linux:** `~/FCC_DB`

This takes a while and needs an internet connection. Everything after it is offline. Re-run the download whenever you want current data — the FCC updates daily.

The app can also download ZIP code centroids from the U.S. Census, which is what distance and bearing are calculated from.

## Sharing with JS8Map

`ham.db` is the same database used by [JS8MapChat](https://github.com/HamRadioMadeSimple/JS8MapChat). If you run both, they can share one copy rather than each building their own.

## Download and install

**[Download FCC Lookup](https://github.com/HamRadioMadeSimple/FCC_Lookup/releases/latest)** (Releases page, free).

| System | File | How |
|---|---|---|
| Windows 10/11 | `FCC_Lookup_Ver_1.65_Setup.exe` | Run it. [Windows Installation Guide (PDF)](docs/FCC_Lookup_Windows_Install_Guide.pdf) |
| Windows, no install | `FCC-Lookup-1.65-Windows-Portable.zip` | Unzip and run `FCC_Lookup_Ver_1.65.exe` |
| Linux | `FCC-Lookup-1.65-Linux.tar.gz` | Three pasted lines, below. [Installing FCC Lookup on Linux (PDF)](docs/FCC_Lookup_Linux_Install_Guide.pdf) |

How to use it: **[User Guide (PDF)](docs/FCC_Lookup_User_Guide.pdf)**.

### Linux

The Linux download carries its own Python and window toolkit, so **nothing else needs installing**: no
password, no extra packages. It runs on Linux Mint 21 and newer, Ubuntu 22.04 and newer, Debian 12, Fedora and
other current desktop Linux (64-bit PC).

Save the `.tar.gz` in your Downloads folder, open a terminal (Ctrl+Alt+T), paste these three lines and press Enter:

```bash
F="$(ls -t ~/Downloads/FCC-Lookup-*-Linux*.tar.gz | head -n 1)"
tar -xzf "$F" -C ~/Downloads
bash ~/Downloads/"$(tar -tzf "$F" | head -n 1 | cut -d/ -f1)"/update_linux.sh
```

It installs into `~/Applications/FCC-Lookup`, with an **FCC Lookup** icon in the menu and on the desktop. Paste
the same lines again to update; your database and settings are kept. To remove it:
`bash ~/Applications/FCC-Lookup/linux_uninstall.sh`.

### From source

The program is one Python file with no extra packages: `windows/FCC_Lookup_Ver_1.65.pyw` or
`linux/FCC_Lookup_Ver_1.65_linux.py` (needs Python 3 with Tk). Building the downloads is described in
[CONTRIBUTING.md](CONTRIBUTING.md).

## Data sources

**FCC amateur license database** — United States government work, public domain.

**Canadian amateur callsign data** — open data published by ISED Canada.

**ZIP code centroids** — U.S. Census Bureau, public domain.

All of it is downloaded from the official sources by the app itself. None of it is redistributed here. Credits for the parts bundled in the downloads are in [NOTICE.md](NOTICE.md).

## License

Copyright (C) 2026 MJ Jordan (KW3KW)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

The full license text is in [LICENSE](LICENSE).

## Reporting problems

Open an issue on the [Issues](https://github.com/HamRadioMadeSimple/FCC_Lookup/issues) page. Please include: Windows or Linux, the version (Help > About), and what you expected to happen. More in [CONTRIBUTING.md](CONTRIBUTING.md).

## More free ham radio apps by KW3KW

[RigPanel](https://github.com/HamRadioMadeSimple/RigPanel) · [Flrig EMCOMM](https://github.com/HamRadioMadeSimple/Flrig-EMCOMM) · [JS8Map Spotter](https://github.com/HamRadioMadeSimple/JS8MapSpotter) · [JS8MapChat](https://github.com/HamRadioMadeSimple/JS8MapChat) · [DigiApp Launcher](https://github.com/HamRadioMadeSimple/DigiApp-Launcher) · all on the [website](https://hamradiomadesimple.github.io/) and the [YouTube channel](https://www.youtube.com/@hamradiomadesimple).

73 de KW3KW
