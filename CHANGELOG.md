# Changelog

## 1.68 - 2026-11-20
- **New install: FCC Lookup offers to download the callsign data.** The first time it starts with no database, it
  asks "Download the U.S. (FCC) and Canadian amateur databases now?". Yes downloads both, one after the other
  (several minutes). If a database is already there, for example from JS8Map or an earlier install, it is used
  straight away and nothing is asked.
- **Fixed: license class names.** The result card showed just "E" for Amateur Extra licenses, and some other
  classes had the wrong name. It now reads Technician, General, Amateur Extra, Advanced, Novice or Technician Plus.

## 1.67 - 2026-11-20 - first release built by GitHub
FCC Lookup answers one question quickly: who holds this callsign, and where are they from you? It looks up U.S. (FCC)
and Canadian amateur licenses from a database on your own PC, so it works without the internet, and shows the
distance and direction from your own callsign.

- **Linux: nothing else to install.** The new download, `FCC-Lookup-1.67-Linux.tar.gz`, carries its own Python and
  window toolkit. Three pasted lines install it into `~/Applications/FCC-Lookup`, with icons in the menu and on the
  desktop. No password and no extra packages. Runs on Linux Mint 21 and newer, Ubuntu 22.04 and newer, Debian 12,
  Fedora and other current desktop Linux.
- Linux: pasting the same three lines again updates the program and keeps your database (`~/FCC_DB`) and settings.
  A copy installed with the earlier setup script (in the hidden `~/.local/share/fcc-lookup`) is moved across.
- Linux: new uninstaller, `bash ~/Applications/FCC-Lookup/linux_uninstall.sh`. It asks before deleting your database.
- Linux: the `.tar.gz` replaces the AppImage, which needed extra system parts (FUSE) on newer Ubuntu.
- Windows: new portable zip for running without installing. The Setup.exe now installs the User Guide too, with a
  Start Menu shortcut.
- Guides are PDFs in the `docs` folder and inside every download: User Guide, Windows Installation Guide and
  Installing FCC Lookup on Linux.
- The Update FCC DB and Update Canadian DB buttons work again (fixed in 1.65).
