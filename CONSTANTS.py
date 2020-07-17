#!/usr/bin/python3
print("started")
import os,sys
import pyglet
from pyglet.window import key
import pyglet.window as pgw
from time import time
print("imported libraries")

DISPLAY=pyglet.canvas.get_display()#It took ages to find these functions, so don't question them.
SCREEN=DISPLAY.get_default_screen()
WIDTH=SCREEN.width
HEIGHT=SCREEN.height
WIDTH2=WIDTH/2
HEIGHT2=HEIGHT/2
BTNHEIGHT=HEIGHT/15
BTNWIDTH=WIDTH/10
ANCHORSy=("bottom","center","top")
ANCHORSx=("left","center","right")
print(f"initialized screen with size {WIDTH}x{HEIGHT}")

TIME=time()
TIMEC=0
DTIME=0
print(f"initialized time {TIME}")

class ENTCONTAINER:#base class for all entity containers
	@classmethod
	def draw(cls):
		for ent in cls.all():
			if ent:
				ent.draw()

class LABELS(ENTCONTAINER):
	fps=None
	ups=None
	@classmethod
	def all(cls):
		yield cls.fps
		yield cls.ups

class BTNS(ENTCONTAINER):
	start=None
	sett=None
	exit=None
	back=None
	@classmethod
	def all(cls):
		yield cls.start
		yield cls.sett
		yield cls.exit
		yield cls.back

print("initialized entity containers")
