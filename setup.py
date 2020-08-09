#!/usr/bin/python3
import setuptools, argparse
import PyInstaller.__main__ as pim

DEFAULT_PROFILE = set([
	"--name=DodgeToDrums",
	"--onefile",
	"--windowed",
	"--clean",
	"--exclude-module=tkinter",
	"--exclude-module=PyQt4",
	"--exclude-module=PyQt5",
	"--exclude-module=numpy",
	"--hidden-import=packaging.requirements",
#	"--icon=icon.ico",
#	"--add-data=./data/",
	"main.py"
])

PROFILES = {
	"dev": [
		"--windowed",
	]
}

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Builds DodgeToDrums")
	parser.add_argument("profile", type=str, nargs='?', help="The build-profile")
	args = parser.parse_args()

	if args.__contains__("profile") and args.profile is not None:
		PROFILE = args.profile
		pim.run(DEFAULT_PROFILE.symmetric_difference(PROFILES[PROFILE]))
	else:
		pim.run(DEFAULT_PROFILE)
