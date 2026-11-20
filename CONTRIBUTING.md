# Helping with FCC Lookup

Thanks for helping! Bug reports, ideas and code are all welcome.

## Reporting a problem

Open an issue on the [Issues page](https://github.com/HamRadioMadeSimple/FCC_Lookup/issues) with:
- the FCC Lookup version (Help > About) and your Windows or Linux version
- what you clicked, what you expected, and what happened (a screenshot helps a lot)
- if the window never opens: `error_log.txt` from the settings folder
  (`%APPDATA%\FCC_Lookup` on Windows, `~/.config/FCC_Lookup` on Linux)

## Where things are

| Folder | What |
|---|---|
| `windows/` | `FCC_Lookup_Ver_1.65.pyw` (the program), PyInstaller `.spec`, Inno Setup `.iss`, `Build_FCC_Lookup_Ver_1.65.bat` |
| `linux/` | `FCC_Lookup_Ver_1.65_linux.py` (the program), `build_linux.sh`, `update_linux.sh` (install / update), `linux_uninstall.sh` |
| `docs/` | The guides (PDF) |

The Windows and Linux programs are the same code apart from the default database folder (`C:\FCC_DB` or
`~/FCC_DB`) and the version label. A change to one should be made to the other.

## Running from source

Python 3 with Tk (Linux: `sudo apt install python3-tk`). Nothing else is needed.

```
python3 linux/FCC_Lookup_Ver_1.65_linux.py      # Linux, or: bash linux/run_fcc_lookup_Ver_1.65_linux.sh
python windows\FCC_Lookup_Ver_1.65.pyw          # Windows, or Run_FCC_Lookup_Ver_1.65_Debug.bat
```

## Building the downloads

- **Linux:** `bash linux/build_linux.sh` makes `output/FCC-Lookup-<version>-Linux.tar.gz`. Build on the oldest
  Linux you want to support: the release is built on Ubuntu 22.04 so it runs on Mint 21 and newer.
- **Windows:** run `windows\Build_FCC_Lookup_Ver_1.65.bat` (needs Python 3 and Inno Setup 6).

Keep `.sh` and `.py` files with LF line endings and `.bat` / `.iss` files with CRLF (`.gitattributes` does this).

## Making a release

Raise `APP_VERSION` in both programs and add a `## <version> - <date>` section at the top of `CHANGELOG.md`,
written for users. Then create a release with the tag `v<version>` on GitHub: the Release workflow builds the
Setup.exe, the portable zip and the Linux `.tar.gz`, installs the Linux download on clean Ubuntu, Debian and
Fedora to check it, and attaches the files with the CHANGELOG section as the release notes.
