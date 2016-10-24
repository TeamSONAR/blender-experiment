import bge
import bgl
import math
import socket
import bpy
import array

first = 1
TCP_IP = '127.0.0.1'
TCP_PORT = 5002
BUFFER_SIZE = 1024
MESSAGE = b"Initiali"

xpts = 128
ypts = 64

def close_socket(dummy):
    global s
    s.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

bpy.app.handlers.game_post.append(close_socket)

def myModule():
    global s
    global first
    # select the front buffer (the game window)
    bgl.glReadBuffer(bgl.GL_FRONT)
    
    # allocate 4 integers to capture the box (x,y,width,height) of the GL_FRONT
    b = bgl.Buffer(bgl.GL_INT, 4)
    #print(b)
    
    # capture the GL_FRONT bounding box
    bgl.glGetIntegerv(bgl.GL_VIEWPORT, b)
    #print(b)
    
    # allocate a buffer for the image
    pix = bgl.Buffer(bgl.GL_FLOAT, b[2] * b[3])
   
    # fill the pix array taken from the box
    #bgl.glReadPixels(b[0], b[1], b[2], b[3], bgl.GL_COLOR_INDEX, bgl.GL_BYTE, pix)
    #print(bgl.GL_IMPLEMENTATION_COLOR_READ_FORMAT_OES)
    #bgl.glReadPixels(b[0], b[1], b[2], b[3], bgl.GL_LUMINANCE, bgl.GL_FLOAT, pix)
    bgl.glReadPixels(b[0], b[1], b[2], b[3], bgl.GL_DEPTH_COMPONENT, bgl.GL_FLOAT, pix)
    
    
    wWidth = b[2]
    wHeight = b[3]
    fovDeg = 45
    AspectRatio = 640/480
    zNear = 1
    zFar = 20
    CoordList = []
    
    print('first' + str(first))
    first += 1
    s.send(b'newframe')
    for n in range(1,(xpts+1)):
        column = round(wWidth/(xpts+1))*n
        
        #columnstr = []
        ColumnStruct = array.array('H')
        
        for n2 in range(1,(ypts+1)):
            row = round(wHeight/(ypts+1)*n2)
            pixnum = (row*wWidth) + column
        
            depthSample = 2.0 * pix[pixnum] - 1.0;
            zLinear = 2.0 * zNear * zFar / (zFar + zNear - depthSample * (zFar - zNear));
            
            ThetaZX = ((fovDeg/-2)+(fovDeg*column/wWidth))
            ThetaZY = ((fovDeg/(-2*AspectRatio))+(fovDeg*row/(wHeight*AspectRatio)))
            
            PhiZX = math.radians(90-abs(ThetaZX))
            PhiZY = math.radians(90-abs(ThetaZY))
            
            a1 = pow((1/math.tan(PhiZX)),2)
            a2 = pow((1/math.tan(PhiZY)),2)
            PhiZ = math.atan(1/math.sqrt(a1 + a2))
            
            h = zLinear/math.sin(PhiZ)
            
            ColumnStruct.append(int(h*65535/23))
            
        s.send(ColumnStruct)

