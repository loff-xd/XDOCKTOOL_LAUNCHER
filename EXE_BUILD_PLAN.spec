# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['launcher.py'],
             pathex=['venv\\Lib\\site-packages', 'C:\\Users\\Loff0\\PycharmProjects\\XDOCKTOOL_LAUNCHER'],
             binaries=[],
             datas=[('XDMGR.ico', '.'), ('XDMGR_S.ico', '.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='XDOCK_MANAGER LAUNCHER',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , version='version.txt', icon='XDMGR.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='XDOCK_MANAGER LAUNCHER')
