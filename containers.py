#!/usr/bin/python3
from CONSTANTS import *

class IMGC():
	def __init__(self,fp):
		self.img=pyglet.image.load(fp)
	def get(self,x,y,w,h,batch,group):
		return Sprite(x,y,w,h,self.img,batch,group)

class Sprite():
	def __init__(self,x,y,w,h,img,batch,group):
		self.x=x
		self.y=y
		self.sprite=pyglet.sprite.Sprite(img,x,y,batch=batch,group=group)
		self.ow=self.sprite.width
		self.oh=self.sprite.height
		self.set_size(w,h)
	def set_size(self,w,h):
		self.w=w
		self.h=h
		self.sprite.update(scale_x=w/self.ow,scale_y=h/self.oh)
	def set_pos(self,x,y):
		self.x=x
		self.y=y
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
	def __init__(self,fps,wait):
		self.imgs=[pyglet.image.load(fp) for fp in fps]
		self.wait=wait
	def get(self,x,y,w,h,batch,group):
		return AnimSprite(x,y,w,h,self.imgs,self.wait,batch,group)

class AnimSprite(Sprite):
	def __init__(self,x,y,w,h,imgs,wait,batch,group):
		self.x=x
		self.y=y
		self.ow=imgs[0].width
		self.oh=imgs[0].height
		self.visible=True
		self.wait=wait
		self.curs=0
		self.curw=0
		self.lens=len(imgs)
		self.sprites=[pyglet.sprite.Sprite(img,x,y,batch=batch,group=group) for img in imgs]
		for sprite in self.sprites[1:]:
			sprite.visible=False
		self.set_size(w,h)
	def set_size(self,w,h):
		self.w=w
		self.h=h
		for sprite in self.sprites:
			sprite.update(scale_x=w/self.ow,scale_y=h/self.oh)
	def set_pos(self,x,y):
		self.x=x
		self.y=y
		for sprite in self.sprites:
			sprite.update(x=x,y=y)
	def set_rotation(self,rot):
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
		for n in ("floor","walk","idle","crawl","cidle","btn","btnp"):
			if n in data:
				if isinstance(data[n],str):
					fn=data[n]
					fp=os.path.join(datafp,f"{fn}.png")
					if os.path.exists(fp):
						setattr(cls,n,IMGC(fp))
					else:
						print(f"Not loading {fn} as it wasn't found")
				else:
					fps=[]
					for fn in data[n][:-1]:
						fp=os.path.join(datafp,f"{fn}.png")
						if os.path.exists(fp):
							fps.append(fp)
						else:
							print(f"Not loading {fn} as it wasn't found")
					if len(fps)>0:
						setattr(cls,n,ANIMC(fps,data[n][-1]))
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
	@classmethod
	def all(cls):
		yield cls.fps
		yield cls.ups

class BTNS(ENTCONTAINER):
	#menu
	start=None#also in gmselect
	sett=None
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
		yield cls.start
		yield cls.sett
		yield cls.cancle
		yield cls.back
		yield cls.fullscr
		yield cls.showfps
		yield cls.vsync
		yield cls.mode
		yield cls.pause

class PHYS(ENTCONTAINER):#physical objects
	walls=[]
	char=None
	@classmethod
	def all(cls):
		return (*cls.walls,cls.char)

class MISCE(ENTCONTAINER):#miscellanious entities
	overlay=None#for pause screen
	@classmethod
	def all(cls):
		yield cls.overlay

print("initialized entity containers")
