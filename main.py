#!/usr/bin/python3
from CONSTANTS import *
import entities

class GameWin(pyglet.window.Window):
	prvscr=None#which scene was shown last frame
	curscr=0#which scene is shown
	#scenes include:
	#0 → menu
	#1 → settings
	#2 → game mode select
	fps=0#maximum fps and ups
	tc=0#how many cycles have passed since ups label has last been updated
	dt=0#how much time has passed since ups label has last been updated
	batch=None#gets renewed when scene changes
	gbatch=None#this one doesn't
	def __init__(self,*args,**kwargs):
		self.set_fps(60)
		self.batch=pyglet.graphics.Batch()
		if CONF.showfps:
			LABELS.fps=entities.Label(0,HEIGHT,0,0,"FPS:60.0",6,batch=self.gbatch)
			LABELS.ups=entities.Label(0,HEIGHT-13,0,0,"UPS:60.0",6,batch=self.gbatch)
		super().__init__(*args,**kwargs)
	def set_fps(self,fps):
		if fps!=self.fps and fps>0:
			self.fps=fps
			pyglet.clock.unschedule(self.update)
			pyglet.clock.schedule_interval(self.update,1/fps)
	def update(self,dt):#gets called every cycle, has double the importance of on_draw
		self.tc+=1
		self.dt+=dt
		if self.dt>=0.1:
			#update ups counter
			if CONF.showfps:
				LABELS.ups.setText(f"UPS:{self.tc/self.dt:.1f}/{self.fps}")
			#set tc and dt to 0
			self.tc=0
			self.dt=0
		#if scr changed, set up the scene
		if self.curscr!=self.prvscr:
			self.clear_scene(self.prvscr)
			self.construct_scene(self.curscr)
			self.prvscr=self.curscr
		#process pressed buttons
		self.pressproc(self.curscr)
	def pressproc(self,scr):
		if scr==0:
			if BTNS.back.pressed:
				print("got exit button")
				pyglet.app.exit()
			elif BTNS.sett.pressed:
				self.curscr=1
				BTNS.sett.release()
			elif BTNS.start.pressed:
				self.curscr=2
				BTNS.start.release()
		elif scr==1:
			if BTNS.back.pressed:
				CONF.fullscreen=BTNS.fullscr.pressed
				CONF.showfps=BTNS.showfps.pressed
				CONF.dump(conffp)
				print("\033[1mRESTARTING PROGRAM…\033[22m")
				self.set_fullscreen(False)#bc restarting with fullscreen on is troubeling.
				pyglet.app.exit()#closes pyglet window
				os.execv(__file__,sys.argv)#restarts the whole program to ensure applied settings
			elif BTNS.cancle.pressed:
				self.curscr=0
		elif scr==2:
			if BTNS.back.pressed:
				self.curscr=0
	def clear_scene(self,scr):
		if scr==None:
			pass
		elif scr==0:
			BTNS.back=None
			BTNS.sett=None
			BTNS.start=None
			self.batch=pyglet.graphics.Batch()
		elif scr==1:
			BTNS.back=None
			BTNS.cancle=None
			BTNS.fullscr=None
			BTNS.showfps=None
			self.batch=pyglet.graphics.Batch()
		elif scr==2:
			BTNS.back=None
			self.batch=pyglet.graphics.Batch()
		else:
			raise ValueError(f"Scene {scr} does not exist to clear")
	def construct_scene(self,scr):
		if scr==None:
			pass
		elif scr==0:
			BTNS.back=entities.Button(WIDTH2,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Exit",anch=4,key=key.ESCAPE,batch=self.batch)
			BTNS.start=entities.Button(WIDTH2,HEIGHT2,BTNWIDTH,BTNHEIGHT,"Start",anch=4,key=key.ENTER,batch=self.batch)
			BTNS.sett=entities.Button(WIDTH2,HEIGHT2-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Settings",anch=7,batch=self.batch)
		elif scr==1:
			BTNS.back=entities.Button(WIDTH-BTNWIDTH*2.5,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Save & Restart",anch=4,key=key.ENTER,batch=self.batch)
			BTNS.cancle=entities.Button(WIDTH-BTNWIDTH,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Cancle",anch=4,key=key.ESCAPE,batch=self.batch)
			BTNS.fullscr=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Borderless",pressedText="Fullscreen",anch=6,batch=self.batch)
			if CONF.fullscreen:
				BTNS.fullscr.press()
			BTNS.showfps=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT*2.5,BTNWIDTH,BTNHEIGHT,"Show FPS/UPS",pressedText="Hide FPS/UPS",anch=6,batch=self.batch)
			if CONF.showfps:
				BTNS.showfps.press()
		elif scr==2:
			BTNS.back=entities.Button(WIDTH2,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Back",anch=4,key=key.ESCAPE,batch=self.batch)
		else:
			raise ValueError(f"Scene {scr} does not exist to construct")
	def on_draw(self):#gets called on draw (duh)
		global TIME,DTIME,TIMEC
		t=time()
		DTIME+=t-TIME
		TIMEC+=1
		if DTIME>=0.1:
			if CONF.showfps:
				LABELS.fps.setText(f"FPS:{TIMEC/DTIME:.1f}/{self.fps}")
			TIMEC=0
			DTIME=0
		TIME=t
		del t
		self.clear()
		LABELS.draw()
		BTNS.draw()
		self.batch.draw()
		pyglet.clock.tick()
	def on_mouse_press(self,x,y,button,modifiers):
		if button==pgw.mouse.LEFT:
			for item in BTNS.all():
				if item:
					ret=item.checkpress(x,y)
					if ret:
						return ret
		elif button==pgw.mouse.RIGHT:
			pass
		elif button==pgw.mouse.MIDDLE:
			pass
	def on_key_press(self,symbol,modifiers):
		for item in BTNS.all():
			if item:
				ret=item.checkKey(symbol)
				if ret:
					return ret

#I don't like window borders & I have a tiling window manager so I couldn't test it anyway.
window=GameWin(
		WIDTH,HEIGHT,
		fullscreen=CONF.fullscreen,
		style=GameWin.WINDOW_STYLE_BORDERLESS,
		screen=SCREEN,
		caption="Testing Pyglet",
		vsync=True,visible=True)
window.set_location(0,0)
print(f"opened window with size {WIDTH}x{HEIGHT}")

pyglet.app.run()
