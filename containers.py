#!/usr/bin/python3
from CONSTANTS import *
from time import time
from collections.abc import Iterable

class IMGC():
	def __init__(self,fp,nn):
		pyglet.image.Texture.default_mag_filter=pyglet.gl.GL_NEAREST if nn else pyglet.gl.GL_LINEAR
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
		self.visible=self.sprite.visible=True
	def hide(self):
		self.visible=self.sprite.visible=False
	def __del__(self):
		self.sprite.delete()

class ANIMC(IMGC):
	def __init__(self,fps,nn,wait):
		pyglet.image.Texture.default_mag_filter=pyglet.gl.GL_NEAREST if nn else pyglet.gl.GL_LINEAR
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
	sign=None
	signp=None
	heart=None
	heart_death=None
	#progress bar
	progrleft=None
	progrmid=None
	progrright=None
	progrfill=None
	#backgrounds
	menu=None
	bg1=None
	bg2=None
	bg3=None
	bg4=None
	bg5=None
	bg6=None
	#projectiles
	knife=None
	flame_smol=None
	flame_big=None
	bomb=None
	explosion=None
	#sounds
	click=1
	hurt=1
	menubgm=1
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
		for n,val in cls.__dict__.items():
			if n.startswith("_"):
				continue
			elif val==None:
				if n in imgs:
					cls.load_img(imgs[n],n)
				else:
					print(f"not loading image {n} as it's not in the resource pack")
			elif val==1:
				if n in sfx:
					cls.load_sfx(sfx[n],n)
				else:
					print(f"not loading sound {n} as it's not in the resource pack")
	@classmethod
	def load_img(cls,img,n):
		val=None
		if isinstance(img[0],str):
			fn,nn=img
			fp=os.path.join(datafp,f"{fn}.png")
			if os.path.exists(fp):
				val=IMGC(fp,nn)
			else:
				print(f"not loading sprite {fn} as it wasn't found")
		else:
			fps=[]
			if isinstance(img[0][0],int):
				st,nd,nm=img[0]
				faulty=False
				for i in range(st,nd+1):
					try:
						fn=nm%i
					except TypeError:
						print(f"not loading animation {n} as its string formatting is faulty")
						faulty=True
						return
					fp=os.path.join(datafp,f"{fn}.png")
					if os.path.exists(fp):
						fps.append(fp)
					else:
						print(f"not loading frame {fn} from animation {n} as it wasn't found")
			else:
				for fn in img[0]:
					fp=os.path.join(datafp,f"{fn}.png")
					if os.path.exists(fp):
						fps.append(fp)
					else:
						print(f"not loading frame {fn} from animation {n} as it wasn't found")
			if len(fps)>0:
				val=ANIMC(fps,*img[1][:2])
			else:
				print(f"not loading animation {n} as no frames were found")
		setattr(cls,n,val)
	@classmethod
	def load_sfx(cls,sfx,n):
		val=None
		fn,strem=sfx
		fp=os.path.join(datafp,f"{fn}.opus")
		if os.path.exists(fp):
			val=pyglet.media.load(fp,streaming=strem)
		else:
			print(f"not loading sound {fn} as it wasn't found in {fp}")
		setattr(cls,n,val)

MEDIA.load_all(datafp)
print("Loaded media")

class Level():
	def __init__(self,name,img,bg,mus,acts,lp,progr=None):
		self.name=name
		self.img=img
		self.bg=bg
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
		bg=data["bg"]
		bg=getattr(MEDIA,f"bg{bg}",None)
		if bg==None:
			bg=MEDIA.bg1
		if isinstance(imgfn,str):
			nn,=imgdat
			img=IMGC(os.path.join(fp,imgfn+".png"),nn)
		else:
			wait,nn=imgdat
			img=ANIMC([os.path.join(fp,fn+".png") for fn in imgfn],nn,wait)
		return cls(data["name"],img,bg,mus,data["act"],fp,progress)

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

class ENTCONTAINER:#base for all entity containers
	def all(self):
		l=[]
		for val in self.__dict__.values():
			if isinstance(val,Iterable):
				l+=val
			else:
				l.append(val)
		return l
	def draw(self):
		for ent in self.all():
			if ent:
				ent.draw()
	def __getattr__(self,name):
		if name in self.__dict__.keys():
			return self.__dict__[name]
		else:
			return None

LABELS=ENTCONTAINER()
LABELS.lives=[]
BTNS=ENTCONTAINER()
BTNS.strg=[]
PHYS=ENTCONTAINER()#physical objects
PHYS.bullets=[]
MISCE=ENTCONTAINER()#miscellanious entities

window.set_containers(LABELS,BTNS,PHYS,MISCE)

print("initialized entity containers")
