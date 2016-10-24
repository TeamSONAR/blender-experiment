#import bge
import bgl
import math
import socket
import bpy
import array
import time
import numpy
import ctypes


def close_fmap(dummy):
    global HarambePointer
    UnmapDepthBufFile(ctypes.c_void_p(HarambePointer))

bpy.app.handlers.game_post.append(close_fmap)
#print(bpy.app.handlers.game_post)


lib = ctypes.WinDLL('F:/seniorproject/Visual Studio/BlenderToDepthMapDLL/x64/Debug/BlenderToDepthMapDLL.dll')

CreateDepthBufMapFile = lib[1]
WriteDepthMapBufFile = lib[7]
UnmapDepthBufFile = lib[6]

CreateDepthBufMapFile.restype = ctypes.c_void_p
WriteDepthMapBufFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
HarambePointer = CreateDepthBufMapFile(0, 0)

bgl.glReadBuffer(bgl.GL_FRONT)

# allocate 4 integers to capture the box (x,y,width,height) of the GL_FRONT
b = bgl.Buffer(bgl.GL_INT, 4)

# capture the GL_FRONT bounding box
bgl.glGetIntegerv(bgl.GL_VIEWPORT, b)

pix = bgl.Buffer(bgl.GL_FLOAT, b[2] * b[3])
print((b[2],b[3]))
print((b[2]*b[3]))

def ReadOutDepthMap():
    global HarambePointer
    global b
    global pix
    
    start_time = time.time()
    # select the front buffer (the game window)
    bgl.glReadPixels(b[0], b[1], b[2], b[3], bgl.GL_DEPTH_COMPONENT, bgl.GL_FLOAT, pix)
    
    jj = (ctypes.c_float * len(pix))()
    jj[:] = pix
    kfj = ctypes.pointer(jj)
    
    WriteDepthMapBufFile(ctypes.c_void_p(HarambePointer), kfj, len(jj))
    
    print("--- %s seconds ---" % (time.time() - start_time))

