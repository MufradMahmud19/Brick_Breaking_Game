from OpenGL.GL import *
from OpenGL.GLUT import *
from random import uniform as rnd, randrange, choices
from time import time

WIDTH,HEIGHT = 700,700
FPS=60
score=0
gameover=False
n=int(input("Enter number of balls: ")) # number of balls
tl= 6 #2.97

def findzone(x1,y1,x2,y2):
    dx,dy=x2-x1,y2-y1
    dX,dY=abs(dx),abs(dy)
    if dx>=0 and dy>=0:
        return 0 if dX>dY else 1
    if dx<=0 and dy>=0:
        return 3 if dX>dY else 2
    if dx<=0 and dy<=0:
        return 4 if dX>dY else 5
    if dx>=0 and dy<=0:
        return 7 if dX>dY else 6
def toZone0(x,y,z):
    if z==1: return y,x
    if z==2: return y,-x
    if z==3: return -x,y
    if z==4: return -x,-y
    if z==5: return -y,-x
    if z==6: return -y,x
    if z==7: return x,-y
    return x,y
def toOriginalZone(x,y,z):
    if z==1: return y,x
    if z==2: return -y,x
    if z==3: return -x,y
    if z==4: return -x,-y
    if z==5: return -y,-x
    if z==6: return y,-x
    if z==7: return x,-y
    return x,y
def mpLine(x1,y1,x2,y2):
    z=findzone(x1,y1,x2,y2)
    x1,y1=toZone0(x1,y1,z)
    x2,y2=toZone0(x2,y2,z)
    dx,dy=x2-x1,y2-y1
    d=2*dy-dx
    incE,incNE=2*dy,2*(dy-dx)
    y=y1
    glBegin(GL_POINTS)
    glColor3f(1,1,1)
    for x in range(x1,x2+1):
        glVertex2f(*toOriginalZone(x,y,z))
        if d>0:
            y+=1
            d+=incNE
        else:
            d+=incE
    glEnd()

def f(i,X,Y):
    return X+(i%2)*10,Y+(i//2)*10        # // diye row number, % diye column number

def draw(s):
    '''
        0 1
        2 3
        4 5
    '''
    digit=['01540','04','013245','0132354','02315','102354','235401','015','3245102','51023'] # [0,1,2,3,4,5,6,7,8,9]
    x,y=WIDTH-(len(str(s))+1)*11,10
    for d in str(s):
        points=[f(int(i),x,y) for i in digit[int(d)]]
        for i in range(len(points)-1):
            mpLine(*points[i],*points[i+1])
        if d!='1':
            x+=15
        else:
            x+=10

def _8way(x,y,a,b):
    for i,j in [(x,y),(x,-y),(-x,y),(-x,-y),(y,x),(-y,x),(y,-x),(-y,-x)]:
        glVertex2f(i+a,j+b)

def circle(r,a=0,b=0):
    glPointSize(3)
    glBegin(GL_POINTS)
    # glBegin(GL_LINES)
    d=1-r
    x,y=0,r
    _8way(x,y,a,b)
    while x<y:
        if d<0:
            d+=2*x+3
        else:
            y-=1
            d+=2*(x-y)+5
        x+=1
        _8way(x,y,a,b)
    glEnd()

class Brick:
    def __init__(self,x,y,w,h,color=(0,1,1)):
        self.tlX=x
        self.tlY=y
        self.w=w
        self.h=h
        self.broken=False
        self.color=color
    def destroy(self):
        self.broken=True
    def move(self):
        self.tlY+=1.5
    def draw(self):
        glColor3f(*self.color)
        glBegin(GL_POLYGON)
        glVertex2f(self.tlX,self.tlY)
        glVertex2f(self.tlX+self.w,self.tlY)
        glVertex2f(self.tlX+self.w,self.tlY+self.h)
        glVertex2f(self.tlX,self.tlY+self.h)
        glEnd()

class Ball:
    def __init__(self,r,a,b,color=(1,1,1)):
        self.r=r
        self.cx=a
        self.cy=b
        self.v=[rnd(-3,3),-3]
        self.color=color
    def update(self):
        if self.cx+self.r>=WIDTH:   # right
            self.v[0]*=-1
            self.cx= WIDTH-self.r
        elif self.cx-self.r<=0:     # left
            self.v[0]*=-1
            self.cx=self.r
        if self.cy-self.r<0:        # top
            self.v[1]*=-1
            self.cy=self.r
        # elif self.cy+self.r>HEIGHT:  # bottom
        #     self.v[1]*=-1
        #     self.cy=HEIGHT-self.r
        self.cx+=self.v[0]
        self.cy+=self.v[1]
    def draw(self):
        glColor3f(*self.color)
        circle(self.r,self.cx,self.cy)

class Paddle:
    def __init__(self,cx,ty,w,h,color=(0,1,0)): # cx= center x, ty= top y
        self.cx = cx  # center
        self.ty = ty  # top
        self.w = w  # width
        self.h = h  # height
        self.color = color # paddle er color

    def draw(self):
        glColor3f(*self.color)
        glBegin(GL_POLYGON)
        glVertex2f(self.cx-self.w/2,self.ty) # polygon er uporer left half
        glVertex2f(self.cx+self.w/2,self.ty) # polygon er uporer right half
        glVertex2f(self.cx+self.w/2,self.ty+self.h) # polygon er nicher right half
        glVertex2f(self.cx-self.w/2,self.ty+self.h) # polygon er nicher left half
        glEnd()

bricks=[]
paddle=Paddle(WIDTH//2,0.95*HEIGHT,100,11)   #paddle er x cordinate, y cordinate , width , height
balls=[Ball(9,WIDTH//2,paddle.ty-10) for i in range(n)]

def mouseMove(mx,my):
    if mx-paddle.w/2<0 or mx+paddle.w/2>WIDTH: # checking mouse screen er baire kina, mx = mouse er position, width/2 theke boro ba choto hyte parbena
        return
    paddle.cx=mx # taking mouse's x axis's value as paddle's center of x


def generateBricks():
    n=choices([1,2,3,4],[.5,.9,.7,.4])[0]
    from random import random as rn
    for i in range(n):
        x=randrange(i*WIDTH//n,(i+1)*WIDTH//n-80)
        bricks.append(Brick(x,1,80,40,(rn(),rn(),rn())))


import numpy as np
sq=[(-60,-10),(-30,-10),(-30,20),(-60,20),(40,-10),(70,-10),(70,20),(40,20)]
m=[(-45,70), (-45, 100), (60, 100), (60, 70)]
rt=np.array(
    [[1.01,0],
    [0,1.01]]       #scaling
    )@np.array([
        [0.9998,-0.0175],  #rotate 1 deg
        [0.0175,0.9998]
    ])

def finish():
    global sq,m
    for i in range(len(sq)):
        z=np.array([[sq[i][0]],[sq[i][1]]])
        ans=rt@z  # metrics multiplication
        sq[i]=[ans[0][0],ans[1][0]]

    for i in range(len(m)):
        z=np.array([[m[i][0]],[m[i][1]]])
        ans=rt@z  # metrics multiplication
        m[i]=[ans[0][0],ans[1][0]]
    conv=lambda x,y: glVertex2f(x+WIDTH/2,y+HEIGHT/2)
    glBegin(GL_QUADS)
    for p in sq:
        conv(*p)
    glEnd()
    glBegin(GL_LINE_LOOP)
    for i in m:
        conv(*i)
    glEnd()

def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    if gameover:
        finish()
    else:
        draw(score)
        for b in bricks:
            if b.broken:
                continue
            b.draw()
        for b in balls:
            b.draw()
        paddle.draw()
    glutSwapBuffers()

astart=None # animation start time

def frame(z):
    global balls,score, gameover, astart
    if gameover and time()-astart>tl:
        return
    if z%FPS==0:    #to continuously generate bricks
        z=0
        generateBricks()
    b2=[]    #to store remaining or non-broken bricks
    for br in bricks:
        # if br.broken:
        #     continue
        br.move()
        if br.tlY+br.h>paddle.ty:
            br.destroy()
    for bl in balls:
        nx=max(paddle.cx-paddle.w/2,min(paddle.cx+paddle.w/2,bl.cx))
        ny=max(paddle.ty,min(paddle.ty+paddle.h,bl.cy))
        if (bl.cx-nx)**2+(bl.cy-ny)**2<bl.r**2:
            if nx>=paddle.cx:
                bl.v[0]=abs(bl.v[0])
            else:
                bl.v[0]=-abs(bl.v[0])
            # if bl.cx!=nx: bl.v[0]*=-1
            if bl.cy!=ny: bl.v[1]*=-1

        for br in bricks:
            if br.broken:
                continue
            nx=max(br.tlX,min(br.tlX+br.w,bl.cx))
            ny=max(br.tlY,min(br.tlY+br.h,bl.cy))
            dx,dy=bl.cx-nx,bl.cy-ny
            if dx*dx+dy*dy<bl.r*bl.r:
                if bl.cx!=nx:
                    bl.v[0]*=-1
                if bl.cy!=ny:
                    bl.v[1]*=-1
                br.destroy()
                score+=1
        bl.update()
        if bl.cy-bl.r<=HEIGHT:
            b2.append(bl)
    balls=b2
    if len(balls)==0 and not gameover:
        gameover=True
        astart=time()

    glutPostRedisplay()
    glutTimerFunc(1000//FPS,frame,z+1)

def setup(w,h):
    # print(w,h)
    global WIDTH,HEIGHT
    WIDTH,HEIGHT = w,h
    glViewport(0,0,w,h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0,w,h,0,0.0,1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    paddle.ty=0.95*h

glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
glutInitWindowSize(WIDTH,HEIGHT) #window size
glutInitWindowPosition(0, 0)
glutCreateWindow(b'<----- Brick Breaking Game ----->')
# setup(WIDTH, HEIGHT)
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
glPointSize(2)
glutDisplayFunc(render)
glutPassiveMotionFunc(mouseMove)
glutTimerFunc(0,frame,0)
glutReshapeFunc(setup)
glutMainLoop()