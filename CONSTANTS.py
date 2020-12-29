#!/usr/bin/python3
VERSION="0.3-dev"
print("  importing os,sys,math,json,time…")
import os,sys,math
import json
from time import time
print("  importing pyglet…")
import pyglet
import pyglet.window as pgw

if getattr(sys, 'frozen', False):
	curdir=os.path.abspath(os.path.dirname(sys.executable))
else:
	curdir=os.path.abspath(os.path.dirname(__file__))

print(f"  running in {curdir}, with arguments {sys.argv}")

conffp=os.path.join(curdir,"conf.json")
datafp=os.path.join(curdir,"data")
lvlfp=os.path.join(curdir,"levels")

print("  loading config…")
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
		print(f"    loaded config from {fp}")
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

print("  opening window…")
class Window(pgw.Window):
	def set_game(self,game):
		self.game=game
	def set_containers(self,LABELS,BTNS,PHYS,MISCE):
		self.LABELS=LABELS
		self.BTNS=BTNS
		self.PHYS=PHYS
		self.MISCE=MISCE
	def on_draw(self):#gets called on draw (duh)
		global TIME,DTIME,TIMEC
		t=time()
		DTIME+=t-TIME
		TIMEC+=1
		if DTIME>=0.1:
			if self.LABELS.fps:
				self.LABELS.fps.setText(f"FPS:{TIMEC/DTIME:.1f}/{self.game.fps}")
			TIMEC=0
			DTIME=0
		TIME=t
		del t
		self.clear()
		self.LABELS.draw()
		self.BTNS.draw()
		self.PHYS.draw()
		self.MISCE.draw()
		self.game.batch.draw()
		pyglet.clock.tick()
	def on_mouse_press(self,x,y,button,modifiers):
		if button==pgw.mouse.LEFT:
			for item in self.BTNS.all():
				if item:
					ret=item.checkpress(x,y)
					if ret:
						return ret
		elif button==pgw.mouse.RIGHT:
			pass
		elif button==pgw.mouse.MIDDLE:
			pass
	def on_mouse_drag(self,x,y,dx,dy,button,modifiers):
		if button==pgw.mouse.LEFT:
			for item in self.BTNS.draggable():
				ret=item.checkdrag(x,y,dx,dy)
				if ret:
					return ret
	def on_key_press(self,symbol,modifiers):
		if self.PHYS.char:
			self.PHYS.char.checkKey(symbol,True)
		for item in self.BTNS.all():
			if item:
				ret=item.checkKey(symbol)
				if ret:
					return ret
	def on_key_release(self,symbol,modifiers):
		if self.PHYS.char:
			self.PHYS.char.checkKey(symbol,False)

DISPLAY=pyglet.canvas.get_display()#It took ages to find these functions, so don't question them.
SCREEN=DISPLAY.get_default_screen()

window=Window(
		fullscreen=CONF.fullscreen,
		style=pgw.Window.WINDOW_STYLE_BORDERLESS,
		screen=SCREEN,
		caption=f"Dodge to Drums {VERSION}",
		vsync=CONF.vsync,
		visible=True)#invisible windows sometimes get ignored from certain stuff I need here

if not CONF.fullscreen:
	window.maximize()

#enable transparency
pyglet.gl.glEnable(pyglet.gl.GL_BLEND)

print("  defining constants…")
WIDTH,HEIGHT=window.get_size()
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
SIZE20=SIZE/20
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
print(f"  window has a size of {WIDTH}x{HEIGHT}")

TIME=time()
TIMEC=0
DTIME=0

print("  initializing OpenGL groups…")
GRbg=pyglet.graphics.OrderedGroup(0)#background
GRmp=pyglet.graphics.OrderedGroup(1)#midpoint (widgets, objects)
GRfb=pyglet.graphics.OrderedGroup(2)#fore-back-ground – for backgrounds that want to overlap game sprites but not labels
GRfg=pyglet.graphics.OrderedGroup(3)#foreground (labels)
GRobg=pyglet.graphics.OrderedGroup(4)#overlay background
GRomp=pyglet.graphics.OrderedGroup(5)#overlay midpoint (overlay widgets)
GRofg=pyglet.graphics.OrderedGroup(6)#overlay foreground (overlay labels)
GRs=[GRbg,GRmp,GRfb,GRfg,GRobg,GRomp,GRofg]
