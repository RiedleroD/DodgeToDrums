#!/usr/bin/python3
print("started")
VERSION="0.3-dev"
import os,sys,math
import json
import pyglet
import pyglet.window as pgw
from time import time
print("imported libraries")

if getattr(sys, 'frozen', False):
	curdir=os.path.abspath(os.path.dirname(sys.executable))
else:
	curdir=os.path.abspath(os.path.dirname(__file__))

print(f"started in dir {curdir} with arguments {sys.argv}")

conffp=os.path.join(curdir,"conf.json")
datafp=os.path.join(curdir,"data")
lvlfp=os.path.join(curdir,"levels")

class CONF:
	defaults={"fullscreen":True,"showfps":True,"vsync":True,"showcoll":False,"volmaster":1,"volmusic":0.8,"volsfx":0.5}
	defstrg={
		"LEFT":pgw.key.A,
		"RIGHT":pgw.key.D,
		"UP":pgw.key.W,
		"DOWN":pgw.key.S,
		"CROUCH":pgw.key.LSHIFT,
		"BACK":pgw.key.ESCAPE,
		"OK":pgw.key.ENTER,
		"SHOOT":pgw.key.SPACE}
	@classmethod
	def load(cls,fp):
		with open(fp,"r") as f:
			data=json.load(f)
		cls.loads(data)
		print(f"loaded config from {fp}")
	@classmethod
	def loads(cls,data):
		for sett, default in cls.defaults.items():
			if sett in data:
				val=data[sett]
			else:
				val=default
			setattr(cls,sett,val)
		if "strg" not in data:
			data["strg"]={}
		dats=data["strg"]
		for strg,default in cls.defstrg.items():
			if strg in dats:
				val=dats[strg]
			else:
				val=default
			setattr(cls,f"k_{strg}",val)
			globals()[f"k_{strg}"]=val
	@classmethod
	def dump(cls,fp):
		with open(fp,"w+") as f:
			json.dump(cls.dumps(),f)
		print(f"dumped config to {fp}")
	@classmethod
	def dumps(cls):
		result={name:getattr(cls,name) for name in cls.defaults.keys()}
		result["strg"]={name:getattr(cls,f"k_{name}") for name in cls.defstrg.keys()}
		return result

if os.path.exists(conffp):
	CONF.load(conffp)
else:
	CONF.loads({})
	CONF.dump(conffp)

DISPLAY=pyglet.canvas.get_display()#It took ages to find these functions, so don't question them.
SCREEN=DISPLAY.get_default_screen()

_win=pgw.Window(
		fullscreen=CONF.fullscreen,
		style=pgw.Window.WINDOW_STYLE_BORDERLESS,
		screen=SCREEN,
		caption="Dodge to Drums",
		vsync=CONF.vsync,
		visible=True)#invisible windows sometimes get ignored from certain stuff I need here

if not CONF.fullscreen:
	_win.maximize()

WIDTH,HEIGHT=_win.get_size()
_win.close()
WIDTH2=WIDTH/2
WIDTH3=WIDTH/3
WIDTH20=WIDTH/20
HEIGHT2=HEIGHT/2
HEIGHT4=HEIGHT/4
HEIGHT10=HEIGHT/10
BTNHEIGHT=HEIGHT/15
BTNWIDTH=WIDTH/10
BTNHEIGHT2=BTNHEIGHT/2
BTNWIDTH2=BTNWIDTH/2
SIZE=(WIDTH+HEIGHT)/2#for scaling stuff where the aspect ratio shouldn't be changed but the size should
GBGw=5*WIDTH/6
GBGx=WIDTH/12
GBG_x=11*WIDTH/12
GBGh=3*HEIGHT/4
GBGy=HEIGHT/4
GBG_y=HEIGHT
GBGh10=GBGh/10
GBGw20=GBGw/20
ANCHORSy=("bottom","center","top")
ANCHORSx=("left","center","right")
print(f"initialized screen with size {WIDTH}x{HEIGHT}")

TIME=time()
TIMEC=0
DTIME=0

GRbg=pyglet.graphics.OrderedGroup(0)#background
GRmp=pyglet.graphics.OrderedGroup(1)#midpoint (widgets, objects)
GRfb=pyglet.graphics.OrderedGroup(2)#fore-back-ground – for backgrounds that want to overlap game sprites but not labels
GRfg=pyglet.graphics.OrderedGroup(3)#foreground (labels)
GRobg=pyglet.graphics.OrderedGroup(4)#overlay background
GRomp=pyglet.graphics.OrderedGroup(5)#overlay midpoint (overlay widgets)
GRofg=pyglet.graphics.OrderedGroup(6)#overlay foreground (overlay labels)
GRs=[GRbg,GRmp,GRfg,GRobg,GRomp,GRofg]
print(f"Initialized OpenGL groups")
