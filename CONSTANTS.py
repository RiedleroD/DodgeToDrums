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
	defaults={"fullscreen":True,"showfps":True,"vsync":True}
	@classmethod
	def load(cls,fp):
		with open(fp,"r") as f:
			data=json.load(f)
		cls.loads(data)
		print(f"loaded config:\n {data}")
	@classmethod
	def loads(cls,data):
		for sett, default in cls.defaults.items():
			if sett in data:
				val=data[sett]
			else:
				val=default
			setattr(cls,sett,val)
	@classmethod
	def dump(cls,fp):
		with open(fp,"w+") as f:
			json.dump(cls.dumps(),f)
		print("dumped config")
	@classmethod
	def dumps(cls):
		return {name:getattr(cls,name) for name in cls.defaults.keys()}

if os.path.exists(conffp):
	CONF.load(conffp)
else:
	CONF.loads({})
	CONF.dump(conffp)

DISPLAY=pyglet.canvas.get_display()#It took ages to find these functions, so don't question them.
SCREEN=DISPLAY.get_default_screen()
WIDTH=SCREEN.width
HEIGHT=SCREEN.height
WIDTH2=WIDTH/2
HEIGHT2=HEIGHT/2
HEIGHT4=HEIGHT/4
BTNHEIGHT=HEIGHT/15
BTNWIDTH=WIDTH/10
BTNHEIGHT2=BTNHEIGHT/2
BTNWIDTH2=BTNWIDTH/2
ANCHORSy=("bottom","center","top")
ANCHORSx=("left","center","right")
print(f"initialized screen with size {WIDTH}x{HEIGHT}")

TIME=time()
TIMEC=0
DTIME=0
print(f"initialized time {TIME}")

class ENTCONTAINER:#base class for all entity containers
	@classmethod
	def draw(cls,*args,**kwargs):
		for ent in cls.all():
			if ent:
				ent.draw(*args,**kwargs)

class LABELS(ENTCONTAINER):
	fps=None
	ups=None
	@classmethod
	def all(cls):
		yield cls.fps
		yield cls.ups

class BTNS(ENTCONTAINER):
	#menu
	start=None#also in gmselect
	sett=None
	#generic back & cancle buttons
	back=None
	cancle=None
	#settings
	fullscr=None
	showfps=None
	vsync=None
	#game mode select
	mode=None
	#while in game
	pause=None
	@classmethod
	def all(cls):
		yield cls.start
		yield cls.sett
		yield cls.cancle
		yield cls.back
		yield cls.fullscr
		yield cls.showfps
		yield cls.vsync
		yield cls.mode
		yield cls.pause

class PHYS(ENTCONTAINER):#physical objects
	walls=[]
	char=None
	@classmethod
	def all(cls):
		return (*cls.walls,cls.char)

class MISCE(ENTCONTAINER):#miscellanious entities
	overlay=None#for pause screen
	@classmethod
	def all(cls):
		yield cls.overlay

print("initialized entity containers")
