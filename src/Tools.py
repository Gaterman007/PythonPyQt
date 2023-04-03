from enum import Enum
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from Icons import Icons
import glm

class ToolMode(Enum):
    SELECT = 0
    LINE = 1
    POINTS = 2
    RECTANGLE = 3
    PAN = 4
    ORBIT = 5

class MouseTool:
    def __init__(self,mainWin):
        self.mainWin = mainWin
        self.defaultCursor()

    def getOGl(self):
        return self.mainWin.oglFrame

    def getAPI(self):
        return self.mainWin.api

    def defaultCursor(self):
        self.CURSOR_Arrow = QtGui.QCursor(Qt.ArrowCursor)
        self.mainWin.oglFrame.setCursor(self.CURSOR_Arrow)
#        self.CURSOR_Arrow = QtGui.QCursor(Qt.ArrowCursor)
#        self.CURSOR_PointingHandCursor = QtGui.QCursor(Qt.PointingHandCursor)
#        self.mainWin.oglFrame.setCursor(self.CURSOR_Arrow)

    def cursorChange(self):
        pass
        
    def ButtonDownEvent(self,event):
        pass

    def ButtonUpEvent(self,event):
        pass

    def MouseMoveEvent(self,event):
        pass
            
    def MouseWheelEvent(self,event):
        pass
        
    def MouseLeaveEvent(self,event):
        pass
        
class SelectTool(MouseTool):
    def __init__(self,mainWin):
        super().__init__(mainWin)

    def defaultCursor(self):
        self.CURSOR_Arrow = QtGui.QCursor(Qt.ArrowCursor)
        self.mainWin.oglFrame.setCursor(self.CURSOR_Arrow)

    def ButtonDownEvent(self,event):
        self.mainWin.oglFrame.ButtonDown(event)

    def ButtonUpEvent(self,event):
        self.mainWin.oglFrame.ButtonUp(event)

    def MouseMoveEvent(self,event):
        camera = self.getAPI().getCamera()
        self.getOGl().hudTexture.clear()
        ray = camera.get_Ray((event.x(),event.y()))
        onAModel = False
        onATriangle = False
        OnAVertex =  False
        for drawModel in self.getOGl().drawModelList:
            if not drawModel.internal:
                isOnModel, distance,isOnTriangle,isOnVertex = drawModel.HitTest(ray,triangleTest = True)
                if isOnModel:
                    onAModel = True
                if isOnTriangle:
                    onATriangle = True
                if isOnVertex:
                    OnAVertex =  True

        if onAModel:
            if onATriangle:
                visualIndicator = (255,255,0,255)
            else:
                visualIndicator = (255,0,0,255)
            if OnAVertex:
                visualIndicator = (0,0,255,255)
            
            self.getOGl().hudTexture.drawCircle(event.x(),event.y(),15,color = visualIndicator)

        self.mainWin.oglFrame.MouseMove(event)

    def MouseWheelEvent(self,event):
        self.mainWin.oglFrame.MouseWheel(event)

    def MouseLeaveEvent(self,event):
        self.getOGl().hudTexture.clear()


class LineTool(MouseTool):
    def __init__(self,mainWin):
        super().__init__(mainWin)
        self.point1 = None
        self.point2 = None
        self.MouseButtonDown = False

    def defaultCursor(self):
        self.CURSOR_Pencil = QtGui.QCursor(QtGui.QPixmap('Image\\pencil.png'), 6, 27)
        self.getOGl().setCursor(self.CURSOR_Pencil)

    def ButtonDownEvent(self,event):
        self.point1 = (event.x(),event.y())
        camera = self.getAPI().getCamera()
        self.pos1 = camera.glUnProject(self.point1)
        self.MouseButtonDown = True
 
    def ButtonUpEvent(self,event):
        self.point2 = (event.x(),event.y())
        camera = self.getAPI().getCamera()
        self.pos2 = camera.glUnProject(self.point2)
        self.getAPI().selectedModelAddSegment(self.pos1,self.pos2)
        self.MouseButtonDown = False
        self.getOGl().hudTexture.clear()

    def MouseMoveEvent(self,event):
        if self.MouseButtonDown:

            camera = self.getAPI().getCamera()
            screenPos = (event.x(),event.y())
#            posMouse = camera.glUnProject(screenPos)
            self.getOGl().hudTexture.clear()
            self.getOGl().hudTexture.drawLine(self.point1,screenPos)
        self.getOGl().MouseMove(event)

    def MouseWheelEvent(self,event):
        self.getOGl().MouseWheel(event)


class RegtangleTool(MouseTool):
    def __init__(self,mainWin):
        super().__init__(mainWin)
        self.point1 = None
        self.point2 = None
        self.MouseButtonDown = False

    def defaultCursor(self):
        self.CURSOR_Pencil = Icons.inst().getCursorNo(13,rowNo = 0,HotSpotX = 6,HotSpotY = 27)
        self.getOGl().setCursor(self.CURSOR_Pencil)

    def ButtonDownEvent(self,event):
        self.MouseButtonDown = True
        self.point1 = (event.x(),event.y())
        camera = self.getAPI().getCamera()
        self.pos1 = camera.glUnProject(self.point1)
        
#        self.getAPI().selectedModelAddPoint((event.x(),event.y()))

    def ButtonUpEvent(self,event):
        self.point2 = (event.x(),event.y())
        camera = self.getAPI().getCamera()
        self.pos2 = camera.glUnProject(self.point2)

# point1        self.pos1
# point2        glm.vec3(self.pos1.x,0.0,self.pos2.z)
# point3        self.pos2
# point4        glm.vec3(self.pos2.x,0.0,self.pos1.z)


#        self.getAPI().selectedModelAddSegment(self.pos1,glm.vec3(self.pos1.x,0.0,self.pos2.z))
#        self.getAPI().selectedModelAddSegment(glm.vec3(self.pos1.x,0.0,self.pos2.z),self.pos2)
#        self.getAPI().selectedModelAddSegment(self.pos2,glm.vec3(self.pos2.x,0.0,self.pos1.z))
#        self.getAPI().selectedModelAddSegment(glm.vec3(self.pos2.x,0.0,self.pos1.z),self.pos1)
        
        self.getAPI().selectedModelAddTriangle(self.pos1,self.pos2,glm.vec3(self.pos1.x,0.0,self.pos2.z))
        self.getAPI().selectedModelAddTriangle(self.pos1,glm.vec3(self.pos2.x,0.0,self.pos1.z),self.pos2)
#        self.getAPI().selectedModelAddPoint((event.x(),event.y()))
        self.MouseButtonDown = False
        self.getOGl().hudTexture.clear()

    def MouseMoveEvent(self,event):
        if self.MouseButtonDown:

            camera = self.getAPI().getCamera()
            screenPos = (event.x(),event.y())
            posMouse = camera.glUnProject(screenPos)
            
            point2 = camera.glProject(glm.vec3(self.pos1.x,0.0,posMouse.z))
            point3 = camera.glProject(glm.vec3(posMouse.x,0.0,self.pos1.z))

            self.getOGl().hudTexture.clear()
            self.getOGl().hudTexture.drawLine(self.point1,point2)
            self.getOGl().hudTexture.drawLine(point2,screenPos)
            self.getOGl().hudTexture.drawLine(screenPos,point3)
            self.getOGl().hudTexture.drawLine(point3,self.point1)
            
#            self.getOGl().hudTexture.drawRectangle(self.point1,(event.x(),event.y()))
        self.getOGl().MouseMove(event)

    def MouseWheelEvent(self,event):
        self.getOGl().MouseWheel(event)
