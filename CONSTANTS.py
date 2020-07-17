#!/usr/bin/python3
print("started")
import os,sys
import json
import pyglet
from pyglet.window import key
import pyglet.window as pgw
from time import time
print("imported libraries")

curdir=os.path.abspath(os.path.dirname(__file__))
conffp=os.path.join(curdir,"conf.json")

class CONF:
	fullscreen=None
	showfps=None
	@classmethod
	def load(cls,fp):
		with open(fp,"r") as f:
			data=json.load(f)
		cls.loads(data)
		print(f"loaded config:\n {data}")
	@classmethod
	def loads(cls,data):
		cls.fullscreen=data["fullscreen"]
		cls.showfps=data["showfps"]
	@classmethod
	def dump(cls,fp):
		with open(fp,"w+") as f:
			json.dump(cls.dumps(),f)
		print("dumped config")
	@classmethod
	def dumps(cls):
		return {"fullscreen":cls.fullscreen,"showfps":cls.showfps}

if os.path.exists(conffp):
	CONF.load(conffp)
else:
	CONF.loads({"fullscreen":True,"showfps":True})
	CONF.dump(conffp)

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
	#menu
	start=None
	sett=None
	#generic back & cancle buttons
	back=None
	cancle=None
	#settings
	fullscr=None
	showfps=None
	@classmethod
	def all(cls):
		yield cls.start
		yield cls.sett
		yield cls.cancle
		yield cls.back
		yield cls.fullscr
		yield cls.showfps

print("initialized entity containers")
