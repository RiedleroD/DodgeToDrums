#!/usr/bin/python3
from CONSTANTS import *
import entities

class GameWin(pyglet.window.Window):
	prvscr=None#which scene was shown last frame
	curscr=0#which scene is shown
	#scenes include:
	#0 → menu
	fps=0#maximum fps and ups
	tc=0#how many cycles have passed since ups label has last been updated
	dt=0#how much time has passed since ups label has last been updated
	batch=None
	def __init__(self,*args,**kwargs):
		self.set_fps(60)
		self.batch=pyglet.graphics.Batch()
		LABELS.fps=entities.Label(0,HEIGHT,0,0,"FPS:60",6,batch=self.batch)
		LABELS.ups=entities.Label(0,HEIGHT-13,0,0,"UPS:60",6,batch=self.batch)
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
			LABELS.ups.setText("UPS:%02i/%02i"%(round(self.tc/self.dt),self.fps))
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
			if BTNS.exit.pressed:
				print("got exit button")
				quit()
	def clear_scene(self,scr):
		if scr==None:
			pass
		elif scr==0:
			BTNS.exit=None
		else:
			raise ValueError(f"Scene {scr} does not exist to clear")
	def construct_scene(self,scr):
		if scr==None:
			pass
		elif scr==0:
				BTNS.exit=entities.Button(WIDTH2,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Exit",1,key=key.ESCAPE)
		else:
			raise ValueError(f"Scene {scr} does not exist to construct")
	def on_draw(self):#gets called on draw (duh)
		global TIME,DTIME,TIMEC
		t=time()
		DTIME+=t-TIME
		TIMEC+=1
		if DTIME>=0.1:
			LABELS.fps.setText("FPS:%02i/%02i"%(round(TIMEC/DTIME),self.fps))
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

config = pyglet.gl.Config(sample_buffers=1, samples=4)#just to make the graphics a little crisper, maybe a setting gets added later that lets control the sample size
#I don't like window borders & I have a tiling window manager so I couldn't test it anyway.
window=GameWin(
		WIDTH,HEIGHT,
		fullscreen=True,#TODO: add option to en/disable fullscreen
		style=GameWin.WINDOW_STYLE_BORDERLESS,
		screen=SCREEN,
		caption="Testing Pyglet",
		config=config,
		vsync=True,visible=True)
window.set_location(0,0)
print(f"opened window with size {WIDTH}x{HEIGHT}")

pyglet.app.run()
