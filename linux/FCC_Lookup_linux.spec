# -*- mode: python ; coding: utf-8 -*-
# FCC Lookup - PyInstaller settings for the Linux download (used by build_linux.sh).
# One folder, FCC_Lookup/, holding the program with its own Python and Tk, so the user's PC
# needs nothing extra. Built on Ubuntu 22.04 by GitHub so it runs on Mint 21 / Ubuntu 22.04 and newer.

a = Analysis(
    ['FCC_Lookup_Ver_1.68_linux.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('fcc_icon.png',         '.'),
        ('FC_launcher_icon.ico', '.'),
    ],
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog',
        'sqlite3', 'csv', 'urllib.request', 'zipfile', 'tempfile', 'json', 'math',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PIL', 'Pillow', 'numpy'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FCC_Lookup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='FCC_Lookup',
)
