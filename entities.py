#!/usr/bin/python3
from containers import MEDIA
from CONSTANTS import *

class Entity:
	def __init__(self,x,y,w,h,anch=0,batch=None,group=None):
		self.w=w
		self.h=h
		self.set_pos(x,y,anch)
		self.rendered=False
		self.batch=batch
		self.group=group
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
	def draw(self):
		if not self.rendered:
			self.render()
		pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad)

class Overlay(Entity):
	def __init__(self,x,y,w,h,c):
		super().__init__(x,y,w,h,group=GRobg)
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
		pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad,self.cquad)

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
		if self.w>0 and self.h>0:
			pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad,self.cquad)
		if self.batch==None:
			self.label.draw()
	def __del__(self):
		self.label.delete()

class LabelMultiline(Label):
	def __init__(self,x,y,w,h,text,anch=0,color=(255,255,255,255),bgcolor=(0,0,0,0),size=12,batch=None,group=None):
		self.labels=[pyglet.text.Label(text,x=0,y=-size*1.5,color=color,font_size=size,batch=batch) for line in text.split("\n")]
		super().__init__(x,y,w,h,text,anch,color,bgcolor,size,batch,group)
		self.label.delete()
		del self.label
	def setColor(self,color):
		self.color=color
		for label in self.labels:
			label.color=self.color
	def setText(self,text):
		self.text=text
		text=text.split("\n")
		while len(self.labels)<len(text):
			self.labels.append(pyglet.text.Label("",x=0,y=-self.size*1.5,color=self.color,font_size=self.size,batch=self.batch,group=self.group))
		self.rendered=False
		for label in reversed(self.labels):
			try:
				label.text=text.pop()
			except IndexError:
				label.text=""
	def render(self):
		if self.w>0 and self.h>0:
			self.quad=('v2f',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
			for i,label in enumerate(self.labels):
				label.x=self.cx
				label.y=self.cy+self.size*(len(self.labels)-i-1)*1.5
				label.anchor_x=ANCHORSx[1]
				label.anchor_y=ANCHORSy[1]
		else:
			for i,label in enumerate(self.labels):
				label.x=self.x
				label.y=self.y+self.size*(len(self.labels)-i-1)*1.5
				label.anchor_x=ANCHORSx[self.anch%3]
				label.anchor_y=ANCHORSy[self.anch//3]
		self.rendered=True
	def draw(self):
		if not self.rendered:
			self.render()
		if self.w>0 and self.h>0:
			pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad,self.cquad)
		if self.batch==None:
			for label in self.labels:
				label.draw()
	def __del__(self):
		for label in self.labels:
			label.delete()

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
		if MEDIA.btn and batch:
			self.sprite=MEDIA.btn.get(self.x,self.y,w,h,batch,group)
		else:
			self.sprite=None
		if MEDIA.btnp and batch:
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
				pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad,self.cquad)
		if self.batch==None:
			self.label.draw()

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

class TextEdit(Button):#also unused
	def __init__(self,x,y,w,h,desc,value="",anch=0,key=None,size=12,batch=None,group=None):
		self.desc=desc
		self.value=value
		super().__init__(x,y,w,h,desc,anch,key,size,batch=batch,group=group)
	def checkKey(self,key):
		if self.pressed:
			if key==pgw.key.BACKSPACE:
				self.value=self.value[:-1]
				self.setText("[%s]"%self.value)
			elif key in (pgw.key.RETURN,pgw.key.ESCAPE):
				self.release()
			else:
				self.value+=chr(key)
				self.setText("[%s]"%(self.value))
			return pyglet.event.EVENT_HANDLED
		elif self.key!=None and key==self.key:
			return self.press()
	def press(self):
		if not self.pressed:
			self.pressed=True
			self.setText("[%s]"%self.value)
			self.setBgColor((255,255,255,255))
			return pyglet.event.EVENT_HANDLED
	def release(self):
		if self.pressed:
			self.pressed=False
			self.setText(self.desc)
			self.setBgColor((255,255,255,255))
			return pyglet.event.EVENT_HANDLED

class IntEdit(TextEdit):
	nums=("0","1","2","3","4","5","6","7","8","9")
	preval=None
	def checkKey(self,key):
		if self.pressed:
			if key==pgw.key.BACKSPACE:
				self.value=self.value[:-1]
				self.setText("[%s]"%self.value)
			elif key in (pgw.key.RETURN,pgw.key.ESCAPE):
				if len(self.value)==0:
					self.value="0"
				self.release()
			else:
				try:
					char=chr(key)
				except OverflowError:#if a weird utf-8 symbol comes rolling in. Most apparent on non-english keyboards that have ß ö ä ü ect.
					return None
				if char in self.nums:
					self.value+=chr(key)
					self.setText("[%s]"%(self.value))
			return pyglet.event.EVENT_HANDLED
		elif self.key!=None and key==self.key:
			return self.press()
	def getNum(self):
		if not self.pressed:
			self.preval=int(self.value)
		return self.preval

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
		self.quad=('v2f',(self.x,self.y,self._x,self.y,self._x,self._y,self.x,self._y))
		self.rendered=True
	def setBgColor(self,color):
		self.cquad=("c3B",color*4)
	def draw(self):
		if not self.rendered:
			self.render()
		for btn in self.btns:
			btn.draw()
	def getSelected(self):
		for i,btn in enumerate(self.btns):
			if btn.pressed:
				return i

class RadioListPaged(RadioList):
	def __init__(self,x,y,w,h,texts,pageic,anch=0,keys=None,pressedTexts=None,selected=None,size=12,batch=None,group=None):
		self.pageic=pageic
		self.page=0
		btnc=len(texts)
		btnh=h/(pageic+1)
		super().__init__(x,y,w,h,texts,anch,keys,pressedTexts,selected,size,batch,group)
		onscr=self.btns[self.page*self.pageic:(self.page+1)*self.pageic]#get buttons which should be on screen
		for i,btn in enumerate(self.btns):#correct btn position and height based on pages and set label text to none
			btn.set_size(w,btnh)
			btn.set_pos(x,y-btnh*(i%self.pageic),anch)
			if btn not in onscr:
				btn.label.text=""
		self.next=Button(x,y-btnh*pageic,w/2,btnh,"→",anch,None,size,batch=batch)
		self.prev=Button(x-w/2,y-btnh*pageic,w/2,btnh,"←",anch,None,size,batch=batch)
	def checkpress(self,x,y):
		if self.prev.checkpress(x,y):
			prsd=-1
		elif self.next.checkpress(x,y):
			prsd=1
		else:
			prsd=None
		if prsd:
			self.page+=prsd
			#make sure that self.page wraps around if too big
			self.page%=-(-len(self.btns)//self.pageic)#ceiling division
		onscr=self.btns[self.page*self.pageic:(self.page+1)*self.pageic]#get buttons which should be on screen
		if prsd:
			#remove text from all buttons that shouldn't be on screen (because the labels get rendered in batch)
			#re-add text from all buttons that should be on screen
			for btn in self.btns:
				if btn in onscr:
					btn.label.text=btn.text
				else:
					btn.label.text=""
			prsd=None
		for btn in onscr:
			prsd=btn.checkpress(x,y)
			if prsd:
				prsd=btn
				break
		if prsd!=None:
			for btn in self.btns:
				if btn is not prsd and btn.pressed:
					btn.release()
					if btn not in onscr:
						btn.label.text=""
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
	def draw(self):
		if not self.rendered:
			self.render()
		onscr=self.btns[self.page*self.pageic:(self.page+1)*self.pageic]#get buttons which should be on screen
		#draw the background plane
		pyglet.graphics.draw(4,pyglet.gl.GL_QUADS,self.quad,self.cquad)
		#draw the buttons in the current page plus prev and next
		for btn in onscr:
			btn.draw()
		self.prev.draw()
		self.next.draw()
		#releasing next & previous buttons only after drawing to show single-frame click
		if self.prev.pressed:
			self.prev.release()
		if self.next.pressed:
			self.next.release()

class PhysEntity(Entity):
	def __init__(self,x,y,w,h,c,spdx=0,spdy=0):
		super().__init__(x,y,w,h,0,None)
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
	def draw(self,batch,group=None):
		if not self.rendered:
			self.render()
		batch.add(4,pyglet.gl.GL_QUADS,group,self.quad,self.cquad)

class Wall(PhysEntity):
	def __init__(self,x,y,w,h,c):
		super().__init__(x,y,w,h,c,0,0)

class Hooman(PhysEntity):
	l=False
	r=False
	u=False
	d=False
	sh=False#shift → crouch
	wb=None#width boundary
	hb=None#height boundary
	bh=None#holds the base height when crouching
	def set_boundaries(self,w,h):
		self.wb=w
		self.hb=h
	def checkKey(self,k,prsd):
		if k in (key.LEFT,key.A):
			self.l=prsd
		elif k in (key.RIGHT,key.D):
			self.r=prsd
		elif k in (key.DOWN,key.S):
			self.d=prsd
		elif k in (key.UP,key.W):
			self.u=prsd
		elif k in (key.LSHIFT,key.RSHIFT):
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
			x=self.x if x==None else x
			y=self.y if y==None else y
			self.set_pos(x,y)

print("defined entities")
