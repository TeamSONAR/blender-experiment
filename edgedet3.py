# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 16:51:20 2016

@author: Colin
"""

import os
from PIL import Image, ImageOps, ImageDraw
import numpy as np
from scipy import ndimage, misc
import time
import DepthMapTools as dmt
import matplotlib.pyplot as plt

def histeq(im,nbr_bins=256):
    """ Histogram equalization of a grayscale image. """
    # get image histogram
    imhist,bins = np.histogram(im.flatten(),nbr_bins,normed=True)
    cdf = imhist.cumsum() # cumulative distribution function
    cdf = 255 * cdf / cdf[-1] # normalize
    # use linear interpolation of cdf to find new pixel values
    im2 = np.interp(im.flatten(),bins[:-1],cdf)
    return im2.reshape(im.shape), cdf


ImgName = input('Image Name?')

SaveExtraImages = True

try:
    os.remove(ImgName + 'Traces.png')
    os.remove(ImgName + 'HistEq.png')
    os.remove(ImgName + 'Blurred.png')
    os.remove(ImgName + 'Final.png')
except:
    print('lol')

x = Image.open(ImgName + '.png', 'r')
print(x.size)

#=============================================================================
#load the image
y = np.asarray(x.getdata(), dtype=np.float64)
y = y.reshape((x.size[1], x.size[0]))
print(y.max())
print(y.min())
print(y.mean())
#yCopy = np.copy(y)

#MaskA = (yCopy > 254).astype(np.float64)
#misc.imsave(ImgName + 'far.png', MaskA)

#Turn depth map to point cloud, for later use
poclo = dmt.DepthMapToPC(y, x.size[0], x.size[1], 45, x.size[0]/x.size[1])

ogstart = time.time()
#=============================================================================
#use gaussian filter to get second-order derivative of points
imx = np.zeros(y.shape)
imy = np.zeros(y.shape)
sigma = 1
ndimage.filters.gaussian_filter(y, (sigma,sigma), (0,2), imx)

imx = -abs(imx)
imx = (imx > imx.mean()/4).astype(np.float64)
print(imx.mean())
if SaveExtraImages:
    misc.imsave(ImgName + 'imx.png', imx)

ndimage.filters.gaussian_filter(y, (sigma,sigma), (2,0), imy)

imy = -abs(imy)
imy = (imy > imy.mean()/4).astype(np.float64)
print(imy.mean())
if SaveExtraImages:
    misc.imsave(ImgName + 'imy.png', imy)

#=============================================================================
#combine x and y derivatives
jkfd = ((imx)+(imy))/2

#jkfd = -abs(jkfd)

if SaveExtraImages:
    misc.imsave(ImgName + 'HistEq.png', jkfd)

#jkfd,cdf = histeq(jkfd)

#misc.imsave(ImgName + 'HistEq.png', jkfd)

mult = 1

foo = np.copy(jkfd)

#=============================================================================
#blur the binary image
sigma2 = 1
ndimage.filters.gaussian_filter(foo, (0,sigma2), (0,0), jkfd)


#=============================================================================
#turn the image into a binary image, where only points above average are white
#nm = (foo.min()+foo.max())/2
#nm = 128
nm = jkfd.mean()
jkfd = (jkfd > nm).astype(np.float64)

#=============================================================================
#blur the binary image

ndimage.filters.gaussian_filter(jkfd, (sigma2,0), (0,0), jkfd)


#=============================================================================
#turn the image into a binary image, where only points above average are white

nm = jkfd.mean()
jkfd = (jkfd > nm).astype(np.float64)

if SaveExtraImages:
    misc.imsave(ImgName + 'Blurred.png', jkfd)

jmax = jkfd.max()
jmean = jkfd.mean()
print('Mean Max Min')
print(jkfd.mean())
print(jkfd.max())
print(jkfd.min())
jmean = (jmax + jmean)/2

#=============================================================================
#Do edge detection stuff

ObjectIDarray = np.zeros(jkfd.shape)
objectarray = []
ObjectEqualityList = []
ObjConList = []

for i in range(0, 1600):
    ObjectEqualityList.append(0)
    ObjConList.append([])

objlist = []
LineIndex = 0
direction = 'left'

start_time = time.time()

xGridPts = 30
yGridPts = 30

GoRight = False
GoLeft = True
GoUp = False
GoDown = True

for xpt in range(0,xGridPts):
    for ypt in range(0, yGridPts):
        x = int(((1+xpt)/(xGridPts+1))*(jkfd.shape[0]))
        y = int(((1+ypt)/(yGridPts+1))*(jkfd.shape[1]))
        
        if (jkfd[x,y] > jmean) and (ObjectIDarray[x,y] == 0):
            LineIndex += 1
            StartX = x
            StartY = y
            
            ObjectIDarray[x, y] = LineIndex
            FoundLineIndex = 0
            
            xmax = x
            #left
            af = 0
            while (jkfd[x, y] > jmean) and (x>1):
                x-=1
                if (ObjectIDarray[x,y] > 0):
                    FoundLineIndex = ObjectIDarray[x,y]
                    af = int(FoundLineIndex)
                    break
                ObjectIDarray[x,y] = LineIndex
                    
            xmin = x
            x = StartX
                    
            ymax = y
            y = StartY
            
            #down
            while (jkfd[x, y] > jmean) and (y>1):
                y-=1
                if (ObjectIDarray[x,y] > 0):
                    FoundLineIndex = ObjectIDarray[x,y]
                    break
                ObjectIDarray[x,y] = LineIndex
            
            ymin = y
            
            FoundLineIndex = int(FoundLineIndex)
            
            if (ymin < 1) or (xmin < 1):
                print('oh no')
            
            if (FoundLineIndex == 0):
                objectarray.append([xmin, xmax, ymin, ymax, 1, [[x,y, dmt.GetPointNormal(y, x, poclo)]]])
                #print(poclo[y][x])
                print(dmt.GetPointNormal(y, x, poclo))
                ObjectEqualityList[LineIndex] = len(objectarray)-1
                
            else:
                FoundObjectIndex = ObjectEqualityList[FoundLineIndex]
            
                if (af > 0):
                    FirstObjectFoundIndex = ObjectEqualityList[af]
                    if not (FirstObjectFoundIndex == FoundObjectIndex):
                        #ObjConList[FoundObjectIndex].append(ObjectEqualityList[af])
                        
                        NewObjectEqualityList = []
                        for item in ObjectEqualityList:
                            if (item == FirstObjectFoundIndex):
                                NewObjectEqualityList.append(FoundObjectIndex)
                            else:
                                NewObjectEqualityList.append(item)
                        ObjectEqualityList = NewObjectEqualityList
                              
                        if (objectarray[FirstObjectFoundIndex] != [52, 52, 52, 52, 1, []]):
                            print(objectarray[FoundObjectIndex])
                            objectarray[FoundObjectIndex][0] = min((objectarray[FoundObjectIndex][0], objectarray[FirstObjectFoundIndex][0]))
                            objectarray[FoundObjectIndex][1] = max((objectarray[FoundObjectIndex][1], objectarray[FirstObjectFoundIndex][1]))
                            objectarray[FoundObjectIndex][2] = min((objectarray[FoundObjectIndex][2], objectarray[FirstObjectFoundIndex][2]))
                            objectarray[FoundObjectIndex][3] = max((objectarray[FoundObjectIndex][3], objectarray[FirstObjectFoundIndex][3]))
                            objectarray[FoundObjectIndex][4] += objectarray[FirstObjectFoundIndex][4]
                            objectarray[FoundObjectIndex][5] += objectarray[FirstObjectFoundIndex][5]
                            #print(objectarray[FoundObjectIndex])
                            objectarray[FirstObjectFoundIndex] = [52, 52, 52, 52, 1, []]
                
                ObjectEqualityList[LineIndex] = FoundObjectIndex
                
                ObjArrayIndex = FoundObjectIndex
                
                if objectarray[ObjArrayIndex] == [52, 52, 52, 52, 1, []]:
                    print(ObjArrayIndex)
                    print('error')
                
                objectarray[ObjArrayIndex][0] = min((objectarray[ObjArrayIndex][0], xmin))
                objectarray[ObjArrayIndex][1] = max((objectarray[ObjArrayIndex][1], xmax))
                objectarray[ObjArrayIndex][2] = min((objectarray[ObjArrayIndex][2], ymin))
                objectarray[ObjArrayIndex][3] = max((objectarray[ObjArrayIndex][3], ymax))
                #print('number of things')
                objectarray[ObjArrayIndex][4] += 1
                objectarray[ObjArrayIndex][5] += [x,y, dmt.GetPointNormal(y, x, poclo)]
                #print(objectarray[ObjArrayIndex][4])
        
Fobjectarray = []
print('\n\n')
for Pobject in objectarray:
    if Pobject != [52, 52, 52, 52, 1, []]:
        Fobjectarray.append(Pobject)


#outi = Image.new("RGB", jkfd.shape, "black")
outi = Image.open(ImgName + '.bmp', 'r')
outi = outi.convert('RGB')

draw = ImageDraw.Draw(outi)

for Pobject in Fobjectarray:
    LY = Pobject[0]
    HY = Pobject[1]
    LX = Pobject[2]
    RX = Pobject[3]
    R = np.random.randint(0,255)
    G = np.random.randint(0,255)
    B = np.random.randint(0,255)
    area = (Pobject[1]-Pobject[0]) * (Pobject[3]-Pobject[2])
    if (area/Pobject[4] < 10000):
        draw.rectangle([LX, LY, RX, HY], outline=(R,G,B))
    
    print('\nsize:')
    
    #print(area)
    print((Pobject[0],Pobject[2]))
    print(area/Pobject[4])
    print(((Pobject[1]+Pobject[0])/2, (Pobject[3]+Pobject[2])/2))
    print('number of things')
    print(Pobject[4])
    
del draw
outi = outi.rotate(180)
outi.save(ImgName + 'Final.png')

print("--- %s seconds ---" % (time.time() - start_time))
print("--- %s seconds ---" % (time.time() - ogstart))
#print(ObjConList[0:10])
print(len(Fobjectarray))
if SaveExtraImages:
    misc.imsave(ImgName + 'Traces.png', ObjectIDarray)