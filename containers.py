#!/usr/bin/python3
from CONSTANTS import *
from time import time

class IMGC():
	def __init__(self,fp,nn):
		pyglet.image.Texture.default_min_filter=pyglet.image.Texture.default_mag_filter=pyglet.gl.GL_NEAREST if nn else pyglet.gl.GL_LINEAR
		self.img=pyglet.image.load(fp)
		self.texture=self.img.get_texture()
		self.nn=nn
	def get(self,x,y,w,h,batch,group,visible=True):
		s=Sprite(x,y,w,h,self.texture,self.nn,batch,group)
		if not visible:
			s.hide()
		return s

class Sprite():
	px=None
	py=None
	pw=None
	ph=None
	prot=None
	lens=0
	def __init__(self,x,y,w,h,img,nn,batch,group):
		self.x=x
		self.y=y
		self.rot=0
		self.sprite=pyglet.sprite.Sprite(img,x,y,batch=batch,group=group)
		self.flipped=False
		self.ow=self.sprite.width
		self.oh=self.sprite.height
		self.set_size(w,h)
	def flip(self):
		self.flipped=not self.flipped
		if self.flipped:
			x=self.x+self.w
			scale_x=-self.w/self.ow
		else:
			x=self.x
			scale_x=self.w/self.ow
		if self.rot:
			j=self.rot/90
			n=self.rot/180
			x+=self.w*(3+abs(1-j)-abs(n-1)-j-abs(j-3))
		self.sprite.update(x=x,scale_x=scale_x)
	def set_size(self,w,h):
		self.w=w
		self.h=h
		self.sprite.update(scale_x=w/self.ow,scale_y=h/self.oh)
	def set_pos(self,x,y):
		self.x=x
		self.y=y
		if self.rot:
			x,y,_x,_y,__x,__y,_x_,_y_=self.get_posss()
		if self.flipped:
			x+=self.w
		self.sprite.update(x=x,y=y)
	def set_rotation(self,rot):
		rot%=360
		self.rot=rot
		x,y,_x,_y,__x,__y,_x_,_y_=self.get_posss()
		self.sprite.update(rotation=rot,y=y,x=x)
	def get_posss(self):
		x=self.x
		y=self.y
		w=self.w
		h=self.h
		if not (x==self.px and y==self.py and w==self.pw and h==self.ph and self.rot==self.prot):
			if self.rot:
				rot=math.radians(180-self.rot)
				cx=x+w/2
				cy=y+h/2
				ox=w/2
				oy=h/2
				_ox=-w/2
				_oy=-h/2
				#bottom left
				x=cx+ox*math.cos(rot)-oy*math.sin(rot)
				y=cy+ox*math.sin(rot)+oy*math.cos(rot)
				#top left
				_x=cx+ox*math.cos(rot)-_oy*math.sin(rot)
				_y=cy+ox*math.sin(rot)+_oy*math.cos(rot)
				#top right
				__x=cx+_ox*math.cos(rot)-_oy*math.sin(rot)
				__y=cy+_ox*math.sin(rot)+_oy*math.cos(rot)
				#bottom right
				_x_=cx+_ox*math.cos(rot)-oy*math.sin(rot)
				_y_=cy+_ox*math.sin(rot)+oy*math.cos(rot)
			else:
				_x=_x_=x+w
				__x=x
				_y=_y_=y+h
				__y=y
			self.pposs=(x,y,_x,_y,__x,__y,_x_,_y_)
			self.pw=w
			self.ph=h
			self.px=x
			self.py=y
			self.prot=self.rot
		return self.pposs
	def get_poss(self):
		if self.rot:
			x,y,_x,_y,__x,__y,_x_,_y_=self.get_posss()
			return (min(x,_x,__x,_x_),min(y,_y,__y,_y_),max(x,_x,__x,_x_),max(y,_y,__y,_y_))
		else:
			return (self.x,self.y,self.x+self.w,self.y+self.h)
	def get_bb(self):
		x,y,_x,_y=self.get_poss()
		return (x,y,_x-x,_y-y)
	def cycle(self):
		return 0
	def show(self):
		self.sprite.visible=True
	def hide(self):
		self.sprite.visible=False
	def __del__(self):
		self.sprite.delete()

class ANIMC(IMGC):
	def __init__(self,fps,nn,wait):
		pyglet.image.Texture.default_min_filter=pyglet.image.Texture.default_mag_filter=pyglet.gl.GL_NEAREST if nn else pyglet.gl.GL_LINEAR
		self.imgs=[pyglet.image.load(fp) for fp in fps]
		self.textures=[]
		for img in self.imgs:
			txt=img.get_texture()
			self.textures.append(txt)
		self.wait=wait
		self.nn=nn
	def get(self,x,y,w,h,batch,group,visible=True):
		s=AnimSprite(x,y,w,h,self.textures,self.nn,self.wait,batch,group)
		if not visible:
			s.hide()
		return s

class AnimSprite(Sprite):
	curs=0
	curw=0
	def __init__(self,x,y,w,h,imgs,nn,wait,batch,group):
		self.x=x
		self.y=y
		self.rot=0
		self.ow=imgs[0].width
		self.oh=imgs[0].height
		self.visible=True
		self.wait=wait
		self.flipped=False
		self.lens=len(imgs)
		self.sprites=[]
		for img in imgs:
			sprite=pyglet.sprite.Sprite(img,x,y,batch=batch,group=group)
			sprite.visible=False
			self.sprites.append(sprite)
		self.sprites[0].visible=True
		self.set_size(w,h)
	def flip(self):
		self.flipped=not self.flipped
		if self.flipped:
			for sprite in self.sprites:
				sprite.update(x=self.x+self.w,scale_x=-self.w/self.ow)
		else:
			for sprite in self.sprites:
				sprite.update(x=self.x,scale_x=self.w/self.ow)
	def set_size(self,w,h):
		self.w=w
		self.h=h
		if self.flipped:
			w=-w
		for sprite in self.sprites:
			sprite.update(scale_x=w/self.ow,scale_y=h/self.oh)
	def set_pos(self,x,y):
		self.x=x
		self.y=y
		if self.rot:
			x,y,_x,_y,__x,__y,_x_,_y_=self.get_posss()
		if self.flipped:
			x+=self.w
		for sprite in self.sprites:
			sprite.update(x=x,y=y)
	def set_rotation(self,rot):
		if self.flipped:
			rot=(360-rot)%360
		self.rot=rot
		for sprite in self.sprites:
			sprite.update(rotation=rot)
	def cycle(self):
		self.curw+=1
		if self.curw>=self.wait:
			self.sprites[self.curs].visible=False
			self.curs+=1
			self.curs%=self.lens
			self.sprites[self.curs].visible=self.visible
			self.curw=0
		return self.curs
	def show(self):
		self.visible=True
		self.sprites[self.curs].visible=True
	def hide(self):
		self.visible=False
		self.sprites[self.curs].visible=False
		self.curs=0
		self.curw=0
	def __del__(self):
		for sprite in self.sprites:
			sprite.delete()

class MEDIA:
	#main character
	idle=None
	up=None
	down=None
	side=None
	idle=None
	cup=None
	cdown=None
	cside=None
	cidle=None
	death=None
	#ui stuff
	btn=None
	btnp=None
	progrbar=None
	progrfill=None
	#backgrounds
	menu=None
	bg_1=None
	bg_2=None
	bg_3=None
	#projectiles
	knife=None
	flame_smol=None
	flame_big=None
	#sounds
	click=None
	hurt=None
	@classmethod
	def load_all(cls,fp):
		if os.path.isdir(fp):
			imgfp=os.path.join(fp,"sprites.json")
			sfxfp=os.path.join(fp,"sfx.json")
			if os.path.isfile(imgfp):
				with open(imgfp,"r") as f:
					imgs=json.load(f)
			else:
				imgs={}
			if os.path.isfile(sfxfp):
				with open(sfxfp,"r") as f:
					sfx=json.load(f)
			else:
				sfx={}
			cls.loads_all(imgs,sfx)
		else:
			print(f"no resources loaded as {fp} wasn't found")
	@classmethod
	def loads_all(cls,imgs,sfx):
		for n in (
				"idle","up","down","side",#main character
				"cup","cdown","cside","cidle",#main character crouching
				"death",
				"btn","btnp",#ui elements
				"knife","flame_big","flame_smol",#projectiles
				"progrleft","progrmid","progrright","progrfill",#progress bar
				"menu","bg1","bg2","bg3"):#backgrounds
			if n in imgs:
				if isinstance(imgs[n][0],str):
					fn,nn=imgs[n]
					fp=os.path.join(datafp,f"{fn}.png")
					if os.path.exists(fp):
						setattr(cls,n,IMGC(fp,nn))
					else:
						print(f"not loading sprite {fn} as it wasn't found")
				else:
					fps=[]
					for fn in imgs[n][0]:
						fp=os.path.join(datafp,f"{fn}.png")
						if os.path.exists(fp):
							fps.append(fp)
						else:
							print(f"not loading frame {fn} from animation {n} as it wasn't found")
					if len(fps)>0:
						setattr(cls,n,ANIMC(fps,*imgs[n][1][:2]))
					else:
						print(f"not loading animation {n} as no frames were found")
			else:
				print(f"not loading image {n} as it's not in the resource pack")
		for n in ("hurt","click"):
			if n in sfx:
				fn,strem=sfx[n]
				fp=os.path.join(datafp,f"{fn}.opus")
				if os.path.exists(fp):
					setattr(cls,n,pyglet.media.load(fp,streaming=strem))
				else:
					print(f"not loading sound {fn} as it wasn't found")
			else:
				print(f"not loading sound {n} as it's not in the resource pack")

MEDIA.load_all(datafp)
print("Loaded media")

class Level():
	def __init__(self,name,img,mus,acts,lp,progr=None):
		self.name=name
		self.img=img
		self.mus=mus
		self.len=self.mus.duration
		self.player=None
		self.vol=CONF.volmaster*CONF.volmusic
		self.fit=None
		self.fot=None
		self.acts=acts
		if progr:
			self.progr=progr
		else:
			self.progr=[]
		self.lp=lp#level path
	def play(self):
		self.unf=self.acts.copy()#unf→ unfinished acts
		self.player=self.mus.play()
		self.set_volume(CONF.volmaster*CONF.volmusic)
	def set_volume(self,vol):#not in percent but as float from 0 to 1
		self.player.volume=vol
		self.vol=vol
	def cycle(self)->"list with all actions to do":
		if self.player and self.player.playing:
			t=self.player.time
			if self.fit:
				v=(t-self.fit)/self.fot
				if v>=1:
					v=1
					self.fit=None
				self.player.volume=self.vol*v
			acts=[]
			while self.unf and self.unf[0][1]<t:
				act=self.unf.pop(0)
				acts.append([act[0],*act[2:]])
			if not self.player.playing:
				acts.append(["stop"])
			return acts,t
		else:
			return [],0
	def fade_in(self,t):
		if self.player:
			self.player.volume=0
			self.fit=self.player.time
			self.fot=t
	def stop(self):
		if self.player:
			#get & save new score
			self.progr.append(round(self.player.time,2))
			with open(os.path.join(self.lp,"progress.json"),"w+") as f:
				json.dump(self.progr,f)
			print(f"added new score {self.player.time} to level {self.name}")
			self.player.next_source()#else the StreamingSource doesn't get unqueued
			self.player.delete()
			self.player=None
		self.fit=None
		self.fot=None
	def pause(self):
		if not self.player:
			pass
		elif self.player.playing:
			self.player.pause()
		else:
			self.player.play()
	def __del__(self):
		self.stop()
		self.mus.delete()
	@classmethod
	def load(cls,dp):
		lfp=os.path.join(dp,"level.json")
		pfp=os.path.join(dp,"progress.json")
		with open(lfp,"r") as f:
			data=json.load(f)
		if os.path.exists(pfp):
			with open(pfp,"r") as f:
				progress=json.load(f)
		else:
			progress=[]
		return cls.loads(data,progress,dp)
	@classmethod
	def loads(cls,data,progress,fp):
		musfp=os.path.join(fp,data["mus"]+".opus")
		if os.path.exists(musfp):
			mus=pyglet.media.load(musfp,streaming=True)
		else:
			raise ValueError(f"Level music not found at {musfp}")
		imgfn,imgdat=data["img"]
		if isinstance(imgfn,str):
			nn,=imgdat
			img=IMGC(os.path.join(fp,imgfn+".png"),nn)
		else:
			wait,nn=imgdat
			img=ANIMC([os.path.join(fp,fn+".png") for fn in imgfn],nn,wait)
		return cls(data["name"],img,mus,data["act"],fp,progress)

class LVLS:
	curlv=0
	lvls=[]
	@classmethod
	def load_all(cls,fp):
		if os.path.exists(fp):
			for d in os.listdir(fp):
				d=os.path.join(fp,d)
				if os.path.isdir(d):
					if os.path.exists(os.path.join(d,"level.json")):
						try:
							cls.lvls.append(Level.load(d))
						except Exception as e:
							print(e.__class__.__name__,e,sep=": ")
			if len(cls.lvls)==0:
				print(f"No levels found in level directory {fp}")
		else:
			print(f"Couldn't find level directory {fp}")

LVLS.load_all(lvlfp)
print("loaded levels")

class ENTCONTAINER:#base class for all entity containers
	@classmethod
	def draw(cls):
		for ent in cls.all():
			if ent:
				ent.draw()

class LABELS(ENTCONTAINER):
	fps=None
	ups=None
	notice=None
	version=None
	lives=None
	creds=[]
	@classmethod
	def all(cls):
		return (cls.fps,cls.ups,cls.notice,cls.version,cls.lives,*cls.creds)

class BTNS(ENTCONTAINER):
	#menu
	sett=None
	creds=None
	#generic back, start & cancle buttons
	start=None
	back=None
	cancle=None
	#settings
	fullscr=None
	showfps=None
	vsync=None
	showcoll=None
	strg=[]
	volmaster=None
	volmusic=None
	volsfx=None
	#game mode select
	mode=None
	#while in game
	pause=None
	#level select
	lvls=None
	@classmethod
	def all(cls):
		return (
			*cls.strg,
			cls.lvls,
			cls.start,
			cls.sett,
			cls.volmaster,
			cls.volmusic,
			cls.volsfx,
			cls.cancle,
			cls.back,
			cls.fullscr,
			cls.showfps,
			cls.vsync,
			cls.showcoll,
			cls.mode,
			cls.pause,
			cls.creds)

class PHYS(ENTCONTAINER):#physical objects
	walls=[]
	char=None
	bullets=[]
	@classmethod
	def all(cls):
		return (*cls.walls,*cls.bullets,cls.char)

class MISCE(ENTCONTAINER):#miscellanious entities
	overlay=None#for pause screen
	bg=None#generic background
	@classmethod
	def all(cls):
		yield cls.overlay
		yield cls.bg

print("initialized entity containers")
