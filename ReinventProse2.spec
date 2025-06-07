# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

app_data_files = [
    ('app_icon.ico', '.'),
    ('bold.png', '.'),
    ('edit.png', '.'),
    ('edit2.png', '.'),
    ('italic.png', '.'),
    ('library.png', '.'),
    ('new_book.png', '.'),
    ('open.png', '.'),
    ('redo.png', '.'),
    ('save.png', '.'),
    ('underline.png', '.'),
    ('undo.png', '.')
]

a = Analysis(
    ['main.py'],
    pathex=['C:\\Users\\Mauricio\\Documents\\Version2'], # Asegúrese que esta ruta es la raíz de su proyecto
    binaries=[], # PyInstaller intentará encontrar las DLLs de Python automáticamente
    datas=app_data_files,
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
    a.binaries,  # <--- AÑADIDO/CORREGIDO
    a.zipfiles,  # <--- AÑADIDO/CORREGIDO
    a.datas,
    [],
    name='ReinventProse2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
)
# No hay sección COLLECT para modo --onefile