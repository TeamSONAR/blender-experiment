# -*- coding: utf-8 -*-
"""
Created on Sat Oct  8 21:02:52 2016

@author: Colin
"""
import ctypes
import array
import numpy as np
import scipy.ndimage
import scipy.misc
import matplotlib.pyplot as plt
import DepthMapTools as dmt
import os

from PIL import Image, ImageOps

lib = ctypes.WinDLL('F:/seniorproject/Visual Studio/BlenderToDepthMapDLL/x64/Debug/BlenderToDepthMapDLL.dll')

try:
    os.remove('Bimage.png')
    os.remove('Bcontour.png')
    os.remove('Bf.png')
except:
    print('lol')

OpenDepthBufMapFile = lib[4]
ReadDepthMapBufFile = lib[5]
UnmapDepthBufFile = lib[6]

Xd = 450
Yd = 311

OpenDepthBufMapFile.restype = ctypes.c_void_p
#WriteDepthMapBufFile.argtypes = (ctypes.c_void_p, ctypes.c_short, ctypes.c_int)
HarambePointer = OpenDepthBufMapFile()

OutType = (ctypes.c_float)*(Xd*Yd)
kl = OutType()

print('roo')
ReadDepthMapBufFile.argtypes = [ctypes.c_void_p]
ReadDepthMapBufFile.restype = ctypes.c_void_p
print('lfdsijf')
Data = ReadDepthMapBufFile(ctypes.c_void_p(HarambePointer))
print('naps')
#Data = ctypes.cast(Data, ctypes.POINTER(ctypes.c_float))
#Data = ctypes.c_int(ctypes.cast(Data, ctypes.POINTER(OutType)))



DataX = Xd
DataY = Yd
print('reading array')
#addr = ctypes.addressof(Data.contents)
zv = OutType.from_address(Data)
a = np.frombuffer(zv, np.float32, Xd*Yd)
jkf = np.copy(a)
jkf = jkf.reshape((Yd,Xd))

zNear = 1
zFar = 20

z3 = 2.0 * zNear * zFar
z4 = zFar + zNear
z5 = zFar - zNear

depthSample = 2.0 * jkf - 1.0;
jkf = z3 / (z4 - depthSample * z5);

outi = Image.new("RGB", jkf.shape, "black")
pixi = outi.load()

poclo = dmt.DepthMapToPC(jkf, Xd, Yd, 45, Xd/Yd)
pixout = dmt.FindPlanes(poclo, Xd, Yd, 20000, pixi)

outi.save('Bf.png')
#scipy.misc.imsave('Bf.png', pixout)

qq = Image.fromarray(jkf, 'F')
scipy.misc.imsave('Bimage.png', qq)
#jds = a

UnmapDepthBufFile(ctypes.c_void_p(HarambePointer))
sigma = 1
#qq.show()
imx = np.zeros(jkf.shape)
#plt.imshow(jds)
scipy.ndimage.filters.gaussian_filter(qq, (sigma,sigma), (0,2), imx)
#scipy.ndimage.filters.gaussian_filter(imx, (sigma,sigma), (0,1), imx)
scipy.misc.imsave('Bcontour.png', imx)
