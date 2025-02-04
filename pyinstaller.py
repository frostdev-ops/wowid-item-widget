import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--noconsole',
    '--icon=frost3.ico',
    '--name=Frostdev Property Modifier',
    '--optimize=2',
])