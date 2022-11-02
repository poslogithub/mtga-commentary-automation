PyInstaller --noconfirm --clean ".\commentary_backend.spec"
Remove-Item dist\commentary_backend.zip
Compress-Archive -Path .\dist\commentary_backend -DestinationPath .\dist\commentary_backend.zip
Copy-Item .\src\mtgacommentary\SeikaSay2.exe .\dist\commentary_backend\
