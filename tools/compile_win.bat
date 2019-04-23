python parser.py "../code/"

pyinstaller --onefile ../code/source.py
rd /s /q "../code/__pycache__"
rd /s /q build
move "dist\source.exe" "../bin"
rd /s /q dist
del source.spec

PAUSE