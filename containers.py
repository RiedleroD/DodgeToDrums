#!/usr/bin/python3
from CONSTANTS import *
from time import time

class IMGC():
	def __init__(self,fp,nn):
		self.img=pyglet.image.load(fp)
		self.nn=nn
	def get(self,x,y,w,h,batch,group):
		return Sprite(x,y,w,h,self.img,self.nn,batch,group)

class Sprite():
	def __init__(self,x,y,w,h,img,nn,batch,group):
		self.x=x
		self.y=y
		self.rot=0
		if nn:
			#nearest-neighbour texture upscaling
			self.nn=lambda:pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D,pyglet.gl.GL_TEXTURE_MAG_FILTER,pyglet.gl.GL_NEAREST)
		else:
			self.nn=lambda:pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D,pyglet.gl.GL_TEXTURE_MAG_FILTER,pyglet.gl.GL_LINEAR)
		self.sprite=pyglet.sprite.Sprite(img,x,y,batch=batch,group=group)
		self.nn()
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
			#top right
			_x=cx+_ox*math.cos(rot)-_oy*math.sin(rot)
			_y=cy+_ox*math.sin(rot)+_oy*math.cos(rot)
			#top left
			__x=cx+ox*math.cos(rot)-_oy*math.sin(rot)
			__y=cy+ox*math.sin(rot)+_oy*math.cos(rot)
			#bottom right
			_x_=cx+_ox*math.cos(rot)-oy*math.sin(rot)
			_y_=cy+_ox*math.sin(rot)+oy*math.cos(rot)
		else:
			_x=_x_=x+w
			__x=x
			_y=_y_=y+h
			__y=y
		return (x,y,_x,_y,__x,__y,_x_,_y_)
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
		pass
	def show(self):
		self.sprite.visible=True
	def hide(self):
		self.sprite.visible=False
	def __del__(self):
		self.sprite.delete()

class ANIMC(IMGC):
	def __init__(self,fps,nn,wait):
		self.imgs=[pyglet.image.load(fp) for fp in fps]
		self.wait=wait
		self.nn=nn
	def get(self,x,y,w,h,batch,group):
		return AnimSprite(x,y,w,h,self.imgs,self.nn,self.wait,batch,group)

class AnimSprite(Sprite):
	def __init__(self,x,y,w,h,imgs,nn,wait,batch,group):
		self.x=x
		self.y=y
		self.ow=imgs[0].width
		self.oh=imgs[0].height
		self.visible=True
		self.wait=wait
		self.curs=0
		self.curw=0
		self.flipped=False
		self.lens=len(imgs)
		if nn:
			#nearest-neighbour texture upscaling
			self.nn=lambda:pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D,pyglet.gl.GL_TEXTURE_MAG_FILTER,pyglet.gl.GL_NEAREST)
		else:
			self.nn=lambda:pyglet.gl.glTexParameteri(pyglet.gl.GL_TEXTURE_2D,pyglet.gl.GL_TEXTURE_MAG_FILTER,pyglet.gl.GL_LINEAR)
		self.sprites=[]
		for img in imgs:
			sprite=pyglet.sprite.Sprite(img,x,y,batch=batch,group=group)
			self.nn()
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
		if self.flipped:
			x+=self.w
		for sprite in self.sprites:
			sprite.update(x=x,y=y)
	def set_rotation(self,rot):
		if self.flipped:
			rot=(360-rot)%360
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
	walk=None
	idle=None
	crawl=None
	cidle=None
	btn=None
	btnp=None
	menu=None
	bullet1=None
	@classmethod
	def load_all(cls,fp):
		if os.path.exists(fp):
			with open(os.path.join(fp,"sprites.json"),"r") as f:
				data=json.load(f)
			cls.loads_all(data)
		else:
			print(f"No resources loaded as sprites.json wasn't found in {fp}")
	@classmethod
	def loads_all(cls,data):
		for n in ("walk","idle","crawl","cidle","btn","btnp","menu","bullet1"):
			if n in data:
				if isinstance(data[n][0],str):
					fn,nn=data[n]
					fp=os.path.join(datafp,f"{fn}.png")
					if os.path.exists(fp):
						setattr(cls,n,IMGC(fp,nn))
					else:
						print(f"Not loading {fn} as it wasn't found")
				else:
					fps=[]
					for fn in data[n][0]:
						fp=os.path.join(datafp,f"{fn}.png")
						if os.path.exists(fp):
							fps.append(fp)
						else:
							print(f"Not loading {fn} as it wasn't found")
					if len(fps)>0:
						setattr(cls,n,ANIMC(fps,*data[n][1][:2]))
					else:
						print(f"Not loading animation {n} as no frames were found")
			else:
				print(f"consider adding resource {n} to your resource pack")

MEDIA.load_all(datafp)
print("Loaded media")

class Level():
	def __init__(self,name,img,acts):
		self.name=name
		self.img=img
		self.acts=acts
	def start(self):
		self.t=time()
		self.unf=self.acts.copy()#unf→ unfinished acts
	def cycle(self)->"list with all actions to do":
		td=time()-self.t
		acts=[]
		while self.unf and self.unf[0][1]<td:
			act=self.unf.pop(0)
			acts.append([act[0],*act[2:]])
		return acts
	@classmethod
	def load(cls,fp):
		with open(fp,"r") as f:
			data=json.load(f)
		return cls.loads(data,os.path.dirname(fp))
	@classmethod
	def loads(cls,data,fp):
		imgfn,imgdat=data["img"]
		if isinstance(imgfn,str):
			nn,=imgdat
			img=IMGC(os.path.join(fp,imgfn+".png"),nn)
		else:
			wait,nn=imgdat
			img=ANIMC([os.path.join(fp,fn+".png") for fn in imgfn],nn,wait)
		return cls(data["name"],img,data["act"])

class LVLS:
	curlv=0
	lvls=None
	@classmethod
	def load_all(cls,fp):
		if os.path.exists(fp):
			cls.lvls=[]
			for d in os.listdir(fp):
				d=os.path.join(fp,d)
				if os.path.isdir(d):
					lv=os.path.join(d,"level.json")
					if os.path.exists(lv):
						try:
							cls.lvls.append(Level.load(lv))
						except Exception as e:
							print(e.__class__.__name__,e,sep=": ")
			if len(cls.lvls)==0:
				raise ValueError(f"No levels found in level directory {fp}")
		else:
			raise ValueError(f"Couldn't find level directory {fp}")

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
	creds=[]
	@classmethod
	def all(cls):
		return (cls.fps,cls.ups,cls.notice,*cls.creds)

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
	#game mode select
	mode=None
	#while in game
	pause=None
	#level select
	lvls=None
	@classmethod
	def all(cls):
		return (*cls.strg,cls.lvls,cls.start,cls.sett,cls.cancle,cls.back,cls.fullscr,cls.showfps,cls.vsync,cls.showcoll,cls.mode,cls.pause,cls.creds)

class PHYS(ENTCONTAINER):#physical objects
	walls=[]
	char=None
	bullets=[]
	@classmethod
	def all(cls):
		return (*cls.walls,*cls.bullets,cls.char)

class MISCE(ENTCONTAINER):#miscellanious entities
	overlay=None#for pause screen
	menubg=None#menu background
	@classmethod
	def all(cls):
		yield cls.overlay
		yield cls.menubg

print("initialized entity containers")
