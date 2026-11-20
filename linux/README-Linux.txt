FCC Lookup for Linux
====================

Offline callsign lookup for U.S. (FCC) and Canadian amateur radio licenses.
Created by KW3KW (Ham Radio Made Simple).

The program in the FCC_Lookup folder carries everything it needs, so nothing else has
to be installed. It runs on Linux Mint 21 and newer, Ubuntu 22.04 and newer, Debian 12,
Fedora and other current desktop Linux (64-bit PC).

INSTALL OR UPDATE
-----------------
Leave the .tar.gz in your Downloads folder, open a terminal (Ctrl+Alt+T), paste these
three lines and press Enter:

F="$(ls -t ~/Downloads/FCC-Lookup-*-Linux*.tar.gz | head -n 1)"
tar -xzf "$F" -C ~/Downloads
bash ~/Downloads/"$(tar -tzf "$F" | head -n 1 | cut -d/ -f1)"/update_linux.sh

It installs into ~/Applications/FCC-Lookup and adds icons to the menu and the desktop.
Your database (~/FCC_DB) and settings (~/.config/FCC_Lookup) are kept on every update.

Step-by-step guide: FCC_Lookup_Linux_Install_Guide.pdf (in this folder).
How to use the program: FCC_Lookup_User_Guide.pdf.

REMOVE
------
bash ~/Applications/FCC-Lookup/linux_uninstall.sh

DOWNLOADS AND HELP
------------------
Newest version: https://github.com/HamRadioMadeSimple/FCC_Lookup/releases/latest
Problems:       https://github.com/HamRadioMadeSimple/FCC_Lookup/issues

FCC Lookup is free software under the GNU General Public License v3 (LICENSE.txt).
