# Dodge to Drums
[![Discord server: https://discord.gg/jKUd9Ny](https://img.shields.io/discord/734732041001762856?label=Discord&logo=discord)](https://discord.gg/jKUd9Ny)
[![Pyinstaller build](https://github.com/RiedleroD/DodgeToDrums/workflows/Pyinstaller%20build/badge.svg)](https://github.com/RiedleroD/DodgeToDrums/actions)
[![latest-release](https://img.shields.io/github/v/release/RiedleroD/DodgeToDrums?include_prereleases&label=latest-release)](https://github.com/RiedleroD/DodgeToDrums/releases/latest)

## What is this?

This is a game in development. It's planned to become something between "Just Shapes and Beats" and "Cuphead".
That means it'll become a bullet hell shooter with focus on music and rhythm.

## Who made this?

You will also be able to see this in the ingame credits once they're implemented, but here's the crew so far:

Programming
- Riedler
- Philip Damianik

Sketches & Art:
- Dark Rosemary

Playtesting:
- Andreas S. (Windows)
- Philip Damianik (dual-screen Windows)

Compiling:
- Riedler (Linux)
- Andreas S. (Windows)
- Philip Damianik (build pipeline)

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

Download the matching executable for your OS and save it somewhere where you'll easily find it again, e.g. in a separate folder on your Desktop.
Then download the level archive (base\_levels.zip or base\_levels.tar.xz) and the data archive (base\_data.zip or base\_data.tar.xz) and extract them into the executable folder as levels/ and data/
When you first start the program, all settings are assumed to be the defaults. A config file `conf.json` will be created after changing the settings and saving them.
The menu is controllable with the mouse and a few keys. ESC is usually for going back and Enter for confirming stuff.
In the main game, the character is controllable with WASD or the Arrow keys. You can pause with ESC.
All of those controls can be changed in the settings, as well as various other stuff.

## Adding resources

All resources are in the `data/` subfolder.
All textures are specified in `data/sprites.json`, in the format `"sprite_name":["file_name",true]`, where `"file_name"` is the relative file path without file extension (only png is allowed) and `true` is a boolean that determines if the upscaling method is set as Nearest-Neighbour or Linear.
Animations are also supported, and can be specified in the format `"animation_name":[["file1","file2",…],[18,true]]`, where as many files as necessary can be specified and `18` is the number of frames one picture should last. Animations aren't supported in all objects, but in most. If they're not supported, the animation will stay at frame 0.
All sound effects are specified in `data/sfx.json`, in the format `"sfx_name":["file_name",false]`, where `"file_name"` is the relative file path without file extension in the opus format, and `false` is a boolean that determines if the file is streamed to playback or loaded on program startup. `false` is heavily recommended here, and `true` can lead to crashes in some circumstances.

## <a name="compiling"></a> Compiling

### on windows

You'll need python for this. Make sure to download the newest version.
In the cmd:
First run `pip3 install -r requirements.txt`
Then run `python3 setup.py`, if this doesn't produce any output, try `pyinstaller \args\`, where `\args\` is all the options that aren't commented out in `setup.py`.
I haven't figured out why this happens in windows yet, if you know, please file an issue.
After the command finished successfully, there should be a `build/` and a `dist/` directory. You can delete the `build/` directory, and move the executable from the `dist/` directory wherever you want.
If you encounter any error that's not explained in this guide, please file an issue in the [repo](https://github.com/RiedleroD/DodgeToDrums/issues).

### on Linux

In bash (or zsh probably too):
First run `pip3 install -r requirements.txt --user`.
Then run `python3 setup.py`, which, after a short wait, produces a `build/` and a `dist/` directory. You can delete the `build/` directory, and move the executable from the `dist/` directory wherever you want.
If you encounter any error that's not explained in this guide, please file an issue in the [repo](https://github.com/RiedleroD/DodgeToDrums/issues).
