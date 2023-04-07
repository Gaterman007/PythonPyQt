from enum import Enum
import glm
import numpy as np
import math
from Ray import *

        
class Plane():
    def __init__(self,pointOnPlane = glm.vec3(0.0,0.0,0.0),normal = glm.vec3(0.0,-1.0,0.0) ):
        self.pointOnPlane = pointOnPlane
        self.normal = normal

    # testpoint is glm.vec3
    def isPointOnPlane(self,testpoint):
        vectotestpoint = testpoint - self.pointOnPlane
        testresult = glm.dot(vectotestpoint,self.normal)
        if glm.abs(testresult) < 0.0001:
            return True # on the plane
        else:
            return False

    def testRay(self, camRay = Ray()):
        n_dot_d = glm.dot(self.normal,camRay.rayDirection)
        if glm.abs(n_dot_d) < 0.0001:
            return False
        n_dot_ps = glm.dot(self.normal,self.pointOnPlane - camRay.startPoint)
        camRay.t = n_dot_ps / n_dot_d
        planePoint = camRay.startPoint + camRay.t * camRay.rayDirection
        return planePoint

          
#class TriangleTest():
#    # glm vec3 for pointA pointB pointC
#    def __init__(self,Point_A = glm.vec3( 1.0,1.0,0.0),Point_B = glm.vec3(-1.0,1.0,0.0),Point_C = glm.vec3( 0.0,0.0,0.0)):
#        self.triPoint_A = Point_A
#        self.triPoint_B = Point_B
#        self.triPoint_C = Point_C
#        self.normal = glm.cross(Point_B - Point_A,Point_C - Point_A)
##        self.triPoint_A = glm.vec3( 1.0,1.0,0.0)
##        self.triPoint_B = glm.vec3(-1.0,1.0,0.0)
##        self.triPoint_C = glm.vec3( 0.0,0.0,0.0)
#        
#    def testRay(self , camRay = Ray()):
#        plane = Plane(self.triPoint_A,self.normal)
#        n_dot_d = glm.dot(self.normal,camRay.rayDirection)
#        if glm.abs(n_dot_d) < 0.0001:
#            return False
#        n_dot_ps = glm.dot(self.normal,self.triPoint_A - camRay.startPoint)
#        camRay.t = n_dot_ps / n_dot_d
##        planePoint = camRay.startPoint + camRay.t * camRay.rayDirection
#        planePoint = camRay.pointFromRay()
#        AtoB_Edge = triPoint_B - triPoint_A
#        BtoC_Edge = triPoint_C - triPoint_B
#        CtoA_Edge = triPoint_A - triPoint_C
#        AtoPoint = planePoint - triPoint_A
#        BtoPoint = planePoint - triPoint_B
#        CtoPoint = planePoint - triPoint_C
#        ATestVec = glm.cross(AtoB_Edge,AtoPoint)
#        BTestVec = glm.cross(BtoC_Edge,BtoPoint)
#        CTestVec = glm.cross(CtoA_Edge,CtoPoint)
#        AtestVecMatchNormal = glm.dot(ATestVec,self.normal) > 0.0
#        BtestVecMatchNormal = glm.dot(BTestVec,self.normal) > 0.0
#        CtestVecMatchNormal = glm.dot(CTestVec,self.normal) > 0.0
#        hitTriangle = AtestVecMatchNormal and BtestVecMatchNormal and CtestVecMatchNormal
#        return hitTriangle
        
            
class CameraBehavior(Enum):
    FIRST_PERSON = 1
    SPECTATOR = 2
    FLIGHT = 3
    ORBIT = 4


SPEED = 4.0

# SENSITIVITY and DEFAULT_ROTATION_SPEED have the same objective for rotation with mouse
SENSITIVITY = 0.01
DEFAULT_ROTATION_SPEED = 0.3


DEFAULT_FOVX = 10.0
DEFAULT_ZNEAR = 0.1
DEFAULT_ZFAR = 500.0

DEFAULT_ORBIT_MIN_ZOOM = DEFAULT_ZNEAR + 1.0
DEFAULT_ORBIT_MAX_ZOOM = DEFAULT_ZFAR * 0.5

DEFAULT_ORBIT_OFFSET_DISTANCE = DEFAULT_ORBIT_MIN_ZOOM + (DEFAULT_ORBIT_MAX_ZOOM - DEFAULT_ORBIT_MIN_ZOOM) * 0.25

WORLD_XAXIS = glm.vec3(1.0, 0.0, 0.0);
WORLD_YAXIS = glm.vec3(0.0, 1.0, 0.0);
WORLD_ZAXIS = glm.vec3(0.0, 0.0, 1.0);


CAMERA_ZOOM_MAX = 5.0
CAMERA_ZOOM_MIN = 1.5

CAMERA_SPEED_FLIGHT_YAW = 100.0
CAMERA_SPEED_ORBIT_ROLL = 100.0

CAMERA_ACCELERATION = glm.vec3(4.0, 4.0, 4.0);
CAMERA_VELOCITY = glm.vec3(1.0, 1.0, 1.0);


class Camera:
    def __init__(self, oglFrame, position=(0, 0, 20), yaw=-90, pitch=0, roll=0):
        self.oglFrame = oglFrame

#        self.m_firstPersonYOffset = 0.0

        self.m_behavior = CameraBehavior.FIRST_PERSON
#        self.m_preferTargetYAxisOrbiting = True
        
        self.m_accumPitchDegrees = 0.0
        self.m_savedAccumPitchDegrees = 0.0
        
        self.m_rotationSpeed = DEFAULT_ROTATION_SPEED
        self.m_fovx = DEFAULT_FOVX
        self.m_aspectRatio = 0.0
        self.m_znear = DEFAULT_ZNEAR
        self.m_zfar = DEFAULT_ZFAR  
        
        self.m_orbitMinZoom = DEFAULT_ORBIT_MIN_ZOOM
        self.m_orbitMaxZoom = DEFAULT_ORBIT_MAX_ZOOM
        self.m_orbitOffsetDistance = DEFAULT_ORBIT_OFFSET_DISTANCE
# vectors
    # position of the camera
        self.m_eye = glm.vec3(position);
    # saved position of the camera for Orbiting
        self.m_savedEye = glm.vec3(position);
    # position of the object that the camera is looking at or Orbiting around
        self.m_target = glm.vec3(0.0, 0.0, 0.0);
        
    # the camera axes
    # left / right axe
        self.right = glm.vec3(1.0, 0.0, 0.0) # X axe
    # up axe
        self.up = glm.vec3(0.0, 1.0, 0.0)  # Y axe
    # forward / direction axe
        self.forward = glm.vec3(0.0, 0.0,-1.0)  # Z axe

    # axis of the target for Orbiting
        self.m_targetYAxis = glm.vec3(0.0, 1.0, 0.0);
    # the direction of the camera  negative of the zAxis
        self.m_viewDir = glm.vec3(0.0, 0.0, -1.0);


        self.yaw = yaw      # yaw  rotation around up vector
        self.pitch = pitch  # pitch rotation around right or left vector
        self.roll = roll    # roll rotation around forward vector



    # the acceleration of the movement of the camera
        self.m_acceleration = glm.vec3(0.0, 0.0, 0.0);
    # the velocity of the movement of the camera
        self.m_currentVelocity = glm.vec3(0.0, 0.0, 0.0);
        self.m_velocity = glm.vec3(0.0, 0.0, 0.0);
        self.speed = SPEED


# quaternion
        self.m_orientation = glm.quat()
        self.m_savedOrientation = glm.quat()


#        self.positionChange = False
        

# matrix
    # the view matrix of the camera
        self.m_viewMatrix = glm.mat4(1.0)
        self.m_projMatrix = glm.mat4(0.0)
        self.m_viewProjMatrix = glm.mat4(1.0)
        self.m_orthoMatrix = glm.mat4(1.0)
        self.ortho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
        self.viewWidth = oglFrame.size().width()
        self.viewHeight = oglFrame.size().height()
        self.setAspectRatio(oglFrame.size().width(),oglFrame.size().height())
        self.lookAt(self.m_eye, self.m_eye + self.forward, self.up)
        self.m_viewProjMatrix = self.m_viewMatrix * self.m_projMatrix

        self.planeXY = Plane(pointOnPlane = glm.vec3(0.0,0.0,0.0),normal = glm.vec3(0.0,0.0,1.0))
        self.planeYZ = Plane(pointOnPlane = glm.vec3(0.0,0.0,0.0),normal = glm.vec3(1.0,0.0,0.0))
        self.planeXZ = Plane(pointOnPlane = glm.vec3(0.0,0.0,0.0),normal = glm.vec3(0.0,1.0,0.0))


    def lookAt(self,eye, target, up):
        self.m_eye = eye;
        self.m_target = target;

# calculate the forward vector
        m_zAxis = eye - target  
        m_zAxis = glm.normalize(m_zAxis)

        self.m_viewDir = -m_zAxis

        m_xAxis = glm.cross(up, m_zAxis)
        m_xAxis = glm.normalize(m_xAxis)

        m_yAxis = glm.cross(m_zAxis, m_xAxis)
        m_yAxis = glm.normalize(m_yAxis)
        
        self.m_viewMatrix[0][0] = m_xAxis.x
        self.m_viewMatrix[1][0] = m_xAxis.y
        self.m_viewMatrix[2][0] = m_xAxis.z
        self.m_viewMatrix[3][0] = -glm.dot(m_xAxis, eye)

        self.m_viewMatrix[0][1] = m_yAxis.x
        self.m_viewMatrix[1][1] = m_yAxis.y
        self.m_viewMatrix[2][1] = m_yAxis.z
        self.m_viewMatrix[3][1] = -glm.dot(m_yAxis, eye)

        self.m_viewMatrix[0][2] = m_zAxis.x
        self.m_viewMatrix[1][2] = m_zAxis.y
        self.m_viewMatrix[2][2] = m_zAxis.z    
        self.m_viewMatrix[3][2] = -glm.dot(m_zAxis, eye)
#        // Extract the pitch angle from the view matrix.
        self.m_accumPitchDegrees = glm.degrees(glm.asin(self.m_viewMatrix[1][2]))
        
        self.m_orientation = glm.quat(self.m_viewMatrix)
#        self.m_orientation.fromMatrix(self.m_viewMatrix);
#        self.updateViewMatrix();

# perspective Right Handed
    def perspective(self,fovx, aspect, znear, zfar):
        cotangent = 1.0 / glm.tan(fovx / 2.0) 
        self.m_projMatrix = glm.mat4(0)
        self.m_projMatrix[0][0] = cotangent / aspect
        self.m_projMatrix[1][1] = cotangent
        self.m_projMatrix[2][2] = -(zfar + znear) / (zfar - znear)
        self.m_projMatrix[2][3] = -1.0
        self.m_projMatrix[3][2] = -(2.0 * zfar * znear) / (zfar - znear)

#        self.m_viewProjMatrix = self.m_viewMatrix * self.m_projMatrix
        
# ortho Right Handed
    def ortho(self,left, right, bottom, top, zNear, zFar):
        self.m_orthoMatrix = glm.mat4(0)
        self.m_orthoMatrix[0][0] = 2.0 / (right - left)
        self.m_orthoMatrix[1][1] = 2.0 / (top - bottom)
        self.m_orthoMatrix[2][2] = -2.0 / (zFar - zNear)
        self.m_orthoMatrix[3][0] = -(right + left) / (right - left)
        self.m_orthoMatrix[3][1] = -(top + bottom) / (top - bottom)
        self.m_orthoMatrix[3][2] = -(zFar + zNear) / (zFar - zNear)

    def update(self):
    # set the new position
        self.move()
    # set the new orientation from the mouse delta
        self.rotate()
    # fix the forward right and up vector from the orientation
    # set the viewMatrix of the camera for all objects get from postion and quaternion / euclide yaw pitch roll ?
        self.update_camera_vectors()
    # set the inverted view matrix for the ray picking
        self.invertedViewMatrix = glm.inverse(self.m_viewMatrix)

    def updateViewMatrix(self):
#        // Reconstruct the view matrix.

#        self.m_viewMatrix = self.m_orientation.toMatrix4()

        m_xAxis = glm.vec3(self.m_viewMatrix[0][0], self.m_viewMatrix[1][0], self.m_viewMatrix[2][0])
        m_yAxis = glm.vec3(self.m_viewMatrix[0][1], self.m_viewMatrix[1][1], self.m_viewMatrix[2][1])
        m_zAxis = glm.vec3(self.m_viewMatrix[0][2], self.m_viewMatrix[1][2], self.m_viewMatrix[2][2])
        self.m_viewDir = -m_zAxis

        if (self.m_behavior == CameraBehavior.ORBIT):
#            // Calculate the new camera position based on the current
#            // orientation. The camera must always maintain the same
#            // distance from the target. Use the current offset vector
#            // to determine the correct distance from the target.

            self.m_eye = self.m_target + m_zAxis * self.m_orbitOffsetDistance

        self.m_viewMatrix[3][0] = -glm.dot(m_xAxis, self.m_eye)
        self.m_viewMatrix[3][1] = -glm.dot(m_yAxis, self.m_eye)
        self.m_viewMatrix[3][2] = -glm.dot(m_zAxis, self.m_eye)

    def setAspectRatio(self,width,height):
        self.viewWidth = width
        self.viewHeight = height
        self.m_aspectRatio = width / height
        # set the projection Matrix
        self.perspective(glm.radians(self.m_fovx), self.m_aspectRatio, self.m_znear, self.m_zfar)
        self.invertedProjectionMatrix = glm.inverse(self.m_projMatrix)

    def get_view_matrix(self):
        return self.m_viewMatrix

    def get_view(self):
        return self.m_viewMatrix
    
    def get_projection(self):
        return self.m_projMatrix

    def get_Ortho(self):
        return self.m_orthoMatrix

    def setBehavior(self,m_behavior):
        prevBehavior = self.m_behavior
        if self.m_behavior == m_behavior:
            return
        self.m_behavior = m_behavior

    def rotate(self):
        if self.oglFrame.moveCamera:
            if self.m_behavior == CameraBehavior.FIRST_PERSON:
                self.yaw += self.oglFrame.rel_x * SENSITIVITY
                self.pitch -= self.oglFrame.rel_y * SENSITIVITY
                self.pitch = max(-89, min(89, self.pitch))
#                self.oglFrame.root.cameraFrame.setXYZAngle((self.pitch,self.yaw,self.roll))
            if self.m_behavior == CameraBehavior.SPECTATOR:
                self.yaw += self.oglFrame.rel_x * SENSITIVITY
                self.pitch -= self.oglFrame.rel_y * SENSITIVITY
                self.pitch = max(-89, min(89, self.pitch))
#                self.oglFrame.root.cameraFrame.setXYZAngle((self.pitch,self.yaw,self.roll))
            if self.m_behavior == CameraBehavior.FLIGHT:
                self.roll += self.oglFrame.rel_x * SENSITIVITY
                self.pitch -= self.oglFrame.rel_y * SENSITIVITY
                self.pitch = max(-89, min(89, self.pitch))
#                self.oglFrame.root.cameraFrame.setXYZAngle((self.pitch,self.yaw,self.roll))
            if self.m_behavior == CameraBehavior.ORBIT:
                self.yaw += self.oglFrame.rel_x * SENSITIVITY
                self.pitch -= self.oglFrame.rel_y * SENSITIVITY
                self.pitch = max(-89, min(89, self.pitch))
#                self.oglFrame.root.cameraFrame.setXYZAngle((self.pitch,self.yaw,self.roll))
                    

    def move(self):
        velocity = self.speed * self.oglFrame.delta_time
        if self.oglFrame.keysPress[0]:  # 'w'
            self.m_eye += self.forward * velocity
#            self.positionChange = True
        if self.oglFrame.keysPress[1]:  # 's'
            self.m_eye -= self.forward * velocity
#            self.positionChange = True
        if self.oglFrame.keysPress[2]:  # 'a'
            self.m_eye -= self.right * velocity
#            self.positionChange = True
        if self.oglFrame.keysPress[3]:  # 'd'
            self.m_eye += self.right * velocity
#            self.positionChange = True
        if self.oglFrame.keysPress[4]:
            self.m_eye += self.up * velocity
#            self.positionChange = True
        if self.oglFrame.keysPress[5]:
            self.m_eye -= self.up * velocity
#            self.positionChange = True
        if self.oglFrame.keysPress[6]:
            self.speed += 0.1
            print(self.speed)
        if self.oglFrame.keysPress[7]:
            self.speed -= 0.1
            print(self.speed)
#        if self.positionChange:
##            self.oglFrame.root.cameraFrame.setXYZPosition(self.m_eye)
#            self.positionChange = False

    # set the viewMatrix of the camera for all objects

    def update_camera_vectors(self):
#        pitchMatrix = glm.rotate(self.pitch,glm.vec3(1.0,0.0,0.0))
#        yawMatrix = glm.rotate(self.yaw,glm.vec3(0.0,1.0,0.0))
#        rollMatrix = glm.rotate(self.roll,glm.vec3(0.0,0.0,1.0))
#        rotationMatrix = rollMatrix * yawMatrix * pitchMatrix

        
        
        
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))
    # get the view matrix from forward right and up vector
        self.lookAt(self.m_eye, self.m_eye + self.forward, self.up)


#    def rotateFirstPerson(headingDegrees, pitchDegrees):
## Implements the rotation logic for the first person style and
## spectator style camera behaviors. Roll is ignored.
#        if headingDegrees != 0.0:
#            rot.fromAxisAngle(WORLD_YAXIS, headingDegrees)
#            m_orientation = rot * m_orientation#
## Rotate camera about its local x axis.
## Note the order the quaternions are multiplied. That is important!
#        if pitchDegrees != 0.0:
#            rot.fromAxisAngle(WORLD_XAXIS, pitchDegrees)
#            m_orientation = m_orientation * rot


#    def rotateFlight(headingDegrees, pitchDegrees, rollDegrees):
## Implements the rotation logic for the flight style camera behavior.
#       Quaternion rot;
#
#       rot.fromHeadPitchRoll(headingDegrees, pitchDegrees, rollDegrees);
#       m_orientation *= rot;

    def rotateOrbit(headingDegrees, pitchDegrees, rollDegrees):
# Implements the rotation logic for the orbit style camera behavior.
# Roll is ignored for target Y axis orbiting.
#
# Briefly here's how this orbit camera implementation works. Switching to
# the orbit camera behavior via the setBehavior() method will set the
# camera's orientation to match the orbit target's orientation. Calls to
# rotateOrbit() will rotate this orientation. To turn this into a third
# person style view the updateViewMatrix() method will move the camera
# position back 'm_orbitOffsetDistance' world units along the camera's
# local z axis from the orbit target's world position.
        rot = glm.quat(glm.radians(glm.vec3(headingDegrees, pitchDegrees, rollDegrees)))
#       Quaternion rot;
#
#       if m_preferTargetYAxisOrbiting:
#           if headingDegrees != 0.0
#               rot.fromAxisAngle(m_targetYAxis, headingDegrees)
#               m_orientation = rot * m_orientation
#
#           if pitchDegrees != 0.0
#               rot.fromAxisAngle(WORLD_XAXIS, pitchDegrees)
#               m_orientation = m_orientation * rot
#       else:
#        rot.fromHeadPitchRoll(headingDegrees, pitchDegrees, rollDegrees)
        self.m_orientation = self.m_orientation * rot
    
    
#Walk around
#Look around
#Zoom
#Mouse input

    def getYaw(self):
        return self.yaw

    def getPitch(self):
        return self.pitch

    def getRoll(self):
        return self.roll

    def getPosition(self):
        return self.m_eye

    def setPosition(self,position):
        self.m_eye = position
        
    def setTarget(self,target):
        self.m_target = target
     
    def getTarget(self):
        return self.m_target
        
    def getNormalizedDeviceCoord(self,m_PosX,m_PosY):
        x = (2.0 * m_PosX) / self.viewWidth - 1.0
        y = 1.0 - (2.0 * m_PosY) / self.viewHeight
        return glm.vec4(x,y,-1.0,1.0)

    def toEyeCoords(self,clipCoords):
        eyeCoord = self.invertedProjectionMatrix * clipCoords
        return glm.vec4(eyeCoord.x,eyeCoord.y,-1.0,0.0)

    def toWorldCoords(self,eyeCoord):
        rayWorld = glm.inverse(self.m_viewMatrix) * eyeCoord
        rayWorld = glm.vec3(round(rayWorld.x,5),round(rayWorld.y,5),round(rayWorld.z,5))
        rayWorld = glm.normalize(rayWorld)
        return rayWorld

    def get_Ray(self,pos):
        self.m_Pos = (pos[0],pos[1])
        normalizeDeviceCoord = self.getNormalizedDeviceCoord(pos[0],pos[1])
        clipCoord = normalizeDeviceCoord
        eyeCoord = self.toEyeCoords(clipCoord)
        rayWorld = self.toWorldCoords(eyeCoord)
        return Ray(self.m_eye,rayWorld)

    def testRay(self,mPos):
#        planeXY = Plane(pointOnPlane = glm.vec3(0.0,0.0,0.0),normal = glm.vec3(0.0,0.0,1.0))
#        planeYZ = Plane(pointOnPlane = glm.vec3(0.0,0.0,0.0),normal = glm.vec3(1.0,0.0,0.0))
#        planeXZ = Plane(pointOnPlane = glm.vec3(0.0,0.0,0.0),normal = glm.vec3(0.0,1.0,0.0))
#        return self.planeXY.testRay(self.get_Ray(mPos))
        return self.planeXZ.testRay(self.get_Ray(mPos))


    def glUnProject(self,point1):
        self.ray1 = self.get_Ray(point1)
#        self.planeXZ = Plane(pointOnPlane = glm.vec3(0.0,0.0,0.0),normal = glm.vec3(0.0,1.0,0.0))
#        return self.planeXY.testRay(self.ray1)
        return self.planeXZ.testRay(self.ray1)
    

    def glProject(self,pos1):
        windowCoordinate = [0,0]
        # Modelview transform
        fTx = self.m_viewMatrix[0][0]*pos1.x+self.m_viewMatrix[1][0]*pos1.y+self.m_viewMatrix[2][0]*pos1.z+self.m_viewMatrix[3][0] # w is always 1
        fTy = self.m_viewMatrix[0][1]*pos1.x+self.m_viewMatrix[1][1]*pos1.y+self.m_viewMatrix[2][1]*pos1.z+self.m_viewMatrix[3][1]
        fTz = self.m_viewMatrix[0][2]*pos1.x+self.m_viewMatrix[1][2]*pos1.y+self.m_viewMatrix[2][2]*pos1.z+self.m_viewMatrix[3][2]
        fTw = self.m_viewMatrix[0][3]*pos1.x+self.m_viewMatrix[1][3]*pos1.y+self.m_viewMatrix[2][3]*pos1.z+self.m_viewMatrix[3][3]
        # Projection transform, the final row of projection matrix is always [0 0 -1 0]
        # so we optimize for that.
        fTOx = self.m_projMatrix[0][0]*fTx+self.m_projMatrix[1][0]*fTy+self.m_projMatrix[2][0]*fTz+self.m_projMatrix[3][0]*fTw
        fTOy = self.m_projMatrix[0][1]*fTx+self.m_projMatrix[1][1]*fTy+self.m_projMatrix[2][1]*fTz+self.m_projMatrix[3][1]*fTw
        fTOz = self.m_projMatrix[0][2]*fTx+self.m_projMatrix[1][2]*fTy+self.m_projMatrix[2][2]*fTz+self.m_projMatrix[3][2]*fTw
        fTOw =-fTz
        # The result normalizes between -1 and 1
        if(fTOw!=0.0): # The w value
            fTOw=1.0/fTOw
            # Perspective division
            fTOx*=fTOw
            fTOy*=fTOw
            fTOz*=fTOw
            # Window coordinates
            # Map x, y to range 0-1
            windowCoordinate[0]=np.round(((fTOx*0.5+0.5)*self.viewWidth)+0, 0)
            windowCoordinate[1]=np.round(self.viewHeight - ((fTOy*0.5+0.5)*self.viewHeight)+0,0)

        return windowCoordinate[0],windowCoordinate[1]



#// pseudo code found at: 
#// http://www.gamedev.net/topic/221071-simple-raysphere-collision/ 
#Vec3d ClosestPoint(const Vec3d A, const Vec3d B, 
#                   const Vec3d P, double *t) 
#{ 
#    Vec3d AB = B - A; 
#    double ab_square = DotProduct(AB, AB); 
#    Vec3d AP = P - A; 
#    double ap_dot_ab = DotProduct(AP, AB); 
#    // t is a projection param when we project vector AP onto AB 
#    *t = ap_dot_ab / ab_square; 
#    // calculate the closest point 
#    Vec3d Q = A + AB * (*t); 
#    return Q; 
#} 


#bool RayTest(const Vec3d, const Vec3d start, const Vec3d end, 
#                  Vec3d *pt, double *t, double epsilon) 
#{ 
#    *pt = ClosestPoint(start, end, center, t); 
#    double len = Distance(*pt, m_pos); 
#    return len < (m_radius+epsilon); 
#} 
#// note that "t" param can be used further 
#// the same is with "pt" 