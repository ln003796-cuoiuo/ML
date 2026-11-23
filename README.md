# ML Installer

Windows GUI installer based only on `ИНСТРУКЦИЯ.txt`.

It copies:
- `vcruntime140_1.dll` to the selected Minecraft for Windows `XboxGames\\Minecraft for Windows\\Content` folder.
- `minekryak.dll` to `%APPDATA%\\Minecraft Bedrock\\mods`, creating the folder if needed.

The app searches mounted drive letters automatically and allows selecting the Content folder manually. Existing destination files are backed up with a timestamp before replacement.

## Build
Push to `main` or `build-installer-exe`, or run **Build Windows EXE** manually from GitHub Actions. Download the `ML-Installer-Windows` artifact from the successful workflow run.

The executable is built as a single-file Windows GUI app with the attached logo as its icon.
