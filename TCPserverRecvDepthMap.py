#This script creates a TCP/IP socket server on port 5002.
#It receives depth map data from the python client running in blender.
#The data is formatted as unsigned short
#When the socket is closed by the client, it takes the last depth map
#It creates a pyplot graph using color to indicate depth in the depth map
#It then picks 20 random points and runs a simple-dumb plane detection alg

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import socket
import numpy
import math
import array

TCP_IP = '127.0.0.1'
TCP_PORT = 5002
BUFFER_SIZE = 128  # Normally 1024, but we want fast response

depthbuf = array.array('H')
dummybuf = []

n=1

fovDeg = 45
AspectRatio = 640/480

xpts = 128
ypts = 64

pointcloud = numpy.zeros((xpts,ypts,4))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print('Connection address:', addr)
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    #print("received data:", data)
    if (data == b'Initiali'):
        print('Recvd init cmd')
    elif (data == b'newframe'):
        print('new frame data')
        print(n)
        n = n + 1
        #print(depthbuf)
        print(len(depthbuf))
        if (len(depthbuf) == xpts*ypts):
            depthbuf = numpy.asarray(depthbuf, 'float')
            DBarray = numpy.reshape(depthbuf,(xpts,ypts))
            DBarray = (DBarray*23/65535)
            
            for pointX in range(0,xpts):
                for pointY in range(0,ypts):
                    #pointX = pontX*8
                    #pointY = pontY*8
                    CamZdist = float(DBarray[pointX][pointY])
                    
                    thetaX = (-fovDeg/2)+(fovDeg*pointX/xpts)
                    thetaY = (-fovDeg/(2*AspectRatio))+(fovDeg*pointY/(ypts*AspectRatio))
                    
                    PhiZX = math.radians(90-abs(thetaX))
                    PhiZY = math.radians(90-abs(thetaY))
                    
                    a1 = pow((1/math.tan(PhiZX)),2)
                    a2 = pow((1/math.tan(PhiZY)),2)
                    PhiZ = math.atan(1/math.sqrt(a1 + a2))
                    
                    Zpos = CamZdist * math.sin(PhiZ)
                    Xpos = Zpos * math.cos(PhiZ) * math.cos(math.atan2(thetaY,(thetaX+0.0001)))
                    Ypos = Zpos * math.cos(PhiZ) * math.sin(math.atan2(thetaY,(thetaX+0.0001)))
                    
                    pointcloud[pointX][pointY][0] = Xpos
                    pointcloud[pointX][pointY][1] = Ypos
                    pointcloud[pointX][pointY][2] = Zpos
                    pointcloud[pointX][pointY][3] = CamZdist
        
        depthbuf = array.array('H')
        dummybuf = []
    else:
        dummybuf = array.array('H')
        dummybuf.frombytes(data)
        depthbuf.extend(dummybuf)
conn.close()

#Plot the last point cloud received
fig1 = plt.figure()
ax1 = fig1.add_subplot(111, aspect='equal')
for column in range(0, xpts):
    for row in range(0,ypts):
        ax1.add_patch(
            patches.Rectangle(
                ((column/xpts), (row/ypts)),   # (x,y)
                1/xpts,          # width
                1/ypts,          # height
                0,
                color=str(1-(DBarray[column][row])/23)
            )
        )


#Plane detection part
planelist = []
planelist.append({'Vector' : [0,0,0], 'Origin' : [0,0,0], 'NumberofPoints' : 0})

for i in range(0,20):
    x = numpy.random.randint(1, xpts-1)
    y = numpy.random.randint(1, ypts-1)
    
    v1x = pointcloud[x-1][y][0]-pointcloud[x+1][y][0]
    v1y = pointcloud[x-1][y][1]-pointcloud[x+1][y][1]
    v1z = pointcloud[x-1][y][2]-pointcloud[x+1][y][2]
    
    v2x = pointcloud[x][y-1][0]-pointcloud[x][y+1][0]
    v2y = pointcloud[x][y-1][1]-pointcloud[x][y+1][1]
    v2z = pointcloud[x][y-1][2]-pointcloud[x][y+1][2]
    
    v1 = [v1x, v1y, v1z]
    v2 = [v2x, v2y, v2z]
    
    v1 = v1/numpy.linalg.norm(v1)
    v2 = v2/numpy.linalg.norm(v2)
    
    XprodVect = numpy.cross(v1,v2)
    
    point = pointcloud[x][y]
    foundPlaneMatch = 0
    #newplanelist = planelist    
    
    for plane in planelist:
        planedifx = point[0] - plane['Origin'][0]
        planedify = point[1] - plane['Origin'][1]
        planedifz = point[2] - plane['Origin'][2]
        
        PlaneDifVect = [planedifx, planedify, planedifz]
        PlaneDifVect = PlaneDifVect/numpy.linalg.norm(PlaneDifVect)        
        
        Vcosine = abs(numpy.dot(plane['Vector'], PlaneDifVect))
        
        VectDifX = abs(XprodVect[0] - plane['Vector'][0])
        VectDifY = abs(XprodVect[1] - plane['Vector'][1])
        VectDifZ = abs(XprodVect[2] - plane['Vector'][2])
        
        if ((Vcosine + VectDifX + VectDifY + VectDifZ) < 0.5):
            foundPlaneMatch = 1
            print('point added to plane.')
            plane['NumberofPoints'] += 1
            break
            #print(plane)
    
    if (foundPlaneMatch == 0):
        print('new plane added')
        print(len(planelist))
        planelist.append({'Vector':XprodVect, 'Origin':point, 'NumberofPoints':1})

print(planelist)
    