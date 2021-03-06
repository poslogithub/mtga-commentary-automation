# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['src\\mtgacommentary\\commentary_backend.py'],
             pathex=['src\\mtgacommentary'],
             binaries=[],
             datas=[('src\\mtgacommentary\\config\\defaultSpeaker.json', 'config'), ('src\\mtgacommentary\\LICENSE', 'LICENSE'), ('src\\mtgacommentary\\wav', 'wav')],
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
          name='commentary_backend',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , version='src\\mtgacommentary\\file_version_info.txt', icon='src\\mtgacommentary\\icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='commentary_backend')
