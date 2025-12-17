# start.spec
block_cipher = None

a = Analysis(
    ['start.pyw'],
    pathex=[],
    binaries=[],
    datas=[
        ('controller.py', '.'),
        ('background_service.py', '.'),
        ('fetch_data.py', '.'),
        ('generate_wallpaper.py', '.'),
        ('icon.ico', '.')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='Wordspire By (Merajcode YT)', 
    debug=False,
    strip=False,
    upx=True,
    console=False,  # Set to False if you don’t want a command window
    icon='icon.ico' 
)
