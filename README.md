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

## Install

### Option A: download the app (easiest)
1. Open the [Releases](../../releases) page and download `MeshSwapper.zip`.
2. Unzip it anywhere and start `MeshSwapper\MeshSwapper.exe`.

### Option B: run from source
1. Install [Python 3.9+](https://www.python.org/downloads/) (tick "Add python.exe to PATH").
2. Run `pip install -r requirements.txt`.
3. Double-click `meshswapper.pyw`.

### Option C: build the EXE yourself
Put `build_exe.bat`, `meshswapper.pyw` and `meshswapper.ico` in one folder and run `build_exe.bat`.
The finished app appears in the folder `MeshSwapper`.

## How to use

1. Install and start [Bloxstrap](https://bloxstraplabs.com) once.
2. In MeshSwapper, create a set (or import a folder) and add your `.mesh` files.
3. Select the set and press **Apply set**.
4. Press **Launch Roblox**, or **Refresh Roblox** if the game is already running.

## Antivirus warning?

Some antivirus programs (for example Windows Defender, `Trojan:Win32/Bearfoos.A!ml`) wrongly flag EXEs made with PyInstaller. The `!ml` means the detection is only a machine-learning guess. The full source code is in this repository, so you can read it or build the EXE yourself (Option C).

## Disclaimer

MeshSwapper is a fan-made tool. It is **not affiliated with or endorsed by Roblox Corporation or Bloxstrap**. It only copies files into Bloxstrap's modifications folder and closes and starts the official client again. Nothing is injected into the game. Use it at your own risk.

## Credits

App created with the help of [Claude](https://claude.ai) by Anthropic.
Questions or feedback: [Discord](https://discord.gg/E5yuUshPXY)

## License

[MIT](LICENSE)
