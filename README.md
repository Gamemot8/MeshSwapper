# MeshSwapper

**Swap your Roblox avatar meshes: preview, create, convert and apply them in seconds.**

MeshSwapper is a Windows app for [Bloxstrap](https://bloxstraplabs.com) users. It manages sets of `.mesh` files, shows them on a 3D dummy, applies them with one click and restarts Roblox so you see the result in game.

<!-- Add a screenshot: drag an image into this file on GitHub, it uploads it for you -->
<!-- ![MeshSwapper](screenshot.png) -->

## Features

- **Mesh sets:** create, import and manage sets of `.mesh` files
- **One-click Apply / Reset:** only touches files MeshSwapper created itself
- **Live 3D preview:** parts assembled like the Roblox dummy, rotate, zoom, auto-rotate
- **Launch / Refresh Roblox:** start Roblox through Bloxstrap, or restart it and rejoin the same game
- **Mesh creator:** build meshes from 8 shapes (move, rotate, scale, taper, mirror, undo/redo) and save them straight into a set
- **Convert files:** OBJ, FBX, STL, PLY, OFF, DAE, glTF/GLB, 3MF and Roblox files to `.mesh`, with automatic unit scaling and direction tools
- **Purple galaxy theme** with animated splash screen

## Install (one click)

1. Download **`Install_MeshSwapper.bat`** from the [Releases](../../releases/latest) page. This one file is all you need.
2. Double-click it. If Windows SmartScreen appears, click **More info**, then **Run anyway**.
3. Wait a few minutes (the first time takes longest). The installer does everything for you:
   - installs Python 3.9 for your user if it is missing (no admin rights needed)
   - downloads the MeshSwapper files from this repository
   - builds the app and installs it to `%LOCALAPPDATA%\Programs\MeshSwapper`
   - puts a shortcut on your Desktop and in the Start menu, then starts the app

You need an internet connection and about 1 GB of free space while it builds.

### Something broke? Repair
Run `Install_MeshSwapper.bat` again. It closes the app, repairs Python if needed, rebuilds everything and reinstalls it. **Your sets and settings are kept**, they are stored separately in `%LOCALAPPDATA%\MeshSwapper`.

### Uninstall
Run `Uninstall_MeshSwapper.bat`. It removes the program and the shortcuts. Your sets stay until you delete `%LOCALAPPDATA%\MeshSwapper` yourself.

### Other ways to use it
- **Run from source:** install [Python 3.9+](https://www.python.org/downloads/) (tick "Add python.exe to PATH"), run `pip install -r requirements.txt`, then double-click `meshswapper.pyw`.
- **Portable build:** if a `MeshSwapper.zip` is attached to the release, unzip it anywhere and start `MeshSwapper\MeshSwapper.exe`. No Python needed.

## How to use

1. Install and start [Bloxstrap](https://bloxstraplabs.com) once.
2. In MeshSwapper, create a set (or import a folder) and add your `.mesh` files.
3. Select the set and press **Apply set**.
4. Press **Launch Roblox**, or **Refresh Roblox** if the game is already running.

## Troubleshooting

- **Run `Install_MeshSwapper.bat` again.** It fixes most problems by itself.
- Close MeshSwapper before you run it again.
- Do not run the installer from inside a ZIP window, unzip first. (Downloading only the `.bat` from Releases works fine.)
- The installer needs internet. If a download fails, check your connection and retry.
- If the Python install fails, install [Python 3.9](https://www.python.org/downloads/release/python-3913/) by hand (tick "Add python.exe to PATH") and run the installer again.
- Still stuck? Ask on [Discord](https://discord.gg/E5yuUshPXY) and include the last lines shown in the installer window.

## Antivirus warning?

Some antivirus programs (for example Windows Defender, `Trojan:Win32/Bearfoos.A!ml`) wrongly flag EXEs made with PyInstaller. The `!ml` means the detection is only a machine-learning guess. The installer builds the app on **your own PC** from the source code in this repository, so you can read exactly what runs. If you prefer, skip the EXE and run `meshswapper.pyw` from source.

## Disclaimer

MeshSwapper is a fan-made tool. It is **not affiliated with or endorsed by Roblox Corporation or Bloxstrap**. It only copies files into Bloxstrap's modifications folder and closes and starts the official client again. Nothing is injected into the game. Use it at your own risk.

## Credits

App created with the help of [Claude](https://claude.ai) by Anthropic.
Discord: Gamemot8

## License

[MIT](LICENSE)
