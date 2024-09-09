# -*- mode: python ; coding: utf-8 -*-

import platform


def get_icon():
    if platform.system() == 'Windows':
        return 'packaging\\windows\\icon.ico'
    return 'blackboard_sync/assets/logo.png'


def get_datas():
    s = "\\" if platform.system() == "Windows" else "/"

    return [
        (f"blackboard_sync{s}assets", f"blackboard_sync{s}assets"),
        (f"blackboard_sync{s}qt", f"blackboard_sync{s}qt"),
        (f"blackboard_sync{s}universities.json", f"blackboard_sync")
    ]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=get_datas(),
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BlackboardSync',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[get_icon()],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BlackboardSync',
)

app = BUNDLE(
    coll,
    name="BlackboardSync.app",
    icon='blackboard_sync/assets/logo.png',
    bundle_indentifier='app.bbsync.BlackboardSync',
)