#!/usr/bin/python3
from containers import MEDIA,Sprite
from CONSTANTS import *

class Entity:
	def __init__(self,x,y,w,h,anch=0,batch=None,group=None):
		self.w=w
		self.h=h
		self.set_pos(x,y,anch)
		self.rendered=False
		self.batch=batch
		self.group=group
		self.vl=None
		self.hidden=False
	def set_pos(self,x,y,anch=0):
		#anchor:
		#______
		#|6 7 8|
		#|3 4 5|
		#|0 1 2|
		#——————
		if anch>8:
			raise ValueError("Entity initialized with invalid position anchor: %i"%anch)
		if anch%3==0:
			self.x=x
		elif anch%3==1:
			self.x=x-self.w/2
		else:
			self.x=x-self.w
		if anch//3==0:
			self.y=y
		elif anch//3==1:
			self.y=y-self.h/2
		else:
			self.y=y-self.h
		self.set_deriv()
	def set_size(self,w,h):
		self.w=w
		self.h=h
		self.set_deriv()
	def set_deriv(self):
		self.cx=self.x+self.w/2
		self.cy=self.y+self.h/2
		self._x=self.x+self.w
		self._y=self.y+self.h
		self.rendered=False
	def render(self):
		self.quad=('v2f',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
		self.rendered=True
	def move(self,x,y):
		self.x+=x
		self.y+=y
		self.cx+=x
		self.cy+=y
		self._x+=x
		self._y+=y
		self.rendered=False
	def doesPointCollide(self,x,y):
		return x>=self.x and y>=self.y and x<=self._x and y<=self._y
	def checkPointCollision(self,x,y):
		if self.doesPointCollide(x,y):
			if x>=self.cx:
				if y>=self.cy:
					return (self._x-x,self._y-y)
				else:
					return (self._x-x,self.y-y)
			else:
				if y>=self.cy:
					return (self.x-x,self._y-y)
				else:
					return (self.x-x,self.y-y)
		else:
			return (0,0)
	def distance_from(self,x,y):
		return (self.x-x,self.y-y)
	def hide(self):
		self.hidden=True
	def show(self):
		self.hidden=False
	def draw(self):
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
		if not self.hidden:
			self.batch.add(4,pyglet.gl.GL_QUADS,self.group,self.quad)
	def __del__(self):
		if self.vl:
			self.vl.delete()

class Overlay(Entity):
	def __init__(self,x,y,w,h,c,batch,group):
		super().__init__(x,y,w,h,batch=batch,group=group)
		self.set_color(c)
	def set_color(self,c):
		if len(c)!=4:
			raise ValueError(f"Invalid color tuple {c}: must be exactly 3 integers long")
		elif max(c)>255 or min(c)<0:
			raise ValueError(f"Invalid color tuple {c}: numbers must range between 0 and 255")
		self.cquad=('c4B',c*4)
	def draw(self):
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
		self.vl=pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad,self.cquad)

class Background(Entity):
	def __init__(self,x,y,w,h,c,batch,group,tex=None):
		super().__init__(x,y,w,h,batch=batch,group=group)
		self.sprite=tex.get(x,y,w,h,batch,group) if tex else None
		self.set_color(c)
	def set_color(self,c):
		if len(c)!=4:
			raise ValueError(f"Invalid color tuple {c}: must be exactly 3 integers long")
		elif max(c)>255 or min(c)<0:
			raise ValueError(f"Invalid color tuple {c}: numbers must range between 0 and 255")
		self.cquad=('c4B',c*4)
	def draw(self):
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
		if self.sprite:
			self.sprite.nn()
			self.sprite.cycle()
		else:
			self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,self.group,self.quad,self.cquad)

class Label(Entity):
	def __init__(self,x,y,w,h,text,anch=0,color=(255,255,255,255),bgcolor=(0,0,0,0),size=12,batch=None,group=None):
		self.label=pyglet.text.Label(text,x=x,y=y,color=color,font_size=size,batch=batch,group=group)
		self.setText(text)
		self.setColor(color)
		self.setBgColor(bgcolor)
		self.anch=anch
		self.size=size
		super().__init__(x,y,w,h,anch,batch=batch,group=group)
	def setBgColor(self,color):
		self.cquad=("c4B",color*4)
	def setColor(self,color):
		self.color=color
		self.label.color=self.color
	def setText(self,text):
		self.text=text
		self.label.text=text
	def render(self):
		if self.w>0 and self.h>0:
			self.quad=('v2f',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
			self.label.x=self.cx
			self.label.y=self.cy
			self.label.anchor_x=ANCHORSx[1]
			self.label.anchor_y=ANCHORSy[1]
		else:
			self.label.x=self.x
			self.label.y=self.y
			self.label.anchor_x=ANCHORSx[self.anch%3]
			self.label.anchor_y=ANCHORSy[self.anch//3]
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
		if self.w>0 and self.h>0:
			self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,self.group,self.quad,self.cquad)
	def __del__(self):
		self.label.delete()
		if self.vl:
			self.vl.delete()

class Button(Label):
	def __init__(self,x,y,w,h,text,anch=0,key=None,size=16,pressedText=None,batch=None,group=None):
		self.pressed=False
		self.key=key
		if pressedText:
			self.pressedText=pressedText
			self.unpressedText=text
		else:
			self.pressedText=self.unpressedText=text
		super().__init__(x,y,w,h,text,anch,(0,0,0,255),(255,255,255,255),size,batch=batch,group=GRs[GRs.index(group)+1])
		if MEDIA.btn:
			self.sprite=MEDIA.btn.get(self.x,self.y,w,h,batch,group)
		else:
			self.sprite=None
		if MEDIA.btnp:
			self.psprit=MEDIA.btnp.get(self.x,self.y,w,h,batch,group)
		else:
			self.psprit=None
	def setBgColor(self,color):
		if self.pressed:
			self.cquad=("c4B",(*color,*color,128,128,128,255,128,128,128,255))
		else:
			self.cquad=("c4B",(128,128,128,255,128,128,128,255,*color,*color))
	def checkpress(self,x,y):
		if self.doesPointCollide(x,y):
			return self.press()
	def checkKey(self,key):
		if self.key!=None and key==self.key:
			return self.press()
	def press(self):
		if not self.pressed:
			self.pressed=True
			self.setText(self.pressedText)
			self.setBgColor((255,255,255,255))
			return pyglet.event.EVENT_HANDLED
	def release(self):
		if self.pressed:
			self.pressed=False
			self.setText(self.unpressedText)
			self.setBgColor((255,255,255,255))
			return pyglet.event.EVENT_HANDLED
	def draw(self):
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
			self.vl=None
		if self.sprite and self.pressed:
			self.sprite.hide()
		elif self.psprit and not self.pressed:
			self.psprit.hide()
		if self.psprit and self.pressed:
			self.psprit.nn()
			self.psprit.show()
		elif self.sprite and not self.pressed:
			self.sprite.nn()
			self.sprite.show()
		else:
			if self.w>0 and self.h>0:
				self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,self.group,self.quad,self.cquad)

class ButtonSwitch(Button):
	def checkpress(self,x,y):
		if self.doesPointCollide(x,y):
			if self.pressed:
				self.release()
			else:
				self.press()

class ButtonFlipthrough(Button):
	def __init__(self,x,y,w,h,text,values,anch=0,key=None,size=12,batch=None,group=None):
		self.vals=values
		self.i=0
		self.text=text
		super().__init__(x,y,w,h,text%values[0],anch,key,size,batch=batch,group=group)
	def setText(self,text):
		self.label.text=text
	def getCurval(self):
		return self.vals[self.i]
	def press(self):
		self.i+=1
		self.i%=len(self.vals)
		self.setText(self.text%self.getCurval())
		return pyglet.event.EVENT_HANDLED

class StrgButton(Button):
	def __init__(self,x,y,w,h,desc,value,anch=0,size=12,batch=None,group=None):
		self.keyname=pyglet.window.key.symbol_string
		self.btxt=desc
		self.val=value
		super().__init__(x,y,w,h,f"{desc}:{self.keyname(value)}",anch,None,size,None,batch=batch,group=group)
	def press(self):
		if not self.pressed:
			self.pressed=True
			self.setText(f"[{self.keyname(self.val)}]")
			self.setBgColor((255,255,255,255))
			return pyglet.event.EVENT_HANDLED
	def release(self):
		if self.pressed:
			self.pressed=False
			self.setText(f"{self.btxt}:{self.keyname(self.val)}")
			self.setBgColor((255,255,255,255))
			return pyglet.event.EVENT_HANDLED
	def set_desc(self,desc):
		self.btxt=desc
		if not self.pressed:
			self.setText(f"{desc}:{self.keyname(self.val)}")
	def checkKey(self,key):
		if self.pressed:
			self.val=key
			return self.release()

class RadioList(Entity):
	def __init__(self,x,y,w,h,texts,anch=0,keys=None,pressedTexts=None,selected=None,size=16,batch=None,group=None):
		btnc=len(texts)
		if keys==None:
			keys=[None for i in range(btnc)]
		if pressedTexts==None:
			pressedTexts=[None for i in range(btnc)]
		self.btns=[Button(x,y-i*h/btnc,w,h/btnc,text,anch,keys[i],size,pressedTexts[i],batch=batch,group=group) for i,text in enumerate(texts)]
		if selected!=None:
			self.btns[selected].press()
		super().__init__(x,y,w,h,anch,batch=batch,group=group)
		del self.vl
	def checkpress(self,x,y):
		prsd=None
		for i,btn in enumerate(self.btns):
			prsd=btn.checkpress(x,y)
			if prsd:
				prsd=i
				break
		if prsd!=None:
			for i,btn in enumerate(self.btns):
				if i!=prsd and btn.pressed:
					btn.release()
			return pyglet.event.EVENT_HANDLED
	def checkKey(self,key):
		for i,btn in enumerate(self.btns):
			prsd=btn.checkKey(key)
			if prsd:
				prsd=i
				break
		if prsd!=None:
			for i,btn in enumerate(self.btns):
				if i!=prsd:
					btn.release()
			return pyglet.event.EVENT_HANDLED
	def render(self):
		self.rendered=True
	def draw(self):
		for btn in self.btns:
			btn.draw()
	def getSelected(self):
		for i,btn in enumerate(self.btns):
			if btn.pressed:
				return i
	def __del__(self):
		pass

class PhysEntity(Entity):
	def __init__(self,x,y,w,h,c,batch,group):
		super().__init__(x,y,w,h,0,batch,group)
		self.set_speed(0,0)
		self.set_color(c)
	def set_speed(self,x,y):
		self.spdx=x
		self.spdy=y
	def set_color(self,c):
		if len(c)!=4:
			raise ValueError(f"Invalid color tuple {c}: must be exactly 3 integers long")
		elif max(c)>255 or min(c)<0:
			raise ValueError(f"Invalid color tuple {c}: numbers must range between 0 and 255")
		self.cquad=('c4B',c*4)
	def cycle(self):
		if self.spdx>0 or self.spdy>0:
			self.move(self.spdx,self.spdy)
	def render(self):
		self.quad=('v2f',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
			self.vl=None
		self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,group,self.quad,self.cquad)

class Wall(PhysEntity):
	def __init__(self,x,y,w,h,c,batch,group):
		super().__init__(x,y,w,h,c,batch,group)

class Hooman(PhysEntity):
	l=False
	r=False
	u=False
	d=False
	sh=False#shift → crouch
	wb=None#width boundary
	hb=None#height boundary
	bh=None#holds the base height when crouching
	s_walk=None
	s_idle=None
	s_crawl=None
	s_cidle=None
	a=None
	preva=None
	flipped=False
	def __init__(self,x,y,w,h,c,batch,group):
		if MEDIA.walk:
			self.s_walk=MEDIA.walk.get(x,y,w,h,batch,group)
			self.s_walk.hide()
		if MEDIA.idle:
			self.s_idle=MEDIA.idle.get(x,y,w,h,batch,group)
		if MEDIA.crawl:
			self.s_crawl=MEDIA.crawl.get(x,y,w,h/2,batch,group)
			self.s_crawl.hide()
		if MEDIA.cidle:
			self.s_cidle=MEDIA.cidle.get(x,y,w,h/2,batch,group)
			self.s_cidle.hide()
		super().__init__(x,y,w,h,c,batch,group)
	def set_boundaries(self,w,h):
		self.wb=w
		self.hb=h
	def checkKey(self,k,prsd):
		if k==k_LEFT:
			self.l=prsd
		elif k==k_RIGHT:
			self.r=prsd
		elif k==k_DOWN:
			self.d=prsd
		elif k==k_UP:
			self.u=prsd
		elif k==k_CROUCH:
			self.sh=prsd
	def cycle(self):
		#reset speed
		self.spdx=self.spdy=0
		#slowdown on crouch
		if self.sh:
			if self.bh==None:
				self.bh=self.h
				self.set_size(self.w,self.h/2)
			acc=5
		else:
			if self.bh!=None:
				self.set_size(self.w,self.bh)
				self.bh=None
			acc=10
		if abs(self.l-self.r)+abs(self.u-self.d)>1:
			acc=math.sqrt(2*acc**2)/2
		#moving on button press
		if self.l:
			self.spdx-=acc
		if self.r:
			self.spdx+=acc
		if self.u:
			self.spdy+=acc
		if self.d:
			self.spdy-=acc
		if self.spdx!=0 or self.spdy!=0:
			if self.s_crawl and self.sh:
				self.s_crawl.cycle()
				self.a=self.s_crawl
			elif self.s_walk and not self.sh:
				self.s_walk.cycle()
				self.a=self.s_walk
			else:
				self.a=None
			self.move(self.spdx,self.spdy)
		else:
			if self.s_cidle and self.sh:
				self.s_cidle.cycle()
				self.a=self.s_cidle
			elif self.s_idle and not self.sh:
				self.s_idle.cycle()
				self.a=self.s_idle
			else:
				self.a=None
		if self.spdx<0:
			self.flipped=True
		elif self.spdx>0:
			self.flipped=False
		#repecting boundaries
		if self.x<0:
			x=0
		elif self.x+self.w>self.wb:
			x=self.wb-self.w
		else:
			x=None
		if self.y<0:
			y=0
		elif self.y+self.h>self.hb:
			y=self.hb-self.h
		else:
			y=None
		if not (x==None and y==None):
			self.set_pos(x if x!=None else self.x,y if y!=None else self.y)
		if self.a:
			self.a.set_pos(self.x,self.y)
		else:
			self.rendered=False
	def draw(self):
		if self.a:
			self.a.nn()
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
			self.vl=None
		if self.a==None:
			self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,self.group,self.quad,self.cquad)
		else:
			if CONF.showcoll:
				self.vl=self.batch.add(4,pyglet.gl.GL_LINE_LOOP,self.group,self.quad,("c3B",(255,0,0)*4))
			if (self.flipped and not self.a.flipped) or (not self.flipped and self.a.flipped):
				self.a.flip()
		if self.preva!=self.a:
			if self.preva:
				self.preva.hide()
			if self.a:
				self.a.show()
			self.preva=self.a

class Bullet1(PhysEntity):
	def __init__(self,x,y,w,h,target,wait,c,img,dmg,batch,group):
		self.sprt=img.get(x,y,w,h,batch,group) if img else None
		super().__init__(x,y,w,h,c,batch,group)
		self.dmg=dmg
		self.target=target
		self.wait=wait
	def set_speed(self,x,y):
		self.spdx=x
		self.spdy=y
		if self.sprt:
			if x==0:
				if y==0:
					rot=0
				elif y>0:
					rot=90
				else:
					rot=-90
			elif x>0:
				rot=-degrees(math.atan(y/x))
			else:
				rot=degrees(math.atan(y/x))-180
			self.sprt.set_rotation(rot)
	def cycle(self):
		if self.sprt:
			self.sprt.cycle()
		if self.wait>0:
			self.wait-=1
			#calculate direction only before shooting to stay fair
			spdx=self.x-self.target.x
			spdy=self.y-self.target.y
			d=-10/math.sqrt(spdx**2+spdy**2)
			spdx*=d
			spdy*=d
			if spdx!=self.spdx or spdy!=self.spdy:
				self.set_speed(spdx,spdy)
		else:
			self.move(self.spdx,self.spdy)
	def draw(self):
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
			self.vl=None
		if self.sprt:
			if CONF.showcoll:
				self.vl=self.batch.add(4,pyglet.gl.GL_LINE_LOOP,self.group,self.quad,self.cquad)
		else:
			self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,self.group,self.quad,self.cquad)

print("defined entities")
