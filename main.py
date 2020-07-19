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
	#3 → the game itself
	fps=0#maximum fps and ups
	tc=0#how many cycles have passed since ups label has last been updated
	dt=0#how much time has passed since ups label has last been updated
	batch=None#gets renewed when scene changes
	gbatch=None#this one doesn't
	diffmode=1#difficulty mode
	paused=False
	def __init__(self,*args,**kwargs):
		self.set_fps(60)
		self.batch=pyglet.graphics.Batch()
		self.gbatch=pyglet.graphics.Batch()
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
			if LABELS.ups:
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
		#cycle all physical objects that need cycling
		if PHYS.char and not self.paused:
			PHYS.char.cycle()
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
				self.curscr=0
			elif BTNS.cancle.pressed:
				self.curscr=0
		elif scr==2:
			if BTNS.back.pressed:
				self.curscr=0
				self.diffmode=BTNS.mode.getSelected()
			elif BTNS.start.pressed:
				self.curscr=3
				self.diffmode=BTNS.mode.getSelected()
		elif scr==3:
			if BTNS.pause.pressed:
				self.paused=not self.paused
				BTNS.pause.release()
				if self.paused:
					#to ensure that the button only shows up when paused and vanishes afterwards, it has to have no batch attached
					BTNS.back=entities.Button(WIDTH2,HEIGHT-HEIGHT4,BTNWIDTH,BTNHEIGHT,"Exit",anch=4,batch=None)
				else:
					BTNS.back=None
			elif BTNS.back and BTNS.back.pressed:
				self.curscr=0
				self.paused=False
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
			LABELS.notice=None
			BTNS.fullscr=None
			BTNS.showfps=None
			BTNS.vsync=None
			self.batch=pyglet.graphics.Batch()
		elif scr==2:
			BTNS.back=None
			BTNS.mode=None
			BTNS.start=None
			self.batch=pyglet.graphics.Batch()
		elif scr==3:
			PHYS.walls.clear()
			PHYS.char=None
			MISCE.overlay=None
			BTNS.pause=None
			BTNS.back=None
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
			BTNS.back=entities.Button(WIDTH-BTNWIDTH*2.5,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Save",anch=4,key=key.ENTER,batch=self.batch)
			BTNS.cancle=entities.Button(WIDTH-BTNWIDTH,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Cancle",anch=4,key=key.ESCAPE,batch=self.batch)
			LABELS.notice=entities.Label(5,BTNHEIGHT2,0,0,"Restart the game to fully apply the settings",anch=0,batch=self.batch)
			BTNS.fullscr=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Borderless",pressedText="Fullscreen",anch=6,batch=self.batch)
			if CONF.fullscreen:
				BTNS.fullscr.press()
			BTNS.showfps=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT*2.5,BTNWIDTH,BTNHEIGHT,"Show FPS/UPS",pressedText="Hide FPS/UPS",anch=6,batch=self.batch)
			if CONF.showfps:
				BTNS.showfps.press()
			BTNS.vsync=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT*4,BTNWIDTH,BTNHEIGHT,"Vsync OFF",pressedText="Vsync ON",anch=6,batch=self.batch)
			if CONF.vsync:
				BTNS.vsync.press()
		elif scr==2:
			BTNS.back=entities.Button(WIDTH2,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Back",anch=4,key=key.ESCAPE,batch=self.batch)
			BTNS.start=entities.Button(WIDTH2,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Start",anch=4,key=key.ENTER,batch=self.batch)
			BTNS.mode=entities.RadioList(WIDTH2,HEIGHT2,BTNWIDTH,BTNHEIGHT*3,["Normal","Normal","also Normal lol"],selected=self.diffmode,anch=1,batch=self.batch)
		elif scr==3:
			BTNS.pause=entities.Button(0,0,0,0,"",0,key=key.ESCAPE,batch=self.batch)
			PHYS.walls.append(entities.Wall(0,0,WIDTH,HEIGHT4,(128,128,128,255)))
			PHYS.char=entities.Hooman(WIDTH2,HEIGHT2,BTNWIDTH2,BTNHEIGHT*2,(64,64,255,255))
			PHYS.char.set_floor(HEIGHT4)
			MISCE.overlay=entities.Overlay(0,0,WIDTH,HEIGHT,(0,0,0,64))
		else:
			raise ValueError(f"Scene {scr} does not exist to construct")
	def on_draw(self):#gets called on draw (duh)
		global TIME,DTIME,TIMEC
		t=time()
		DTIME+=t-TIME
		TIMEC+=1
		if DTIME>=0.1:
			if LABELS.fps:
				LABELS.fps.setText(f"FPS:{TIMEC/DTIME:.1f}/{self.fps}")
			TIMEC=0
			DTIME=0
		TIME=t
		del t
		self.clear()
		LABELS.draw()
		BTNS.draw()
		phbatch=pyglet.graphics.Batch()
		PHYS.draw(phbatch)
		phbatch.draw()
		if self.paused:
			MISCE.overlay.draw()
		self.gbatch.draw()
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
		if PHYS.char:
			PHYS.char.checkKey(symbol,True)
		for item in BTNS.all():
			if item:
				ret=item.checkKey(symbol)
				if ret:
					return ret
	def on_key_release(self,symbol,modifiers):
		if PHYS.char:
			PHYS.char.checkKey(symbol,False)

#I don't like window borders & I have a tiling window manager so I couldn't test it anyway.
window=GameWin(
		WIDTH,HEIGHT,
		fullscreen=CONF.fullscreen,
		style=GameWin.WINDOW_STYLE_BORDERLESS,
		screen=SCREEN,
		caption="Dodge to Drums",
		vsync=CONF.vsync,
		visible=True)
window.set_location(0,0)

#enable transparency
pyglet.gl.glEnable(pyglet.gl.GL_BLEND)

print(f"opened window with size {WIDTH}x{HEIGHT}")

pyglet.app.run()
