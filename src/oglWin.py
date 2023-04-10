import numpy as np
import os
import glm
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import QOpenGLWidget, QWidget
from PyQt5.QtCore import QTimer
from Model import *
from textureManager import *
from Camera import *
import time as tm


class OglFrame(QOpenGLWidget):

    def __init__(self, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)
        self.parentWin = args[0]

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateAll)

        self.camera = [Camera(self,position=(5,5,40),pitch=-5,yaw=-90),Camera(self,position=(34,8,0), pitch=0, yaw=180)]
        self.cameraNumber = 0

        self.t0 = tm.time()
        self.t1 = tm.time()
        self.delta_time = 0
        self.framerate = 0

        self.keys = ['w','s','a','d','q','e','+','-']
        self.keysPress = [False] * len(self.keys)
        self.moveCamera = False
        self.setMouseTracking(True)
        self.buttonLeft = False
        self.oldMousePos = None
        self.rel_x = 0
        self.rel_y = 0
        self.oldPos_x = 0
        self.oldPos_y = 0
        self.width = 0
        self.height = 0

    def updateAll(self):
        self.timer.stop()
        self.update()
        self.timer.start(5)

    def leaveEvent(self,event):
        self.parentWin.api.mouseTool.MouseLeaveEvent(event)

    def ButtonDown(self,event):
        if event.button() == QtCore.Qt.LeftButton:
            self.buttonLeft = True
            self.moveCamera = True
            self.oldPos_x = event.x()
            self.oldPos_y = event.y()
            self.rel_x = 0
            self.rel_y = 0
        self.oldMousePos = event.pos()
        
    def MouseMove(self,event):
        if self.buttonLeft:
            if self.oldPos_x != event.x():
                self.rel_x = self.oldPos_x - event.x()
                self.oldPos_x = event.x()
            if self.oldPos_y != event.y():
                self.rel_y = self.oldPos_y - event.y()
                self.oldPos_y = event.y()
    
    def ButtonUp(self,event):
        if event.button() == QtCore.Qt.LeftButton:
            self.buttonLeft = False
            self.moveCamera = False

    def MouseWheel(self,event):
        steps = event.angleDelta().y()
        vector = steps and steps // abs(steps)
#        print(vector)


    def keyPressEvent(self, event):
        key = event.key()
        if key < 128:
            if key < 91 and key > 64:
                char = chr(key).lower()
            else:
                char = chr(key)
            if char in self.keys:
                self.keysPress[self.keys.index(char)] = True

    def keyReleaseEvent(self, event):
        key = event.key()
        if key < 128:
            if key < 91 and key > 64:
                char = chr(key).lower()
            else:
                char = chr(key)
            if char in self.keys:
                self.keysPress[self.keys.index(char)] = False
    
    def wheelEvent(self,event):
        self.parentWin.api.mouseTool.MouseWheelEvent(event)

    def mousePressEvent(self, event):
        widget = QtWidgets.QApplication.focusWidget()
        if widget != self:
            self.setFocus()
        self.parentWin.api.mouseTool.ButtonDownEvent(event)
            
    def mouseReleaseEvent(self, event):
        self.parentWin.api.mouseTool.ButtonUpEvent(event)

    def mouseMoveEvent(self, event):
        self.parentWin.api.mouseTool.MouseMoveEvent(event)

    def getGlInfo(self):
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
            """.format(
            glGetString(GL_VENDOR),
            glGetString(GL_RENDERER),
            glGetString(GL_VERSION),
            glGetString(GL_SHADING_LANGUAGE_VERSION)
        )
        return info

#    def updateTexture(self):
#        pass
#        if self.switch == 0:
#            self.newModel.TextureID = Textures.inst()['img']
#            self.switch = 1
#        elif self.switch == 1:
#            self.newModel.TextureID = self.ID
#            self.switch = 2
#        elif self.switch == 2:
#            self.newModel.TextureID = self.ID
#            self.switch = 3
#        elif self.switch == 3:
#            self.newModel.TextureID = self.ID
#            self.switch = 4
#        elif self.switch == 4:
#            self.newModel.TextureID = Textures.inst()['test']
#            self.switch = 5
#        elif self.switch == 5:
#            self.newModel.TextureID = self.ID
#            self.switch = 6
#        else:
#            self.newModel.TextureID = self.ID
#            self.switch = 0

    def noiseTexture(self):
        width, height, = 128, 128
        img = np.uint8(np.random.rand(width, height)*128)
        # create Texture
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
        glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, img)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

    def initializeGL(self):
#        print(self.getGlInfo())

        ShaderProgram.inst().defaultValue()

        self.drawModelList = []
        
        Textures.inst().addTexture('test','textures\\test.png',alpha = True)
        Textures.inst().addTexture('img','textures\\img_1.png',alpha = True)
        Textures.inst().addTexture('HUD','textures\\HUD.png',alpha = True)
        Textures.inst().addTexture('window','textures\\blending_transparent_window.png',alpha = True)
        self.hudTexture = HUDTexture(self)
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_CULL_FACE)
#        glDisable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
#        glFrontFace(GL_CW)
        
        # Head Up Display
        HUDID = self.hudTexture.getID()
        self.hudModel = None
        newhudModel = ModelDef2(Name = "HUD",progName = 'HUD',
                                TextureID = HUDID,Blend = True)
        newhudModel.internal = True
        newhudModel.addPoint3D([  Point3D(-1.0, -1.0, 1.0, 0.0, 0.0),
                                    Point3D( 1.0, -1.0, 1.0, 1.0, 0.0),
                                    Point3D( 1.0,  1.0, 1.0, 1.0, 1.0),
                                    Point3D(-1.0,  1.0, 1.0, 0.0, 1.0)])
        newhudModel.addIndices([0,1,2,3])
        newhudModel.renders = [(GL_TRIANGLE_FAN,4,0)]
        self.hudModel = newhudModel


        self.timer.start(5)
        
        
        self.StartUpLoading()
    

    def StartUpLoading(self):





        """
#default test model        
        """
        self.defModel = ModelDefault(Name = 'test1',progName = 'def3')
        point1 = Point3D(1.0,  1.0, 1.0)
        point2 = Point3D(1.0, -1.0, 1.0)
        point3 = Point3D(-1.0, -1.0, 1.0)
        point4 = Point3D(-1.0,  1.0, 1.0)

        point5 = Point3D(1.0,  1.0, -1.0)
        point6 = Point3D(1.0, -1.0, -1.0)
        point7 = Point3D(-1.0, -1.0, -1.0)
        point8 = Point3D(-1.0,  1.0, -1.0)
        self.defModel.pointColor = glm.vec4(1.0,1.0,0.0,1.0)
        points4 = [point1,point2,point3,point4,point5,point6,point7,point8]
        self.defModel.addPoint3D(points4)
        self.defModel.segmentColor = glm.vec4(0.0,1.0,1.0,1.0)
        segment4 = [Segment(start = point1,end = point2),Segment(start = point2,end = point3),Segment(start = point3,end = point4),Segment(start = point4,end = point1)]
        self.defModel.addSegment(segment4)
        self.defModel.faceColor = glm.vec4(1.0, 0.0, 1.0, 1.0)
        # counter clock wise
        # front face  0,2,1,0,3,2  
        triangle2 = [Triangle(p1 = point1, p2 = point3,p3 = point2,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,0.0),uv3 = glm.vec2(0.0,0.0))]
        triangle2.append(Triangle(p1 = point1, p2 = point4,p3 = point3,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,1.0),uv3 = glm.vec2(1.0,0.0)))
        # back face 4,5,6,4,6,7
        triangle2.append(Triangle(p1 = point5, p2 = point6,p3 = point7,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,0.0),uv3 = glm.vec2(0.0,0.0)))
        triangle2.append(Triangle(p1 = point5, p2 = point7,p3 = point8,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,1.0),uv3 = glm.vec2(1.0,0.0)))
        # right face 0,1,4,1,5,4
        triangle2.append(Triangle(p1 = point1, p2 = point2,p3 = point5,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,1.0),uv3 = glm.vec2(1.0,0.0)))
        triangle2.append(Triangle(p1 = point2, p2 = point6,p3 = point5,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,1.0),uv3 = glm.vec2(1.0,0.0)))
        # left face 2,6,3,3,6,7
        triangle2.append(Triangle(p1 = point3, p2 = point4,p3 = point7,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,1.0),uv3 = glm.vec2(1.0,0.0)))
        triangle2.append(Triangle(p1 = point4, p2 = point8,p3 = point7,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,1.0),uv3 = glm.vec2(1.0,0.0)))
        # top face 0,3,4,3,7,4
        triangle2.append(Triangle(p1 = point1, p2 = point5,p3 = point4,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,1.0),uv3 = glm.vec2(1.0,0.0)))
        triangle2.append(Triangle(p1 = point4, p2 = point5,p3 = point8,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,1.0),uv3 = glm.vec2(1.0,0.0)))
        # bottom face 1,5,2,2,5,6
        triangle2.append(Triangle(p1 = point2, p2 = point3,p3 = point6,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,1.0),uv3 = glm.vec2(1.0,0.0)))
        triangle2.append(Triangle(p1 = point3, p2 = point7,p3 = point6,uv1 = glm.vec2(0.0,1.0),uv2 = glm.vec2(1.0,1.0),uv3 = glm.vec2(1.0,0.0)))


        self.defModel.addTriangle(triangle2)
        self.defModel.pointSize = 5.0
        
#        self.defModel.setScale(glm.vec3(2,2,2))
#        self.defModel.setScale((2,2,2))     # est aussi correct

#        self.defModel.setRotation((45,15,30))
#        self.defModel.setRotation(glm.vec3(45,15,30)) # est aussi correct

        self.defModel.setPosition(glm.vec3(4,2,-2))


        self.drawModelList.append(self.defModel)



        """
#ModelDef2 test model        
        """

        newdef2Model = ModelDef2(Name = "test2",progName = 'def3',mode = GL_POINTS,Blend = True)
        newdef2Model.addPoint3D([  Point3D(-0.5, -0.5, 0.5, 0.0, 0.0),
                                    Point3D( 0.5, -0.5, 0.5, 1.0, 0.0),
                                    Point3D( 0.5,  0.5, 0.5, 1.0, 1.0),
                                    Point3D(-0.5,  0.5, 0.5, 0.0, 1.0),
                                    Point3D(-0.5, -0.5, -0.5, 0.0, 0.0),
                                    Point3D( 0.5, -0.5, -0.5, 1.0, 0.0),
                                    Point3D( 0.5,  0.5, -0.5, 1.0, 1.0),
                                    Point3D(-0.5,  0.5, -0.5, 0.0, 1.0)])
        newdef2Model.pointSize = 4.0
        newdef2Model.addIndices([0,1,2,3,4,5,6,7])  # 8 Point
        # faces
        newdef2Model.addIndices([0,1,2,0,2,3])      # Front
        newdef2Model.addIndices([4,6,5,4,7,6])      # Back
        newdef2Model.addIndices([0,4,1,1,4,5])      # Right
        newdef2Model.addIndices([2,6,3,3,6,7])      # Left
        newdef2Model.addIndices([0,3,4,3,7,4])      # Top
        newdef2Model.addIndices([1,5,2,2,5,6])      # Bottom

        #  8 point Vert et 12 Triangle Rouge
        newdef2Model.addRender(GL_POINTS,8,0,(0.0,1.0,0.0,1.0))
        newdef2Model.addRender(GL_LINE_LOOP,4,0,(0.0,0.0,1.0,1.0))
        newdef2Model.addRender(GL_LINE_LOOP,4,4*4,(0.0,0.0,1.0,1.0))
        newdef2Model.addRender(GL_TRIANGLES,36,8*4,(1.0,0.0,0.0,1.0))

        self.drawModelList.append(newdef2Model)








#        self.defModel.setWireFrame(True)
        
        self.parentWin.api.defaultAxes()
        self.parentWin.api.defaultGrille()

    def resizeGL(self, width: int, height: int):
        self.width = width
        self.height = height

        glViewport(0, 0, self.width, self.height)
        for camera in self.camera:
            camera.setAspectRatio(self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, self.width, 0.0, self.height, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.hudTexture.resize(self.width, self.height)

    def paintGL(self):
        self.camera[self.cameraNumber].update()

        glClearColor(0.0, 0.2, 0.2, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

#        glBindTexture(GL_TEXTURE_2D, self.ID)
#        self.noiseTexture()
        
        for drawModel in self.drawModelList:
            drawModel.update(self.camera[self.cameraNumber])
            drawModel.paintGL()
        if self.hudModel is not None:
            self.hudModel.paintGL()
        
        self.setFrameRate()

    def setFrameRate(self):
        if tm.time() - self.t1 > 1:
#            self.root.setFrameRate(self.framerate)
            self.framerate = 0
            self.t1 = tm.time()
        self.delta_time = tm.time() - self.t0
        self.t0 = tm.time()
        self.framerate = self.framerate + 1

    def setResetKey(self,key,setReset):
        if key in self.keys:
            self.keysPress[self.keys.index(key)] = setReset

    def keyPress(self,event):
        if self.focused:
            if event.char in self.keys:
                self.keysPress[self.keys.index(event.char)] = True

    def keyRelease(self,event):
        if self.focused:
            if event.char in self.keys:
                self.keysPress[self.keys.index(event.char)] = False

    def cleanUp(self):
        self.timer.stop()
