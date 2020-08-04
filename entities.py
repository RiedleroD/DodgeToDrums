#!/usr/bin/python3
from containers import MEDIA,Sprite
from CONSTANTS import *

class Entity:
	def __init__(self,x,y,w,h,anch=0,batch=None,group=None):
		self.w=w
		self.h=h
		self.vl=None
		self.set_pos(x,y,anch)
		self.rendered=False
		self.batch=batch
		self.group=group
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
	def __init__(self,x,y,w,h,text,anch=0,key=None,size=16,pressedText=None,img=None,pimg=None,batch=None,group=None):
		self.pressed=False
		self.key=key
		if pressedText:
			self.pressedText=pressedText
			self.unpressedText=text
		else:
			self.pressedText=self.unpressedText=text
		super().__init__(x,y,w,h,text,anch,(0,0,0,255),(255,255,255,255),size,batch=batch,group=GRs[GRs.index(group)+1])
		if img:
			self.sprite=img.get(self.x,self.y,w,h,batch,group)
		elif img==0 or not MEDIA.btn:
			self.sprite=None
		else:
			self.sprite=MEDIA.btn.get(self.x,self.y,w,h,batch,group)
		if pimg:
			self.psrit=pimg.get(self.x,self.y,w,h,batch,group)
		elif pimg==0 or not MEDIA.btnp:
			self.psprit=None
		else:
			self.psprit=MEDIA.btnp.get(self.x,self.y,w,h,batch,group)
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
			return pyglet.event.EVENT_HANDLED
	def release(self):
		if self.pressed:
			self.pressed=False
			self.setText(self.unpressedText)
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

class Slider(Button):
	def __init__(self,x,y,w,h,desc,perc=1,anch=0,size=16,batch=None,group=None):
		self.perc=perc
		self.desc=desc
		self.vl1=None
		self.vl2=None
		super().__init__(x,y,w,h,f"{desc}:{int(perc*100)}%",anch=anch,key=None,size=size,img=0,pimg=0,batch=batch,group=group)
		self.setBgColor((96,96,128,255))
	def setBgColor(self,color):
		self.cquad=("c4B",color*4)
		self.cquad2=("c4B",color*8)
	def press(self,x,y):
		self.pressed=True
		perc=(x-self.x)/(self.w-1)
		if perc>1:
			perc=1
		self.perc=perc
		self.setText(f"{self.desc}:{int(perc*100)}%")
		self.rendered=False
		return pyglet.event.EVENT_HANDLED
	def release(self):
		self.pressed=False
	def checkKey(self,key):
		return None
	def checkpress(self,x,y):
		if self.doesPointCollide(x,y):
			return self.press(x,y)
	def render(self):
		_x=self.x+self.w*self.perc
		self.quad=('v2f',(self.x,self.y,_x,self.y,_x,self._y,self.x,self._y))
		self.quad2=('v2f',(self.x,self.y,self._x,self.y,self._x,self.y,self._x,self._y,self._x,self._y,self.x,self._y,self.x,self._y,self.x,self.y))
		self.label.x=self.cx
		self.label.y=self.cy
		self.label.anchor_x=ANCHORSx[1]
		self.label.anchor_y=ANCHORSy[1]
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
			self.vl=None
		if self.vl2:
			self.vl2.delete()
			self.vl2=None
		self.vl2=self.batch.add(8,pyglet.gl.GL_LINES,self.group,self.quad2,self.cquad2)
		self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,self.group,self.quad,self.cquad)
	def __del__(self):
		self.label.delete()
		if self.vl:
			self.vl.delete()
		if self.vl2:
			self.vl2.delete()

class LevelSelect(Label):
	def __init__(self,x,y,w,h,lvls,keynxt,keyprv,selected=0,size=16,batch=None,group=None):
		self.lvls=lvls
		self.lvli=len(lvls)
		self.curlv=selected
		self.keynxt=keynxt
		self.keyprv=keyprv
		self.b=b=(w+h)/50
		self.sprts=[lv.img.get(x+b*2,y+b*2,w-b*4,h-b*4,batch,group) for i,lv in enumerate(self.lvls)]
		super().__init__(x,y,w,h,lvls[selected].name,bgcolor=(255,255,255,255),size=size,batch=batch,group=group)
		self.label.anchor_x=ANCHORSx[1]
		self.label.anchor_y=ANCHORSy[2]
	def setBgColor(self,colr):
		self.cquad=("c4B",colr*16)
	def checkKey(self,key):
		if key==self.keynxt and self.curlv+1<self.lvli:
			self.curlv+=1
			self.rendered=False
			self.setText(self.lvls[self.curlv].name)
			return pyglet.event.EVENT_HANDLED
		elif key==self.keyprv and self.curlv>0:
			self.curlv-=1
			self.rendered=False
			self.setText(self.lvls[self.curlv].name)
			return pyglet.event.EVENT_HANDLED
	def checkpress(self,x,y):
		pass
	def render(self):
		self.label.x=self.cx
		self.label.y=self.y-5
		b=self.b
		x=self.x
		y=self.y
		_x=self._x
		_y=self._y
		xb=x+b
		_xb=_x-b
		yb=y+b
		_yb=_y-b
		self.quad=("v2f",(#non-filled rectangle from x,y to _x,_y with a border of width b, made out of 4 overlapping bars
			x,y,		x,yb,		_x,yb,		_x,y,#bottom bar
			_xb,y,		_xb,_y,		_x,_y,		_x,y,#right bar
			x,_y,		_x,_y,		_x,_yb,		x,_yb,#upper bar
			x,y,		xb,y,		xb,_y,		x,_y))#left bar
		for i,sprt in enumerate(self.sprts):
			sprt.set_pos(x+b*2+(self.w+b)*(i-self.curlv),self.y+b*2)
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
		self.vl=self.batch.add(16,pyglet.gl.GL_QUADS,self.group,self.quad,self.cquad)
	def __del__(self):
		if self.vl:
			self.vl.delete()
		self.label.delete()

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
	def __init__(self,x,y,w,h,c,batch,group,spdx=0,spdy=0):
		super().__init__(x,y,w,h,0,batch,group)
		self.set_speed(spdx,spdy)
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
	s_side=None
	s_up=None
	s_down=None
	s_idle=None
	s_cside=None
	s_cup=None
	s_cdown=None
	s_cidle=None
	a=None
	preva=None
	flipped=False
	def __init__(self,x,y,w,h,c,batch,group):
		for anim in ("side","up","down","idle","cside","cup","cdown","cidle"):
			img=getattr(MEDIA,anim,None)
			if anim.startswith('c'):
				_h=h/2
			else:
				_h=h
			if img:
				setattr(self,f"s_{anim}",img.get(x,y,w,_h,batch,group,visible=False))
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
			self.move(self.spdx,self.spdy)
		#choosing animation/sprite for current action
		if self.spdx!=0:
			if self.s_cside and self.sh:
				self.a=self.s_cside
			elif self.s_side and not self.sh:
				self.a=self.s_side
			else:
				self.a=None
		elif self.spdy>0:
			if self.s_cup and self.sh:
				self.a=self.s_cup
			elif self.s_up and not self.sh:
				self.a=self.s_up
			else:
				self.a=None
		elif self.spdy<0:
			if self.s_cdown and self.sh:
				self.a=self.s_cdown
			elif self.s_down and not self.sh:
				self.a=self.s_down
			else:
				self.a=None
		else:
			if self.s_cidle and self.sh:
				self.s_cidle.cycle()
				self.a=self.s_cidle
			elif self.s_idle and not self.sh:
				self.s_idle.cycle()
				self.a=self.s_idle
			else:
				self.a=None
		#determine if we should flip the current sprite/animation
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
		#setting the current sprite/animation position & cycle it,
		#or set rendered status to false if no sprite/animation is selected
		if self.a:
			self.a.set_pos(self.x,self.y)
			self.a.cycle()
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
		self.x=x
		self.y=y#calc_speed needs own coordinates set
		super().__init__(x,y,w,h,c,batch,group,*self.calc_speed(target))
		self.dmg=dmg
		self.target=target
		self.wait=wait
	def calc_speed(self,target):
		spdx=self.x-target.x
		spdy=self.y-target.y
		d=-10/math.sqrt(spdx**2+spdy**2)
		spdx*=d
		spdy*=d
		return spdx,spdy
	def set_speed(self,x,y):
		self.spdx=x
		self.spdy=y
		if self.sprt:
			if y==0:
				if x==0:
					rot=0
				elif x>0:
					rot=90
				else:
					rot=-90
			else:
				rot=math.degrees(math.atan(x/y))-(180 if y<0 else 0)
			self.sprt.set_rotation(rot)
			self.rendered=False
	def cycle(self):
		if self.sprt:
			self.sprt.cycle()
		if self.wait>0:
			self.wait-=1
			#calculate direction only before shooting to stay fair
			spdx,spdy=self.calc_speed(self.target)
			if spdx!=self.spdx or spdy!=self.spdy:
				self.set_speed(spdx,spdy)
		else:
			self.move(self.spdx,self.spdy)
	def render(self):
		if self.sprt:
			self.sprt.set_pos(self.x,self.y)
			x,y,_x,_y=self.sprt.get_poss()
			self.quad=('v2f',(x,y,_x,y,_x,y,_x,_y,_x,_y,x,_y,x,_y,x,y))
		else:
			self.quad=('v2f',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
			self.vl=None
		if self.sprt:
			if CONF.showcoll:
				self.vl=self.batch.add(8,pyglet.gl.GL_LINES,self.group,self.quad,('c3B',(255,0,0)*8))
		else:
			self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,self.group,self.quad,self.cquad)

print("defined entities")
