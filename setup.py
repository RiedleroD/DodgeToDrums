#!/usr/bin/python3
import setuptools
import sys
import PyInstaller.__main__ as pim

DEFAULT_PROFILE = "dist"

if len(sys.argv) > 0:
	PROFILE = sys.argv[1]
else:
	PROFILE = DEFAULT_PROFILE

PROFILES = {
	"dist": [
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
	],
	"dev": [
		"--name=DodgeToDrums",
		"--onefile",
		"--clean",
		"--exclude-module=tkinter",
		"--exclude-module=PyQt4",
		"--exclude-module=PyQt5",
		"--exclude-module=numpy",
		"--hidden-import=packaging.requirements",
	#	"--icon=icon.ico",
	#	"--add-data=./data/",
		"main.py"
	]
}

pim.run(PROFILES[PROFILE])
