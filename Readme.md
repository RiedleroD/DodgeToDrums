# Dodge to Drums
[![Discord server: https://discord.gg/6teKaP2](https://img.shields.io/discord/734732041001762856)](https://discord.gg/6teKaP2)
[![Pyinstaller build](https://github.com/RiedleroD/DodgeToDrums/workflows/Pyinstaller%20build/badge.svg)](https://github.com/RiedleroD/DodgeToDrums/actions)

## What is this?

This is a game in development. It's planned to become something between "Just Shapes and Beats" and "Cuphead".
That means it'll become a bullet hell shooter with focus on music and rhythm.

## Who made this?

You will also be able to see this in the ingame credits once they're implemented, but here's the crew so far:

Programming
- Riedler

Sketches & Art:
- Dark Rosemary

Playtesting:
- Andreas S. (Windows)

Compiling:
- Riedler (Linux)
- Andreas S. (Windows)

Music:
- Riedler
- Dark Rosemary

## Compatibility

You don't need any special libraries to run it on Windows or Linux.
MacOS is currently unsupported, so please refer to [compiling](#compiling) and figure it out with the guides for Linux and/or Windows. This may improve in the future.
It <u>should</u> run on all major Linux distributions, but only Ubuntu and Arch Linux are supported.
It <u>should</u> also run on everything above including Windows XP, but only Windows 10 is supported.

## Screenshots

No screenshots are yet available, because it's so early in development right now, but Dark Rosemary drew an amazing sketch of what it's going to look like:
![Sketch of DTD](https://riedler.wien/sfto/DTD_sketch1.jpg)

## Usage

Download the matching executable for your OS and save it somewhere where you'll easily find it again, e.g. your Desktop.
When you first start the program, all settings are assumed to be the defaults. A config file `conf.json` will only be created after changing the settings and saving them.
The menu is controllable with the mouse and a few keys. ESC is usually for going back and Enter for confirming stuff.
In the main game, the character is controllable with WASD, Space and/or the Arrow keys. You can pause with ESC.

## Adding textures

This is not implemented yet, but planned would be a data/ directory with a `sprites.json` configuration file and the sprites itself in it.
Most likely, only png will be supported & animations and sprites will be stretched to their proper size.

## <a name="compiling"></a> Compiling

### on windows

In the cmd:
First run `pip3 install pyglet PyInstaller`
Then run `python3 setup.py`, if this doesn't produce any output, try `pyinstaller \args\` where `\args\` is all the options that aren't commented out in `setup.py`.
I haven't figured out why this happens in windows yet, if you know, please file an issue.
After the command finished successfully, there should be a `build/` and a `dist/` directory. You can delete the `build/` directory, and move the executable from the `dist/` directory wherever you want. Just make sure it's not in a folder which doesn't let the program create new files in it since it's going to create a `conf.json` in the same directory.
If you encounter any error that's not explained in this guide, please file an issue in the repo.

### on Linux

In bash (or zsh probably too):
First run `sudo -H pip3 install pyglet PyInstaller` or install pyglet from your package manager of choice. It often works better outside of pip.
Then run `python3 setup.py`, which, after a short wait, produces a `build/` and a `dist/` directory. You can delete the `build/` directory, and move the executable from the `dist/` directory wherever you want. Just make sure it's not in a folder which doesn't let the program create new files in it since it's going to create a `conf.json` in the same directory.
If you encounter any error that's not explained in this guide, please file an issue in the [repo](https://github.com/RiedleroD/DodgeToDrums/issues).
