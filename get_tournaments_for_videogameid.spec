# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['get_tournaments_for_videogameid.py'],
    pathex=[],
    binaries=[],
    datas=[
        ("auth_token.txt","."),
        ("get_tournaments_for_videogameid_query.txt","."),
        ("videogameid_timestamp.txt","."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='get_tournaments_for_videogameid',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='get_tournaments_for_videogameid',
)
