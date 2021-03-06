#!/usr/bin/python3
print("importing constants…")
from CONSTANTS import *
print("importing entities…")
import entities
print("importing containers…")
from containers import LABELS,BTNS,PHYS,MISCE,MEDIA,LVLS

print("defining main game class…")

class Game(pyglet.window.Window):
	prvscr=None#which scene was shown last frame
	curscr=0#which scene is shown
	#scenes include:
	#0 → menu
	#1 → settings
	#2 → game mode select
	#3 → the game itself
	#4 → credits
	#5 → level select
	#6 → error screen
	fps=0#maximum fps and ups
	tc=0#how many cycles have passed since ups label has last been updated
	dt=0#how much time has passed since ups label has last been updated
	batch=None#gets renewed when scene changes
	gbatch=None#this one doesn't
	diffmode=1#difficulty mode
	paused=False
	lv=None
	curt=0#current time, used for spawning and cycling in the main game
	def __init__(self,win):
		self.window=win
		self.set_fps(60)
		self.batch=pyglet.graphics.Batch()
		if CONF.showfps:
			LABELS.fps=entities.Label(0,HEIGHT,WIDTH/15,19,"FPS:60.0",6,bgcolor=(0,0,0,255),batch=self.batch,group=GRofg)
			LABELS.ups=entities.Label(0,HEIGHT-19,WIDTH/15,19,"UPS:60.0",6,bgcolor=(0,0,0,255),batch=self.batch,group=GRofg)
		win.set_game(self)
		if MEDIA.errs:
			self.curscr=self.prvscr=6#to prevent startup initialisation
			BTNS.back=entities.Button(0,0,0,0,"",key=k_BACK,batch=self.batch,group=GRmp)
			for i,err in enumerate(MEDIA.errs):
				setattr(LABELS,f"err{i}",entities.Label(0,20*i,0,0,err,batch=self.batch,group=GRfg))
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
		#in-game stuff
		if self.curscr==3:
			if self.paused==True:
				MISCE.overlay.show()
			else:
				MISCE.overlay.hide()
			if not self.paused:
				#cycle all physical objects that need cycling
				PHYS.char.cycle(self.curt)
				for bullet in PHYS.bullets:
					bullet.cycle(self.curt)
				for heart in LABELS.lives:
					heart.cycle(self.curt)
				if LABELS.lives[-1].dead:
					LABELS.lives.pop()
				self.check_projectiles()
				#execute all acts
				if self.lv:
					self.exec_acts()
			elif self.paused==2:#while dying
				for heart in LABELS.lives:
					heart.cycle(0)
				if LABELS.lives and LABELS.lives[-1].dead:
					LABELS.lives.pop()
				PHYS.char.cycle(0)
				if PHYS.char.dead:
					self.curscr=5#return to main menu if char dead
		#only if no scene change is due
		if self.curscr==self.prvscr:
			#process pressed buttons
			self.pressproc(self.curscr)
	def check_projectiles(self):
		#remove all expired projectiles
		for i in range(len(PHYS.bullets)-1,-1,-1):
			bullet=PHYS.bullets[i]
			if bullet.dead:
				if bullet.explosive:
					PHYS.bullets.append(entities.Explosion(bullet.x,bullet.y,SIZE/16,SIZE/16,MEDIA.explosion,self.curt,batch=self.batch,group=GRmp))
				del PHYS.bullets[i]
			elif bullet.despawn:
				x,y,_x,_y=bullet.get_poss()
				if x>GBG_x or _x<GBGx or y>GBG_y or _y<GBGy:
					del PHYS.bullets[i]
		#check if main char got hit
		x,y,_x,_y=PHYS.char.get_poss()
		for blt in PHYS.bullets:
			if blt.deadly and blt.doesCollide(x,y,_x,_y):
				if PHYS.char.lose_life():
					LABELS.lives[-1].die()
					self.lv.fade_in(1)
				break
		if PHYS.char.lives<=0:
			self.paused=2#paused as far as everything is concerned, but human still cycles.
			self.lv.stop()
	def exec_acts(self):
		acts,curt=self.lv.cycle()
		self.curt=curt
		for act in acts:
			name=act.pop(0)
			if name=="knife":
				x,y,wait=act
				PHYS.bullets.append(entities.DirectedMissile(GBGw20*x+GBGx-SIZE/64,GBGh10*y+GBGy-SIZE/26,SIZE/32,SIZE/13,PHYS.char,self.curt+wait,MEDIA.knife,curt,batch=self.batch,group=GRmp))
			elif name=="flame":
				x,y,dx,dy=act
				PHYS.bullets.append(entities.ProjectileRot(GBGw20*x+GBGx-SIZE/52,GBGh10*y+GBGy-SIZE/30,SIZE/26,SIZE/15,entities.Point(GBGx+GBGw20*dx,GBGy+GBGh10*dy),MEDIA.flame_big,curt,batch=self.batch,group=GRmp))
			elif name=="flame2":
				x,y,exp=act
				PHYS.bullets.append(entities.HomingMissile(GBGw20*x+GBGx-SIZE/64,GBGh10*y+GBGy-SIZE/26,SIZE/32,SIZE/13,PHYS.char,self.curt+exp,MEDIA.flame_smol,curt,batch=self.batch,group=GRmp))
			elif name=="bomb":
				x,y,dx,dy,exp=act
				PHYS.bullets.append(entities.Bomb(GBGw20*x+GBGx-SIZE/32,GBGh10*y+GBGy-SIZE/32,SIZE/16,SIZE/16,entities.Point(GBGx+GBGw20*dx,GBGy+GBGh10*dy),MEDIA.bomb,curt,curt+exp,batch=self.batch,group=GRmp))
			elif name=="stop":
				self.curscr=5
			else:
				print(f"\033[33mWarning:\033[39m tried to spawn unknown enemy \"{name}\" with arguments {act}")
	def pressproc(self,scr):
		if scr==None:#exit the game
			print("WARNING: extra cycle after closing the game")
		elif scr==0:#main menu
			if BTNS.back.pressed:
				print("got exit button")
				self.curscr=None
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
		elif scr==1:#settings
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
			elif BTNS.volmaster.pressed:
				CONF.volmaster=BTNS.volmaster.perc
				BTNS.volmaster.release()
				self.mus.volume=CONF.volmaster*CONF.volmusic
			elif BTNS.volmusic.pressed:
				CONF.volmusic=BTNS.volmusic.perc
				BTNS.volmusic.release()
				self.mus.volume=CONF.volmaster*CONF.volmusic
			elif BTNS.volsfx.pressed:
				CONF.volsfx=BTNS.volsfx.perc
				BTNS.volsfx.release()
		elif scr==2:#difficulty selection
			if BTNS.back.pressed:
				self.curscr=0
				self.diffmode=BTNS.mode.getSelected()
			elif BTNS.start.pressed:
				self.curscr=5
				self.diffmode=BTNS.mode.getSelected()
		elif scr==3:#game
			if self.mus:
				self.mus.next_source()
				self.mus.delete()
				self.mus=None
			if BTNS.pause.pressed:
				BTNS.pause.release()
				if self.paused!=2:
					self.paused=not self.paused
					if self.paused:
						BTNS.back=entities.Button(WIDTH2,HEIGHT-HEIGHT4,BTNWIDTH,BTNHEIGHT,"Exit",anch=4,batch=self.batch,group=GRomp)
					else:
						BTNS.back=None
					self.lv.pause()
			elif BTNS.back and BTNS.back.pressed:
				self.curscr=5
		elif scr==4:#credits
			if BTNS.back.pressed:
				self.curscr=0
		elif scr==5:#level selection
			if BTNS.back.pressed:
				self.curscr=2
				LVLS.curlv=BTNS.lvls.curlv
			elif BTNS.lvls.pressed:
				self.curscr=3
				LVLS.curlv=BTNS.lvls.curlv
		elif scr==6:#error screen
			if BTNS.back.pressed:
				pyglet.app.exit()
	def clear_scene(self,scr):
		if scr==None:#at startup
			self.mus=MEDIA.menubgm.play()
			self.mus.loop=True
			self.mus.volume=CONF.volmaster*CONF.volmusic
		elif scr==0:
			BTNS.back=None
			BTNS.sett=None
			BTNS.start=None
			BTNS.creds=None
			MISCE.bg=None
		elif scr==1:
			BTNS.back=None
			BTNS.cancle=None
			LABELS.notice=None
			BTNS.fullscr=None
			BTNS.showfps=None
			BTNS.vsync=None
			BTNS.showcoll=None
			BTNS.strg.clear()
			BTNS.volmaster=None
			BTNS.volmusic=None
			BTNS.volsfx=None
			MISCE.bg=None
			LABELS.version=None
		elif scr==2:
			BTNS.back=None
			BTNS.mode=None
			BTNS.start=None
			MISCE.bg=None
		elif scr==3:
			self.lv.stop()
			self.lv=None
			self.paused=False
			LABELS.lives.clear()
			PHYS.bullets.clear()
			PHYS.char=None
			MISCE.overlay=None
			BTNS.pause=None
			BTNS.back=None
			MISCE.bg=None
			self.mus=MEDIA.menubgm.play()
			self.mus.loop=True
			self.mus.volume=CONF.volmaster*CONF.volmusic
		elif scr==4:
			BTNS.back=None
			LABELS.creds.clear()
		elif scr==5:
			BTNS.lvls=None
			BTNS.back=None
		else:
			raise ValueError(f"Scene {scr} does not exist to clear")
	def construct_scene(self,scr):
		if scr==None:#at shutdown
			if self.mus:
				self.mus.next_source()
				self.mus.delete()
				self.mus=None
		elif scr==0:
			BTNS.back=entities.Button(WIDTH2,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Exit",anch=4,key=k_BACK,batch=self.batch,group=GRmp)
			BTNS.start=entities.Button(WIDTH2,HEIGHT2,BTNWIDTH,BTNHEIGHT,"Start",anch=4,key=k_OK,batch=self.batch,group=GRmp)
			BTNS.sett=entities.Button(WIDTH2,HEIGHT2-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Settings",anch=7,batch=self.batch,group=GRmp)
			BTNS.creds=entities.Button(WIDTH2,HEIGHT2-BTNHEIGHT*2.5,BTNWIDTH,BTNHEIGHT,"Credits",anch=7,batch=self.batch,group=GRmp)
			MISCE.bg=entities.Background(0,0,WIDTH,HEIGHT,(0,0,0,255),tex=MEDIA.menu,batch=self.batch,group=GRbg)
		elif scr==1:
			BTNS.back=entities.Button(WIDTH-BTNWIDTH*2.5,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Save",anch=4,key=k_OK,batch=self.batch,group=GRmp)
			BTNS.cancle=entities.Button(WIDTH-BTNWIDTH,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Cancle",anch=4,key=k_BACK,batch=self.batch,group=GRmp)
			LABELS.notice=entities.Label(5,BTNHEIGHT2,WIDTH/4,19,"Restart the game to fully apply the settings",bgcolor=(0,0,0,255),anch=0,batch=self.batch,group=GRfg)
			LABELS.version=entities.Label(5,BTNHEIGHT2-19,WIDTH/4,19,f"version: {VERSION}",bgcolor=(0,0,0,255),anch=0,batch=self.batch,group=GRfg)
			BTNS.fullscr=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Borderless",pressedText="Fullscreen",anch=6,batch=self.batch,group=GRmp)
			if CONF.fullscreen:
				BTNS.fullscr.press(silent=True)
			BTNS.showfps=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT*2.5,BTNWIDTH,BTNHEIGHT,"Show FPS/UPS",pressedText="Hide FPS/UPS",size=12,anch=6,batch=self.batch,group=GRmp)
			if CONF.showfps:
				BTNS.showfps.press(silent=True)
			BTNS.vsync=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT*4,BTNWIDTH,BTNHEIGHT,"Vsync OFF",pressedText="Vsync ON",anch=6,batch=self.batch,group=GRmp)
			if CONF.vsync:
				BTNS.vsync.press(silent=True)
			BTNS.showcoll=entities.ButtonSwitch(0,HEIGHT-BTNHEIGHT*5.5,BTNWIDTH,BTNHEIGHT,"Hide Collision Boxes",pressedText="Show Collision Boxes",size=10,anch=6,batch=self.batch,group=GRmp)
			if CONF.showcoll:
				BTNS.showcoll.press(silent=True)
			BTNS.strg+=[
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"UP",CONF.k_UP,anch=6,batch=self.batch,group=GRmp),
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT*2.5,BTNWIDTH,BTNHEIGHT,"DOWN",CONF.k_DOWN,anch=6,batch=self.batch,group=GRmp),
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT*4,BTNWIDTH,BTNHEIGHT,"LEFT",CONF.k_LEFT,anch=6,batch=self.batch,group=GRmp),
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT*5.5,BTNWIDTH,BTNHEIGHT,"RIGHT",CONF.k_RIGHT,anch=6,batch=self.batch,group=GRmp),
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT*7,BTNWIDTH,BTNHEIGHT,"OK",CONF.k_OK,anch=6,batch=self.batch,group=GRmp),
				entities.StrgButton(BTNWIDTH*1.5,HEIGHT-BTNHEIGHT*8.5,BTNWIDTH,BTNHEIGHT,"BACK",CONF.k_BACK,anch=6,batch=self.batch,group=GRmp)]
			BTNS.volmaster=entities.Slider(WIDTH-BTNWIDTH*3.5,HEIGHT-BTNHEIGHT*2,BTNWIDTH*2,BTNHEIGHT2,"master volume",CONF.volmaster,batch=self.batch,group=GRmp)
			BTNS.volmusic=entities.Slider(WIDTH-BTNWIDTH*3.5,HEIGHT-BTNHEIGHT*3.5,BTNWIDTH*2,BTNHEIGHT2,"music volume",CONF.volmusic,batch=self.batch,group=GRmp)
			BTNS.volsfx=entities.Slider(WIDTH-BTNWIDTH*3.5,HEIGHT-BTNHEIGHT*5,BTNWIDTH*2,BTNHEIGHT2,"sfx volume",CONF.volsfx,batch=self.batch,group=GRmp)
			MISCE.bg=entities.Background(0,0,WIDTH,HEIGHT,(0,0,0,255),tex=MEDIA.menu,batch=self.batch,group=GRbg)
		elif scr==2:
			BTNS.back=entities.Button(WIDTH2,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Back",anch=4,key=k_BACK,batch=self.batch,group=GRmp)
			BTNS.start=entities.Button(WIDTH2,HEIGHT-BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Start",anch=4,key=k_OK,batch=self.batch,group=GRmp)
			BTNS.mode=entities.RadioList(WIDTH2,HEIGHT2,BTNWIDTH,BTNHEIGHT*3,["Normal","Normal","also Normal lol"],selected=self.diffmode,anch=1,batch=self.batch,group=GRmp)
			MISCE.bg=entities.Background(0,0,WIDTH,HEIGHT,(0,0,0,255),tex=MEDIA.menu,batch=self.batch,group=GRbg)
		elif scr==3:
			self.lv=LVLS.lvls[LVLS.curlv]
			self.lv.play()
			for i in range(4):
				LABELS.lives.append(entities.Heart(WIDTH3-SIZE20*(3-i),GBGy-SIZE20*1.5,SIZE20,SIZE20,MEDIA.heart,MEDIA.heart_death,batch=self.batch,group=GRfg))
			BTNS.pause=entities.Button(0,0,0,0,"",0,key=k_BACK,batch=self.batch,group=GRmp)
			PHYS.char=entities.Hooman(WIDTH2,HEIGHT2,SIZE/15,SIZE/12.5,self.batch,group=GRmp)
			PHYS.char.set_boundaries(GBGx,GBGy,GBG_x,GBG_y)
			MISCE.overlay=entities.Overlay(0,0,WIDTH,HEIGHT,(0,0,0,64),batch=self.batch,group=GRobg)
			MISCE.bg=entities.Background(0,0,WIDTH,HEIGHT,(0,0,0,0),self.batch,GRfb,tex=self.lv.bg)
		elif scr==4:
			BTNS.back=entities.Button(WIDTH-BTNWIDTH,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Back",anch=4,key=k_BACK,batch=self.batch,group=GRmp)
			LABELS.creds+=[
				entities.Label(BTNWIDTH2,HEIGHT-BTNHEIGHT,0,0,"Programming:",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH,HEIGHT-BTNHEIGHT*1.5,0,0,"Riedler",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH2,HEIGHT-BTNHEIGHT*2,0,0,"Graphics:",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH,HEIGHT-BTNHEIGHT*2.5,0,0,"Dark Rosemary (Sage)",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH2,HEIGHT-BTNHEIGHT*3,0,0,"Testing:",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH,HEIGHT-BTNHEIGHT*3.5,0,0,"Andreas S.",anch=6,batch=self.batch,group=GRfg),
				entities.Label(BTNWIDTH,HEIGHT-BTNHEIGHT*4,0,0,"Philip D.",anch=6,batch=self.batch,group=GRfg)]
		elif scr==5:
			BTNS.back=entities.Button(WIDTH-BTNWIDTH,BTNHEIGHT,BTNWIDTH,BTNHEIGHT,"Back",anch=4,key=k_BACK,batch=self.batch,group=GRmp)
			BTNS.lvls=entities.LevelSelect(WIDTH3,HEIGHT4,WIDTH3,HEIGHT2,LVLS.lvls,k_RIGHT,k_LEFT,k_OK,selected=LVLS.curlv,batch=self.batch,group=GRmp)
		else:
			raise ValueError(f"Scene {scr} does not exist to construct")

print("initializing main game class…")
game=Game(window)

print("starting main loop…")
pyglet.app.run()
