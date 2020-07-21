#!/usr/bin/python3
print("started")
import os,sys
import json
import pyglet
from pyglet.window import key
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

class CONF:
	defaults={"fullscreen":True,"showfps":True,"vsync":True}
	@classmethod
	def load(cls,fp):
		with open(fp,"r") as f:
			data=json.load(f)
		cls.loads(data)
		print(f"loaded config from {fp}:\n {data}")
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
		print(f"dumped config to {fp}")
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
SIZE=(WIDTH+HEIGHT)/2#for scaling stuff where the aspect ratio shouldn't be changed but the size should
ANCHORSy=("bottom","center","top")
ANCHORSx=("left","center","right")
print(f"initialized screen with size {WIDTH}x{HEIGHT}")

TIME=time()
TIMEC=0
DTIME=0

GRbg=pyglet.graphics.OrderedGroup(0)#background
GRmp=pyglet.graphics.OrderedGroup(1)#midpoint (widgets, objects)
GRfg=pyglet.graphics.OrderedGroup(2)#foreground (labels)
GRobg=pyglet.graphics.OrderedGroup(3)#overlay background
GRomp=pyglet.graphics.OrderedGroup(4)#overlay midpoint (overlay widgets)
GRofg=pyglet.graphics.OrderedGroup(5)#overlay foreground (overlay labels)
GRs=[GRbg,GRmp,GRfg,GRobg,GRomp,GRofg]
print(f"Initialized OpenGL groups")
