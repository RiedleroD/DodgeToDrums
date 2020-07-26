#!/usr/bin/python3
from CONSTANTS import *
import entities
from containers import LABELS,BTNS,PHYS,MISCE,MEDIA

class GameWin(pyglet.window.Window):
	prvscr=None#which scene was shown last frame
	curscr=0#which scene is shown
	#scenes include:
	#0 → menu
	#1 → settings
	#2 → game mode select
	#3 → the game itself
	#4 → credits
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
		if CONF.showfps:
			LABELS.fps=entities.Label(0,HEIGHT,WIDTH/15,19,"FPS:60.0",6,bgcolor=(0,0,0,255),batch=self.batch,group=GRofg)
			LABELS.ups=entities.Label(0,HEIGHT-19,WIDTH/15,19,"UPS:60.0",6,bgcolor=(0,0,0,255),batch=self.batch,group=GRofg)
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
		if not self.paused:
			#cycle all physical objects that need cycling
			if PHYS.char:
				PHYS.char.cycle()
			for bullet in PHYS.bullets:
				bullet.cycle()
			#remove all dead or out-of range physical objects
			for i in range(len(PHYS.bullets)-1,-1,-1):
				bullet=PHYS.bullets[i]
				if bullet.x>WIDTH or bullet.x+bullet.w<0 or bullet.y>HEIGHT or bullet.y+bullet.h<0:
					del PHYS.bullets[i]
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
			elif BTNS.creds.pressed:
				BTNS.creds.release()
				self.curscr=4
		elif scr==1:
			if BTNS.back.pressed:
				CONF.fullscreen=BTNS.fullscr.pressed
				CONF.showfps=BTNS.showfps.pressed
				CONF.showcoll=BTNS.showcoll.pressed
				for btn in BTNS.strg:
					setattr(CONF,f"k_{btn.btxt}",btn.val)
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
					BTNS.back=entities.Button(WIDTH2,HEIGHT-HEIGHT4,BTNWIDTH,BTNHEIGHT,"Exit",anch=4,batch=self.batch,group=GRomp)
				else:
					BTNS.back=None
			elif BTNS.back and BTNS.back.pressed:
				self.curscr=0
				self.paused=False
		elif scr==4:
			if BTNS.back.pressed:
				self.curscr=0
	def clear_scene(self,scr):
		if scr==None:
			pass
		elif scr==0:
			BTNS.back=None
			BTNS.sett=None
			BTNS.start=None
			BTNS.creds=None
			MISCE.menubg=None
		elif scr==1:
			BTNS.back=None
			BTNS.cancle=None
			LABELS.notice=None
			BTNS.fullscr=None
			BTNS.showfps=None
			BTNS.vsync=None
			BTNS.showcoll=None
			BTNS.strg.clear()
			MISCE.menubg=None
		elif scr==2:
			BTNS.back=None
			BTNS.mode=None
			BTNS.start=None
			MISCE.menubg=None
		elif scr==3:
			PHYS.walls.clear()
			PHYS.bullets.clear()
			PHYS.char=None
			MISCE.overlay=None
			BTNS.pause=None
			BTNS.back=None
		elif scr==4:
			BTNS.back=None
			LABELS.creds.clear()
		else:
			raise ValueError(f"Scene {scr} does not exist to clear")
	def construct_scene(self,scr):
		if scr==None:
			pass
		elif scr==0:
			BTNS.back=entities.Button(WIDTH2,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Exit",anch=4,key=k_BACK,batch=self.batch,group=GRmp)
			BTNS.start=entities.Button(WIDTH2,HEIGHT2,BTNWIDTH,BTNHEIGHT,"Start",anch=4,key=k_OK,batch=self.batch,group=GRmp)
			BTNS.sett=entities.Button(WIDTH2,HEIGHT2-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Settings",anch=7,batch=self.batch,group=GRmp)
			BTNS.creds=entities.Button(WIDTH2,HEIGHT2-BTNHEIGHT*2.5,BTNWIDTH,BTNHEIGHT,"Credits",anch=7,batch=self.batch,group=GRmp)
			MISCE.menubg=entities.Background(0,0,WIDTH,HEIGHT,(0,0,0,255),tex=MEDIA.menu,batch=self.batch,group=GRbg)
		elif scr==1:
			BTNS.back=entities.Button(WIDTH-BTNWIDTH*2.5,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Save",anch=4,key=k_OK,batch=self.batch,group=GRmp)
			BTNS.cancle=entities.Button(WIDTH-BTNWIDTH,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Cancle",anch=4,key=k_BACK,batch=self.batch,group=GRmp)
			LABELS.notice=entities.Label(5,BTNHEIGHT2,0,0,"Restart the game to fully apply the settings",anch=0,batch=self.batch,group=GRfg)
			BTNS.fullscr=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Borderless",pressedText="Fullscreen",anch=6,batch=self.batch,group=GRmp)
			if CONF.fullscreen:
				BTNS.fullscr.press()
			BTNS.showfps=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT*2.5,BTNWIDTH,BTNHEIGHT,"Show FPS/UPS",pressedText="Hide FPS/UPS",size=12,anch=6,batch=self.batch,group=GRmp)
			if CONF.showfps:
				BTNS.showfps.press()
			BTNS.vsync=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT*4,BTNWIDTH,BTNHEIGHT,"Vsync OFF",pressedText="Vsync ON",anch=6,batch=self.batch,group=GRmp)
			if CONF.vsync:
				BTNS.vsync.press()
			BTNS.showcoll=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT*5.5,BTNWIDTH,BTNHEIGHT,"Hide Collision Boxes",pressedText="Show Collision Boxes",size=10,anch=6,batch=self.batch,group=GRmp)
			if CONF.showcoll:
				BTNS.showcoll.press()
			BTNS.strg+=[
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"UP",CONF.k_UP,anch=6,batch=self.batch,group=GRmp),
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT*2.5,BTNWIDTH,BTNHEIGHT,"DOWN",CONF.k_DOWN,anch=6,batch=self.batch,group=GRmp),
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT*4,BTNWIDTH,BTNHEIGHT,"LEFT",CONF.k_LEFT,anch=6,batch=self.batch,group=GRmp),
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT*5.5,BTNWIDTH,BTNHEIGHT,"RIGHT",CONF.k_RIGHT,anch=6,batch=self.batch,group=GRmp),
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT*7,BTNWIDTH,BTNHEIGHT,"OK",CONF.k_OK,anch=6,batch=self.batch,group=GRmp),
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT*8.5,BTNWIDTH,BTNHEIGHT,"BACK",CONF.k_BACK,anch=6,batch=self.batch,group=GRmp)]
			MISCE.menubg=entities.Background(0,0,WIDTH,HEIGHT,(0,0,0,255),tex=MEDIA.menu,batch=self.batch,group=GRbg)
		elif scr==2:
			BTNS.back=entities.Button(WIDTH2,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Back",anch=4,key=k_BACK,batch=self.batch,group=GRmp)
			BTNS.start=entities.Button(WIDTH2,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Start",anch=4,key=k_OK,batch=self.batch,group=GRmp)
			BTNS.mode=entities.RadioList(WIDTH2,HEIGHT2,BTNWIDTH,BTNHEIGHT*3,["Normal","Normal","also Normal lol"],selected=self.diffmode,anch=1,batch=self.batch,group=GRmp)
			MISCE.menubg=entities.Background(0,0,WIDTH,HEIGHT,(0,0,0,255),tex=MEDIA.menu,batch=self.batch,group=GRbg)
		elif scr==3:
			BTNS.pause=entities.Button(0,0,0,0,"",0,key=k_BACK,batch=self.batch,group=GRmp)
			PHYS.char=entities.Hooman(WIDTH2,HEIGHT2,SIZE/15,SIZE/12.5,(64,64,255,255),self.batch,group=GRmp)
			PHYS.char.set_boundaries(WIDTH,HEIGHT)
			MISCE.overlay=entities.Overlay(0,0,WIDTH,HEIGHT,(0,0,0,64),batch=self.batch,group=GRobg)
		elif scr==4:
			BTNS.back=entities.Button(WIDTH-BTNWIDTH,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Back",anch=4,key=k_BACK,batch=self.batch,group=GRmp)
			LABELS.creds+=[
				entities.Label(BTNWIDTH2,HEIGHT-BTNHEIGHT,0,0,"Programming:",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH,HEIGHT-BTNHEIGHT*1.5,0,0,"Riedler",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH2,HEIGHT-BTNHEIGHT*2,0,0,"Graphics:",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH,HEIGHT-BTNHEIGHT*2.5,0,0,"Dark Rosemary",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH2,HEIGHT-BTNHEIGHT*3,0,0,"Testing:",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH,HEIGHT-BTNHEIGHT*3.5,0,0,"Andreas S.",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH,HEIGHT-BTNHEIGHT*4,0,0,"Philip D.",anch=6,batch=self.batch,group=GRfg)]
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
		if MISCE.overlay:
			if self.paused:
				MISCE.overlay.show()
			else:
				MISCE.overlay.hide()
		LABELS.draw()
		BTNS.draw()
		PHYS.draw()
		MISCE.draw()
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
			if self.curscr==3:
				PHYS.bullets.append(entities.Bullet1(x,y,SIZE/32,SIZE/13,PHYS.char,60,(255,0,0,255),MEDIA.bullet1,1,batch=self.batch,group=GRmp))
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
