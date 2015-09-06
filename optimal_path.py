import cv2.cv as cv
import time
import sys
import math
import msvcrt
import nxt.locator
from nxt.motor import *


capture =cv.CaptureFromCAM(0)

b = nxt.locator.find_one_brick()
motl=Motor(b, PORT_B)
motr=Motor(b, PORT_C)

def redimagepos(img):
    

    hsv_img=cv.CreateImage(cv.GetSize(img), cv.IPL_DEPTH_8U, 3)
    thres_img=cv.CreateImage(cv.GetSize(img),cv.IPL_DEPTH_8U, 1)
       
    
    cv.Smooth(img,img,cv.CV_BLUR,3);
    
    cv.CvtColor(img, hsv_img, cv.CV_BGR2HSV)

    hsv_min = cv.Scalar(0, 100, 100,0)
    hsv_max = cv.Scalar(10, 255,255,0)
   
    cv.InRangeS(hsv_img,hsv_min,hsv_max,thres_img)
    

    cv.Erode(thres_img,thres_img,iterations=1)

    #an image moment is a certain particular weighted average (moment) of the image pixels intensity
    mathead=cv.GetMat(thres_img,1)

    x=0
    y=0
    
    moments = cv.Moments(mathead, 0)
    area = cv.GetCentralMoment(moments, 0, 0)
    if(area > 10000):
        x = cv.GetSpatialMoment(moments, 1, 0)/area 
        y = cv.GetSpatialMoment(moments, 0, 1)/area

    return x,y;

def greenimagepos(img):
    

    hsv_img=cv.CreateImage(cv.GetSize(img), cv.IPL_DEPTH_8U, 3)
    thres_img=cv.CreateImage(cv.GetSize(img),cv.IPL_DEPTH_8U, 1)
       
    
    cv.Smooth(img,img,cv.CV_BLUR,3);
    
    cv.CvtColor(img, hsv_img, cv.CV_BGR2HSV)

    hsv_min = cv.Scalar(60, 80, 80,0)
    hsv_max = cv.Scalar(100, 255,255,0)
   
    cv.InRangeS(hsv_img,hsv_min,hsv_max,thres_img)
    

    cv.Erode(thres_img,thres_img,iterations=0)

    #an image moment is a certain particular weighted average (moment) of the image pixels intensity
    mathead=cv.GetMat(thres_img,1)

    x=0
    y=0
    
    moments = cv.Moments(mathead, 0)
    area = cv.GetCentralMoment(moments, 0, 0)
    if(area > 10000):
        x = cv.GetSpatialMoment(moments, 1, 0)/area 
        y = cv.GetSpatialMoment(moments, 0, 1)/area

    return x,y;

#wait till a character is received from keyboard
def wait():
    msvcrt.getch()


def pos(img):

    i=0
    while i==1:
        time.sleep(2)
        i=0

    x2,y2=redimagepos(img)                  #front
            
    x1,y1=greenimagepos(img)                 #back

    x=((x1+x2)/2)-640
    y=480-((y1+y2)/2)

    theta=math.degrees(math.atan2((y1-y2),(x1-x2)))
    if (theta>-180) and (theta<=90):        #1,3,4 quadrants
        theta=90-theta
    else :
        if (theta>90) and (theta<=180):     #2nd quadrant
            theta=450-theta

    theta=-theta+360

    return x,y,theta

def right(r):
    while (r>=0):    
        motl.run(20,150)
        r=r-1
    motl.brake()

def left(l):
    while (l>=0):    
        motr.run(20,150)
        l=l-1
    motr.brake()


def straight(s):
    while(s>=0):
        motl.run(10,150)
        motr.run(10,150)
        s=s-1
    motl.brake()
    motr.brake()



def caseselector(x0,y0,theta0):
    r=.06
    d=x0+r*math.cos(theta0)

     
    
    if -x0>2*r:    #Long path
     
        if theta0>0 and theta0<=90: #LP1
            print "case 1"
            n= y0-r*math.sin(theta0)+2*r
            y1=n-r
            m=-r
            
            print "position to be reached %s",d
            a=90-theta0
            a=a/360.0*1050
            print a
            right(a)         #R x-variation=x0 to a
            
            b=m-d
            b=b/.6*820
            print b
            straight(b)      #Straight x variation=a to m
            
            c=90
            c=c/360.0*1050
            print c
            left(c)           #L x-variation=m to 0
         


        if(theta0>270):                         #LP-II
            print "case 2"

            n= y0-r*math.sin(theta0)+2*r;
            y1=n-r
            m=-r                    #RSL
            
            a=90+(360-theta0)
            a=a/360*1050
            print a
            right(a)             #R x-variation=x0 to a
            
            b=m-d
            b=b/.6*820
            print b
            straight(b)          #S x variation=a to m
            
            c=90
            c=c/360*1050
            print c
            left(c);

        if(theta0>180)and(theta0<=270):         #LP-III
            print "case 3"

            n= y0+r*math.sin(theta0)
            y1=n-r
            m=-r                    #LSL

            a=90+(270-theta0)
            a=a/360*1050
            left(a)              #L  x-variation=x0 to a

            b=m-d
            b=b/.6*820
            straight(b)          #S x variation=a to m

            c=90
            c=c/360*1050
            left(c)               #L x-variation=m to 0


        if(theta0>90)and(theta0<=180):          #LP-IV
            print "case 4"

            n= y0+r*math.sin(theta0)
            y1=n-r
            m=-r                    #LSL

            a=(theta0-90)
            a=a/360*1050
            print a
            left(a)              #L  x-variation=x0 to a
            
            b=m-d
            b=b/.6*820
            print b
            straight(b)          #S x variation=a to m

            c=90
            c=c/360*1050
            print c
            left(c)               #L x-variation=m to 0

 
    if(-x0<=2*r)and(-x0>r):                     #SP
        if(theta0>0)and(theta0<=90):            #SP-I
            print "case 5"
            
            theta011=math.degrees(math.acos((-x0-r)/r))
            if(theta0> theta011):       #RSL
                n= y0-r*math.sin(theta0)+2*r
                y1=n-r
                m=-r
                right(a,y1)         #R x-variation=x0 to a
                straight(m,y1)      #S x variation=a to m
                left(0,n)           #L x-variation=m to 0
            if(theta0==90):         #SL
                n= y0+r
                y1=n-r
                m=-r
                straight(m,y0)      #S x variation=x0  to m
                left(0,n)           #L x-variation=m to 0

            if(theta0<=theta011):   #RL1
                gamma1a=math.degrees(math.acos((x0+r+r*math.cos(theta0)/(2*r))))
                n= y0-(r*math.sin(theta0))+2*r*math.sin(gamma1a)
                y1=n-r*math.sin(gamma1a)
                m=-r
                x1=r*math.cos(gamma1a)-r
                right(x1,y1)        #R x-variation=x0 to x1
                left(0,n)           #L1 x-variation=x1 to 0


        if(theta0>270):                         #SP-II
            print "case 6"

            theta021=-math.degrees(math.acos((-x0-r)/r))
            if(theta0<theta021):    #RSL
                n= y0-r*math.sin(theta0)+2*r
                y1=n-r
                m=-r
                right(a,y1)         #R x-variation=x0 to a
                straight(m,y1)      #S x variation=a to m
                left(0,n)           #L x-variation=m to 0

            if(theta0>=theta021):   #RL1
                gamma1a=math.degrees(math.acos((x0+r+r*math.cos(theta0)/(2*r))))
                n= y0-(r*math.sin(theta0)+2*r*sin(gamma1a))
                y1=n-r*math.sin(gamma1a)
                m=-r
                x1=r*math.cos(gamma1a)-r
                right(x1,y1)        #R x-variation=x0 to x1
                left(0,n)           #L1 x-variation=x1 to 0


        if((theta0>180)and(theta0<=270)):        #SP-III
            theta031=-180+math.degrees((-x0-r)/r)
            if(theta0>theta031):    #LSL
                n= y0+(r*math.sin(theta0))
                y1=n-r
                m=-r                            
                left(a,y1)          #L  x-variation=x0 to a
                straight(m,y1)      #S x variation=a to m
                left(0,n)           #L x-variation=m to 0


            if(theta0==theta031):

                n= y0+(r*math.sin(theta031))
                m=-r                #L
                left(0,n)           #L x-variation=x0  to 0

            if(theta0<theta031):    #RL2
                gamma1b=-180+math.degrees(math.acos((-x0-r-r*math.cos(theta0))/(2*r)))
                n= y0-(r*math.sin(theta0))+2*r*math.sin(gamma1b)
                y1=n-r*math.sin(gamma1b)
                m=-r
                x1=r*math.cos(gamma1b)-r
                right(x1,y1)        #R x-variation=x0 to x1
                left(0,n)           #L2 x-variation=x1 to 0

        if((theta0>90)and(theta0<=180)):        #SP IV
            theta041=180-math.degrees(math.acos((-x0-r)/r))
            if(theta0<theta041):    #LSL
                n= y0+(r*math.sin(theta0))
                y1=n-r
                m=-r
                left(a,y1)          #L  x-variation=x0 to a
                straight(m,y1)      #S x variation=a to m
                left(0,n)           #L x-variation=m to 0


            if(theta0==theta041):    #L
                n= y0+(r*math.sin(theta041))
                m=-r
                left(0,n)           #L x-variation=x0  to 0


            if(theta0>theta041):    #LR1
                gamma2a=math.degrees(math.acos((-x0+r+r*cos(theta0))/(2*r)))
                n= y0+(r*math.sin(theta0))+2*r*math.sin(gamma2a)
                y1=n-r*math.sin*(gamma2a)
                m=-r
                x1=r-r*math.cos(gamma2a)
                left(x1,y1)         #L x-variation=x0 to x1
                right(0,n)          #R1 x-variation=x1 to 0

    else:                       
        if(-x0<r):                              #VSP      
            theta012=math.degree(math.acos((r+x0)/r))
            if(theta0<theta012):                #VSP I       #RL1
                gamma1a=math.degrees(math.acos((x0+r+r*math.cos(theta0))/(2*r)))
                n= y0-(r*math.sin(theta0))+2*r*math.sin(gamma1a)
                y1=n-r*math.sin(gamma1a)
                m=-r
                x1=r*math.cos(gamma1a)-r
                right(x1,y1)        #R x-variation=x0 to x1
                left(0,n)           #L1 x-variation=x1 to 0
    

            if(theta0==theta012):    #L
                n= y0+(r*math.sin(theta012))
                m=-r
                left(0,n)           #L x-variation=x0  to 0

            if(theta0>theta012):    #LR1
                gamma2a=math.degrees(math.acos((-x0+r+r*math.cos(theta0))/(2*r)))
                n= y0+(r*math.sin(theta0))+2*r*math.sin(gamma2a)
                y1=n-r*math.sin(gamma2a)
                m= r
                x1=r-r*math.cos(gamma2a)
                left(x1,y1)         #L x-variation=x0 to x1
                right(0,n)          #R1 x-variation=x1 to 0

        if(theta0>270):                         #VSP II       #RL1
            gamma1a=math.degrees(math.acos((x0+r+r*math.cos(theta0))/(2*r)))
            n= y0-(r*math.sin(theta0))+2*r*math.sin(gamma1a)
            y1=n-r*math.sin(gamma1a)
            m=-r
            x1=r*math.cos(gamma1a)-r
            right(x1,y1)            #R x-variation=x0 to x1
            left(0,n)               #L1 x-variation=x1 to 0

        if((theta0>180)and(theta0<=270)):       #VSP III
            theta032=-180+math.degrees(math.acos((x0+r)/r))
            if(theta0<theta032):    #RL2
                gamma1b=-180+math.degrees(math.acos((-x0-r-r*math.cos(theta0))/(2*r)))
                n= y0-(r*math.sin(theta0))+2*r*math.sin(gamma1b)
                y1=n-r*math.sin(gamma1b)
                m=-r
                x1=r*math.cos(gamma1b)-r
                right(x1,y1)        #R x-variation=x0 to x1
                left(0,n)           #L2 x-variation=x1 to 0

            if(theta0>=theta032):   #RL1
                gamma1a=math.degrees(math.acos((x0+r+r*math.cos(theta0))/(2*r)))
                n= y0-(r*math.sin(theta0))+2*r*math.sin(gamma1a)
                y1=n-r*math.sin(gamma1a)
                m=-r
                x1=r*math.cos(gamma1a)-r
                right(x1,y1)        #R x-variation=x0 to x1
                left(0,n)           #L1 x-variation=x1 to 0

        if((theta0>90)and(theta0<=180)):        #VSP IV #LR1
                gamma2a=math.degrees(math.acos((-x0+r+r*math.cos(theta0))/(2*r)))
                n= y0+(r*math.sin(theta0))+2*r*math.sin(gamma2a)
                y1=n-r*math.sin(gamma2a)
                m=r
                x1=r-r*math.cos(gamma2a)
                left(x1,y1)         #L x-variation=x0 to x1
                right(0,n)          #R1 x-variation=x1 to 0


if __name__ == '__main__':


    #img=cv.LoadImage("ddd.jpg")
    img=cv.QueryFrame(capture)

    calib=100                   #the value of pixel equal to .6 meter, make it as a floating data    x0,y0,theta0=pos(img)
    #theta0=270
    #while theta0==270 &(theta0>314&theta0<315):

     #   x0,y0,theta0=pos(img)
      #  cv.WaitKey(50)
    x0,y0,theta0=-200,-400,45
    x0=x0/calib*.6
    y0=y0/calib*.6
    print x0,y0,theta0
    caseselector(x0,y0,theta0);
    
    wait()
