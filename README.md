# FCC Lookup

An offline callsign lookup for U.S. FCC and Canadian amateur radio licenses. No internet connection needed once the database is built.

**Version 1.65 — Windows and Linux**

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

`ham.db` is the same database used by [JS8MapChat](https://github.com/mjordan501/JS8MapChat). If you run both, they can share one copy rather than each building their own.

## Installing

### Windows

Installers are on the [Releases](../../releases) page.

To build from source instead, run `Build_FCC_Lookup_Ver_1.65.bat` in the `windows` folder. It uses PyInstaller, with Inno Setup for the installer.

### Linux

Put the contents of the `linux` folder together in one directory, then:

    chmod +x run_fcc_lookup_Ver_1.65_linux.sh
    ./run_fcc_lookup_Ver_1.65_linux.sh

That runs it directly for a quick test. To install properly, use `setup_fcc_lookup_Ver_1.65_linux_mint.sh`. An AppImage build script is included as well.

Written and tested on Linux Mint. Other distributions should work but have not been checked.

## Requirements

Python with Tkinter and SQLite, both standard. The Windows builds bundle everything, so nothing needs installing separately.

## Data sources

**FCC amateur license database** — United States government work, public domain.

**Canadian amateur callsign data** — open data published by ISED Canada.

**ZIP code centroids** — U.S. Census Bureau, public domain.

All of it is downloaded from the official sources by the app itself. None of it is redistributed here.

## License

Copyright (C) 2026 MJ Jordan (KW3KW)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

The full license text is in [LICENSE](LICENSE).

## Reporting problems

Open an issue on the [Issues](../../issues) tab. Please include: Windows or Linux, and what you expected to happen.
