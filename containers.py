#!/usr/bin/python3
from CONSTANTS import *

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
			self.sprite.update(x=self.x+self.w,scale_x=-self.w/self.ow)
		else:
			self.sprite.update(x=self.x,scale_x=self.w/self.ow)
	def set_size(self,w,h):
		self.w=w
		self.h=h
		self.sprite.update(scale_x=w/self.ow,scale_y=h/self.oh)
	def set_pos(self,x,y):
		self.x=x
		self.y=y
		if self.flipped:
			x+=self.w
		self.sprite.update(x=x,y=y)
	def set_rotation(self,rot):
		self.sprite.update(rotation=rot)
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
		for n in ("floor","walk","idle","crawl","cidle","btn","btnp","menu"):
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

class ENTCONTAINER:#base class for all entity containers
	@classmethod
	def draw(cls,*args,**kwargs):
		for ent in cls.all():
			if ent:
				ent.draw(*args,**kwargs)

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
	start=None#also in gmselect
	sett=None
	creds=None
	#generic back & cancle buttons
	back=None
	cancle=None
	#settings
	fullscr=None
	showfps=None
	vsync=None
	#game mode select
	mode=None
	#while in game
	pause=None
	@classmethod
	def all(cls):
		return (cls.start,cls.sett,cls.cancle,cls.back,cls.fullscr,cls.showfps,cls.vsync,cls.mode,cls.pause,cls.creds)

class PHYS(ENTCONTAINER):#physical objects
	walls=[]
	char=None
	@classmethod
	def all(cls):
		return (*cls.walls,cls.char)

class MISCE(ENTCONTAINER):#miscellanious entities
	overlay=None#for pause screen
	menubg=None#menu background
	@classmethod
	def all(cls):
		yield cls.overlay
		yield cls.menubg

print("initialized entity containers")
