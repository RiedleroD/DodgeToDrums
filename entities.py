#!/usr/bin/python3
from containers import MEDIA,Sprite,LVLS
from CONSTANTS import *

class Point:
	def __init__(self,x,y):
		self.x=x
		self.y=y

class Entity(Point):
	vl=None
	def __init__(self,x,y,w,h,anch=0,batch=None,group=None):
		self.w=w
		self.h=h
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
	def get_posss(self):
		x=self.x
		_x=self._x
		y=self.y
		_y=self._y
		return (x,y,x,_y,_x,_y,_x,y)
	def get_poss(self):
		return (self.x,self.y,self._x,self._y)
	def get_bb(self):
		return (self.x,self.y,self.w,self.h)
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
			self.sprite.cycle()
		else:
			self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,self.group,self.quad,self.cquad)

class Label(Entity):
	label=None
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
	def press(self,silent=False):
		if not self.pressed:
			if not silent:
				MEDIA.click.play().volume=CONF.volsfx*CONF.volmaster
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
			self.psprit.show()
		elif self.sprite and not self.pressed:
			self.sprite.show()
		else:
			if self.w>0 and self.h>0:
				self.vl=self.batch.add(4,pyglet.gl.GL_QUADS,self.group,self.quad,self.cquad)

class ButtonSwitch(Button):
	def checkpress(self,x,y):
		if self.doesPointCollide(x,y):
			if self.pressed:
				MEDIA.click.play().volume=CONF.volsfx*CONF.volmaster
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
	def press(self,silent=False):
		if not silent:
			MEDIA.click.play().volume=CONF.volsfx*CONF.volmaster
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
	def press(self,silent=False):
		if not self.pressed:
			if not silent:
				MEDIA.click.play().volume=CONF.volsfx*CONF.volmaster
			self.pressed=True
			self.setText(f"[{self.keyname(self.val)}]")
			self.setBgColor((255,255,255,255))
			return pyglet.event.EVENT_HANDLED
	def release(self):
		if self.pressed:
			MEDIA.click.play().volume=CONF.volsfx*CONF.volmaster
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
	def press(self,x,y,silent=False):
		self.pressed=True
		perc=(x-self.x)/(self.w-1)
		if perc>1:
			perc=1
		self.perc=perc
		self.setText(f"{self.desc}:{int(perc*100)}%")
		self.rendered=False
		return pyglet.event.EVENT_HANDLED
	def release(self):
		MEDIA.click.play().volume=CONF.volsfx*CONF.volmaster
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
	pressed=False
	def __init__(self,x,y,w,h,lvls,keynxt,keyprv,keyok,selected=0,size=16,batch=None,group=None):
		self.lvls=lvls
		self.lvli=len(lvls)
		self.curlv=selected
		self.keynxt=keynxt
		self.keyprv=keyprv
		self.keyok=keyok
		self.b=b=(w+h)/50
		GRou=GRs[GRs.index(group)+1]
		self.sprts=[lv.img.get(x+b*2,y+b*2,w-b*4,h-b*4,batch,group) for i,lv in enumerate(self.lvls)]
		self.progrmid=MEDIA.progrmid.get(x+b*2,y+h,w-b*4,BTNHEIGHT*1.25,batch,group)
		self.progrleft=MEDIA.progrleft.get(x,y+h,b*2,BTNHEIGHT*1.25,batch,group)
		self.progrright=MEDIA.progrright.get(x+w-b*2,y+h,b*2,BTNHEIGHT*1.25,batch,group)
		self.progrfill=MEDIA.progrfill.get(x+b*2,y+h,0,BTNHEIGHT*1.25,batch,GRou)
		self.sign=MEDIA.sign.get(x,y-BTNHEIGHT*2.5,w,BTNHEIGHT*4,batch,group)
		super().__init__(x,y,w,h,lvls[selected].name if self.lvli>0 else "No Levels were found",color=(0,0,0,255),bgcolor=(255,255,255,255),size=size,batch=batch,group=GRou)
		self.label.anchor_x=ANCHORSx[1]
		self.label.anchor_y=ANCHORSy[2]
	def setBgColor(self,colr):
		self.cquad=("c4B",colr*16)
	def checkKey(self,key):
		if key==self.keynxt and self.curlv+1<self.lvli:
			MEDIA.click.play().volume=CONF.volsfx*CONF.volmaster
			self.curlv+=1
			self.rendered=False
			self.setText(self.lvls[self.curlv].name)
			return pyglet.event.EVENT_HANDLED
		elif key==self.keyprv and self.curlv>0:
			MEDIA.click.play().volume=CONF.volsfx*CONF.volmaster
			self.curlv-=1
			self.rendered=False
			self.setText(self.lvls[self.curlv].name)
			return pyglet.event.EVENT_HANDLED
		elif key==self.keyok:
			self.setText("")
			self.sign=MEDIA.signp.get(self.x,self.y-BTNHEIGHT*2.5,self.w,BTNHEIGHT*4,self.batch,self.group)
			self.pressed=None
			return pyglet.event.EVENT_HANDLED
	def checkpress(self,x,y):
		pass
	def render(self):
		self.label.x=self.cx
		self.label.y=self.y-BTNHEIGHT/3
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
		try:
			curlv=LVLS.lvls[self.curlv]
		except IndexError:
			pass
		else:
			self.progrfill.set_size((self.w-self.b*4)*(max(curlv.progr)/curlv.len),BTNHEIGHT*1.25)
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		if self.vl:
			self.vl.delete()
		if self.pressed==None:
			if self.sign:
				if self.sign.cycle()+1==self.sign.lens:
					self.pressed=True
					self.sign.hide()
			else:
				self.pressed=True
		else:
			if self.sign:
				self.sign.cycle()
		self.vl=self.batch.add(16,pyglet.gl.GL_QUADS,self.group,self.quad,self.cquad)
	def __del__(self):
		if self.vl:
			self.vl.delete()
		if self.label:
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
			self.btns[selected].press(silent=True)
		super().__init__(x,y,w,h,anch,batch=batch,group=group)
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

class Hooman(PhysEntity):
	l=False
	r=False
	u=False
	d=False
	sh=False#shift → crouch
	xb=None#minimum possible x pos
	yb=None#minimum possible y pos
	_xb=None#maximum possible x pos
	_yb=None#maximum possible y pos
	bh=None#holds the base height when crouching
	s_side=None
	s_up=None
	s_down=None
	s_idle=None
	s_cside=None
	s_cup=None
	s_cdown=None
	s_cidle=None
	s_death=None
	s_hurt=None#hurt sound
	a=None
	preva=None
	flipped=False
	lives=4
	dead=False#gets set to True once the death animation finishes
	lasthit=0
	apl=None#audio player
	prvt=0#previous cycle time
	def __init__(self,x,y,w,h,c,batch,group):
		for anim in ("side","up","down","idle","death","cside","cup","cdown","cidle"):
			img=getattr(MEDIA,anim,None)
			if anim.startswith('c'):
				_h=h/2
			else:
				_h=h
			if img:
				setattr(self,f"s_{anim}",img.get(x,y,w,_h,batch,group,visible=False))
		self.s_hurt=MEDIA.hurt
		super().__init__(x,y,w,h,c,batch,group)
	def lose_life(self):
		t=time()
		if t>self.lasthit+1.5:#immunity for 1.5 seconds
			self.lives-=1
			self.lasthit=t
			if self.apl:
				self.apl.next_source()
				self.apl.delete()
				self.apl=None
			if self.s_hurt:
				self.apl=self.s_hurt.play()
				self.apl.volume=CONF.volsfx*CONF.volmaster
			return True
		else:
			return False
	def set_boundaries(self,x,y,_x,_y):
		self.xb=x
		self.yb=y
		self._xb=_x
		self._yb=_y
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
	def cycle(self,t):
		#if lifeless, only play death animation
		if self.lives<=0:
			if self.a!=self.s_death:
				self.a=self.s_death
				self.a.set_pos(self.x,self.y)
				self.a.dead=0
			if self.a:
				if self.a.dead>0:
					if self.a.dead==1:
						self.dead=True
					else:
						self.a.dead-=1
				elif self.a.cycle()==self.a.lens-1:
					self.a.hide()
					self.a.dead=10
			else:
				self.dead=True
			return
		#calculate time
		td=t-self.prvt
		self.prvt=t
		#reset speed
		self.spdx=self.spdy=0
		#slowdown & half size on crouch
		if self.sh:
			if self.bh==None:
				self.bh=self.h
				self.set_size(self.w,self.h/2)
			acc=td*SIZE/3
		else:
			if self.bh!=None:
				self.set_size(self.w,self.bh)
				self.bh=None
			acc=td*SIZE/1.5
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
		if self.x<self.xb:
			x=self.xb
		elif self.x+self.w>self._xb:
			x=self._xb-self.w
		else:
			x=None
		if self.y<self.yb:
			y=self.yb
		elif self.y+self.h>self._yb:
			y=self._yb-self.h
		else:
			y=None
		if not x==y==None:
			self.set_pos(x if x!=None else self.x,y if y!=None else self.y)
		#setting the current sprite/animation position & cycle it,
		#or set rendered status to false if no sprite/animation is selected
		if self.a:
			self.a.set_pos(self.x,self.y)
			self.a.cycle()
		else:
			self.rendered=False
	def draw(self):
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
	def __del__(self):
		if self.apl:
			self.apl.next_source()
			self.apl.delete()
			self.apl=None
		if self.vl:
			self.vl.delete()

class Projectile(PhysEntity):
	dead=False
	explosive=False
	deadly=True
	prvt=0
	def __init__(self,x,y,w,h,target,c,img,t,batch,group):
		self.sprt=img.get(x,y,w,h,batch,group) if img else None
		self.x=x
		self.y=y
		if target:
			spdx,spdy=self.calc_speed(target.x,target.y,10)
		else:
			spdx=spdy=0
		super().__init__(x,y,w,h,c,batch,group,spdx,spdy)
		self.prvt=t
		self.target=target
	def doesCollide(self,ox,oy,_ox,_oy):
		x,y,_x,_y=self.get_poss()
		return not (x>_ox or _x<ox or y>_oy or _y<oy)
	def calc_speed(self,x,y,spd):
		spdx=self.x-x
		spdy=self.y-y
		d=-spd/math.sqrt(spdx**2+spdy**2)
		spdx*=d
		spdy*=d
		return spdx,spdy
	def cycle(self,t):
		td=t-self.prvt
		self.prvt=t
		if self.sprt:
			self.sprt.cycle()
		self.move(td*60*self.spdx,td*60*self.spdy)
	def render(self):
		if self.sprt:
			sx,sy,sw,sh=self.sprt.get_bb()
			if self.x!=sx or self.y!=sy:
				self.sprt.set_pos(self.x,self.y)
			if self.w!=sw or self.h!=sh:
				self.sprt.set_size(self.w,self.h)
			#for drawing the collision box when enabled
			x,y,_x,_y,x_,y_,_x_,_y_=self.get_posss()
			self.quad=('v2f',(x,y,_x,_y,_x,_y,x_,y_,x_,y_,_x_,_y_,_x_,_y_,x,y))
		else:
			#no collision box is visible since it's a square anyway when no sprite is available.
			self.quad=('v2f',self.get_posss())
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

class Bomb(Projectile):
	deadly=False
	explosive=True
	def __init__(self,x,y,w,h,target,c,img,t,exp,batch,group):
		self.bw=w
		self.bh=h
		self.spd=math.sqrt(abs(x-target.x)**2+abs(y-target.y)**2)/(60*(exp-t))
		self.exp=exp
		super().__init__(x,y,w,h,target,c,img,t,batch,group)
	def cycle(self,t):
		td=t-self.prvt
		self.prvt=t
		if t>=self.exp:
			self.dead=True
		if self.sprt:
			self.sprt.cycle()
		dist=math.sqrt(abs(self.x-self.target.x)**2+abs(self.y-self.target.y)**2)
		sz=1+math.sqrt(32*dist/(SIZE*self.spd))
		self.set_size(self.bw*sz,self.bh*sz)
		self.set_speed(*self.calc_speed(self.target.x,self.target.y,self.spd))
		self.move(td*60*self.spdx,td*60*self.spdy)

class Explosion(Projectile):
	def __init__(self,x,y,w,h,c,img,t,batch,group):
		self.exp=t+1
		super().__init__(x,y,w,h,None,c,img,t,batch,group)
	def cycle(self,t):
		if self.exp<=t:
			self.dead=True
		if self.sprt and self.sprt.visible:
			#cycle until last frame, then wait until last frame finishes, then hide animation
			if self.dead==None and self.sprt.cycle()==0:
				self.sprt.hide()
			elif self.sprt.cycle()+1==self.sprt.lens:
				self.dead=None

class ProjectileRot(Projectile):
	def __init__(self,x,y,w,h,target,c,img,t,batch,group):
		super().__init__(x,y,w,h,target,c,img,t,batch,group)
		if self.sprt:
			self.get_posss=self.sprt.get_posss
			self.get_poss=self.sprt.get_poss
			self.get_bb=self.sprt.get_bb
	def doesCollide(self,ox,oy,_ox,_oy):
		posss=self.get_posss()
		#check for every own point if it lies within the other rect
		#this doesn't check if a line cuts off a corner of the rect while staying out of it, but due to the nature of the projectiles, this is good enough.
		for x,y in zip(posss[::2],posss[1::2]):
			if ox<=x<=_ox and oy<=y<=_oy:
				return True
		return False
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

class DirectedMissile(ProjectileRot):
	def __init__(self,x,y,w,h,target,wait,c,img,t,batch,group):
		self.wait=wait
		super().__init__(x,y,w,h,target,c,img,t,batch,group)
	def cycle(self,t):
		td=t-self.prvt
		self.prvt=t
		if self.sprt:
			self.sprt.cycle()
		if self.wait>=t:
			#calculate direction only before shooting to stay fair
			spdx,spdy=self.calc_speed(self.target.x,self.target.y,10)
			if spdx!=self.spdx or spdy!=self.spdy:
				self.set_speed(spdx,spdy)
		else:
			self.move(td*60*self.spdx,td*60*self.spdy)

class HomingMissile(ProjectileRot):
	def __init__(self,x,y,w,h,target,expiration,c,img,t,batch,group):
		self.ex=expiration
		super().__init__(x,y,w,h,target,c,img,t,batch,group)
	def cycle(self,t):
		td=t-self.prvt
		self.prvt=t
		if self.sprt:
			self.sprt.cycle()
		if t>self.ex:
			self.dead=True
		spdx,spdy=self.calc_speed(self.target.x,self.target.y,4)
		if spdx!=self.spdx or spdy!=self.spdy:
			self.set_speed(spdx,spdy)
		self.move(td*60*self.spdx,td*60*self.spdy)

print("defined entities")
