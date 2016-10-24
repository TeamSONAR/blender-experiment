import time
import numpy
import math

def DepthMapToPC(DBarray, xpts, ypts, fovDeg, AspectRatio):
    pointcloud = numpy.zeros((xpts, ypts, 3))
    print(xpts, ypts)
    print(DBarray.shape)
    for pointX in range(0,xpts):
        for pointY in range(0,ypts):
            CamZdist = float(DBarray[pointY][pointX])
            
            thetaX = (-fovDeg/2)+(fovDeg*pointX/xpts)
            thetaY = (-fovDeg/(2*AspectRatio))+(fovDeg*pointY/(ypts*AspectRatio))
            
            PhiZX = math.radians(90-abs(thetaX))
            PhiZY = math.radians(90-abs(thetaY))
            
            a1 = pow((1/math.tan(PhiZX)),2)
            a2 = pow((1/math.tan(PhiZY)),2)
            PhiZ = math.atan(1/math.sqrt(a1 + a2))
            
            Zpos = CamZdist# * math.sin(PhiZ)
            Xpos = Zpos * math.cos(PhiZ) * math.cos(math.atan2(thetaY,(thetaX+0.0001)))
            Ypos = Zpos * math.cos(PhiZ) * math.sin(math.atan2(thetaY,(thetaX+0.0001)))
            
            pointcloud[pointX][pointY][0] = Xpos
            pointcloud[pointX][pointY][1] = Ypos
            pointcloud[pointX][pointY][2] = Zpos
            #pointcloud[pointX][pointY][3] = CamZdist
    return pointcloud
    
def FindPlanes(pointcloud, xpts, ypts, numpts, imgin):
    start_time = time.time()
    #Plane detection part
    planelist = []
    planelist.append({'Vector' : [0,0,0], 'Origin' : [0,0,0], 'NumberofPoints' : 0, 'Color':(0,0,0)})
    
    for i in range(0,numpts):
        #Pick a random point
        x = numpy.random.randint(1, xpts-1)
        y = numpy.random.randint(1, ypts-1)
        
        #Calculate two vectors:
        #1 is the vector between the 2 points to the left and right of the point,
        #2 is the vector between the 2 points above and below the point
        v1x = pointcloud[x-1][y][0]-pointcloud[x+1][y][0]
        v1y = pointcloud[x-1][y][1]-pointcloud[x+1][y][1]
        v1z = pointcloud[x-1][y][2]-pointcloud[x+1][y][2]
        
        v2x = pointcloud[x][y-1][0]-pointcloud[x][y+1][0]
        v2y = pointcloud[x][y-1][1]-pointcloud[x][y+1][1]
        v2z = pointcloud[x][y-1][2]-pointcloud[x][y+1][2]
        
        v1 = [v1x, v1y, v1z]
        v2 = [v2x, v2y, v2z]
        
        #Normalize vectors to have magnitude of 1
        v1 = v1/numpy.linalg.norm(v1)
        v2 = v2/numpy.linalg.norm(v2)
        
        #Cross the vectors to get the normal vector
        XprodVect = numpy.cross(v1,v2)
        
        point = pointcloud[x][y]
        foundPlaneMatch = 0
        #newplanelist = planelist    
        
        #Now, search through the plane list to find a plane containing 'point'
        for plane in planelist:
            #Find the vector from 'point' to the origin point of the plane
            planedifx = point[0] - plane['Origin'][0]
            planedify = point[1] - plane['Origin'][1]
            planedifz = point[2] - plane['Origin'][2]
            
            PlaneDifVect = [planedifx, planedify, planedifz]
            PlaneDifVect = PlaneDifVect/numpy.linalg.norm(PlaneDifVect)        
            
            #Get the cosine of the angle between the vector we just calculated,
            #and the normal vector calculated earlier
            #If point is in the plane, angle should be 90 so cosine should be zero
            Vcosine = 2*abs(numpy.dot(plane['Vector'], PlaneDifVect))
            
            #Now calculate the difference between the normal vector of 'point' and
            #the normal vector of this plane
            VectDifX = abs(XprodVect[0] - plane['Vector'][0])
            VectDifY = abs(XprodVect[1] - plane['Vector'][1])
            VectDifZ = abs(XprodVect[2] - plane['Vector'][2])
            
            #If 'point' is on the current plane, the sum should be zero
            #0.5 is an arbitrary constant
            if ((Vcosine + VectDifX + VectDifY + VectDifZ) < 0.5):
                foundPlaneMatch = 1
                #print('point added to plane.')
                imgin[y, x] = plane['Color']
                plane['NumberofPoints'] += 1
                break
                #print(plane)
        
        #If after looping through all the planes, this point still has not found a
        #matching plane, we create a new plane for it.
        if (foundPlaneMatch == 0):
            print('new plane added')
            print(len(planelist))
            R = numpy.random.randint(0,255)
            G = numpy.random.randint(0,255)
            B = numpy.random.randint(0,255)
            planelist.append({'Vector':XprodVect, 'Origin':point, 'NumberofPoints':1, 'Color':(R,G,B)})
    
    print(planelist)
    print("--- %s seconds ---" % (time.time() - start_time))
    return imgin