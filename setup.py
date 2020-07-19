#!/usr/bin/python3
import PyInstaller.__main__ as pim

pim.run([
	"--name=DodgeToDrums",
	"--onefile",
	"--windowed",
	"--clean",
#	"--icon=icon.ico",
#	"--add-data=./data/",
	"main.py"
	])
