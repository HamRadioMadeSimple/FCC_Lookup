# Notices and credits

FCC Lookup is Copyright (C) 2026 MJ Jordan (KW3KW) and is free software under the GNU General Public License,
version 3 or later (see [LICENSE](LICENSE)).

## Data it downloads (not included)

FCC Lookup ships with no callsign data. The program downloads it from the official sources when you click the
update buttons:

- **FCC amateur license database** (ULS), U.S. government work, public domain. <https://www.fcc.gov/uls>
- **Canadian amateur callsign list**, open data published by Innovation, Science and Economic Development
  Canada (ISED). <https://apc-cap.ic.gc.ca/>
- **ZIP code centre points** (ZCTA), U.S. Census Bureau, public domain. <https://www.census.gov/>

FCC Lookup is an independent project and is not part of, or endorsed by, the FCC, ISED Canada or the Census Bureau.
It shares its `ham.db` database format with JS8Map ([JS8MapChat](https://github.com/HamRadioMadeSimple/JS8MapChat)).

## Included in the ready-built downloads

The Windows program and the Linux program are made with **PyInstaller** and each carries its own copy of:

- **Python** (Python Software Foundation License), <https://www.python.org/>
- **Tcl/Tk** (BSD-style Tcl/Tk license), <https://www.tcl-lang.org/>
- On Linux, the system libraries Tk needs to draw its window (such as libX11, libXft, fontconfig and FreeType,
  under their own MIT-style licenses), taken from Ubuntu 22.04.

The PyInstaller bootloader is GPL with an exception that allows it in programs under any license,
<https://pyinstaller.org/>. The Windows installer is made with **Inno Setup** by Jordan Russell,
<https://jrsoftware.org/isinfo.php>.

## Screenshots

Names in the guides' screenshots are blurred; callsigns are shown as examples only.
