# -*- mode: python ; coding: utf-8 -*-
# FCC Lookup Ver 1.68 - PyInstaller Spec File
# Fast-launch test: onedir build, no Pillow dependency.

a = Analysis(
    ['FCC_Lookup_Ver_1.68.pyw'],
    pathex=[],
    binaries=[],
    datas=[
        ('fcc_icon.png',         '.'),
        ('FC_launcher_icon.ico', '.'),
    ],
    hiddenimports=[
        'sqlite3',
        'csv',
        'urllib.request',
        'zipfile',
        'tempfile',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'math',
        'json',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PIL', 'Pillow'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FCC_Lookup_Ver_1.68',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='FC_launcher_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FCC_Lookup_Ver_1.68',
)
