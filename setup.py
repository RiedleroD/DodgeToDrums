#!/usr/bin/python3
import setuptools
import PyInstaller.__main__ as pim

pim.run([
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
