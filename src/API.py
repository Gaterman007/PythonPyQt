from enum import Enum
from os import path
import sys, traceback

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QLabel, QFileDialog, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

from Icons import Icons
from Model import ModelDefault
from Point3D import Point3D,Segment,Triangle
from Camera import Plane
from ModelExplorer import ModelExplorer
from Tools import *

import numpy as np
import glm


class InterpreterError(Exception): pass


class API:
    def __init__(self,mainWin):
        self.mainWin = mainWin
        self.mouseTool = SelectTool(self.mainWin)
        self.grilleModel = None
        self.selectedModel = None
        self.axesModel = [None,None,None]
        self.modelListDisp = None


    def setSelectedModel(self,model):
        self.selectedModel = model
        
    def statusFrameExec(self,*args, **kwargs):
        if len(args) > 0:
            if type(args[0]) != type('str'):
                try:
                    exec(args[0].entry1.get(), globals(),locals())
                    return
                except:
                    return
            else:
        #        try:
                exec(eval(args[0]), globals(),locals())
        else:
            input = kwargs.get('input',None)
            if type(input) == type('str'):
                try:
                    exec(input, globals(),locals())
                    return
                except SyntaxError as err:
                    error_class = err.__class__.__name__
                    detail = err.args[0]
                    line_number = err.lineno
                    print(f"{0} error {1}]\n",error_class,detail)
                    return
                except Exception as err:
                    error_class = err.__class__.__name__
                    detail = err.args[0]
                    cl, exc, tb = sys.exc_info()
                    line_number = traceback.extract_tb(tb)[-1][1]
                    QMessageBox.about(self.mainWin, "Title", "%s at line %d of %s: %s" % (error_class, line_number, 'source ', detail))
#                exec(eval(args[0]), globals(),self.localdict)
        #        except:
        #            return
        #        except SyntaxError as err:
        #            error_class = err.__class__.__name__
        #            detail = err.args[0]
        #            line_number = err.lineno
        #        except Exception as err:
        #            error_class = err.__class__.__name__
        #            detail = err.args[0]
        #            cl, exc, tb = sys.exc_info()
        #            line_number = traceback.extract_tb(tb)[-1][1]
        #        else:
        #            return
        #        raise InterpreterError("%s at line %d of %s: %s" % (error_class, line_number, description, detail))


    def selectMode(self,actionData):
        if actionData == ToolMode.SELECT:
            self.mouseTool = SelectTool(self.mainWin)
        elif actionData == ToolMode.LINE:
            self.mouseTool = LineTool(self.mainWin)
        elif actionData == ToolMode.RECTANGLE:
            self.mouseTool = RegtangleTool(self.mainWin)
        else:
            self.mouseTool = SelectTool(self.mainWin)

    def newFile(self,actionData):
        self.mainWin.statusBar.showMessage("File > New clicked", 3000)
        # Logic for creating a new file goes here...

    def openFile(self,actionData):
        dlg = QFileDialog()
#        dlg.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dlg.setFileMode(QFileDialog.FileMode.AnyFile)
        dlg.setAcceptMode(QFileDialog.AcceptOpen)
        dlg.setNameFilter("All files  (*.*);;Text files  (*.txt);;Image files (*.png *.jpg)")
        dlg.setViewMode(QFileDialog.Detail)
        dlg.setDirectory('C:/')
#        dlg.setFilter("Text files (*.txt)")

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            filenames = dlg.selectedFiles()
            self.mainWin.statusBar.showMessage(f"File > Open {filenames[0]} clicked", 3000)
        else:
            self.mainWin.statusBar.showMessage("File > Open Canceled clicked", 3000)

    def saveFile(self,actionData):
        dlg = QFileDialog()
#        dlg.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dlg.setFileMode(QFileDialog.FileMode.AnyFile)
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setNameFilter("All files  (*.*);;Text files  (*.txt);;Image files (*.png *.jpg)")
        dlg.setViewMode(QFileDialog.Detail)
        dlg.setDirectory('C:/')
        dlg.selectFile("Gaetan.gn")
        dlg.setHistory([""])
#        dlg.setFilter("Text files (*.txt)")

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            filenames = dlg.selectedFiles()
            self.mainWin.statusBar.showMessage(f"File > Save {filenames[0]} clicked", 3000)
        else:
            self.mainWin.statusBar.showMessage("File > Save Canceled clicked", 3000)

    def cutContent(self,actionData):
        self.mainWin.statusBar.showMessage("Edit > Cut clicked", 3000)
        # Logic for cutting content goes here...

    def copyContent(self,actionData):
        self.mainWin.statusBar.showMessage("Edit > Copy clicked", 3000)
        # Logic for copying content goes here...

    def pasteContent(self,actionData):
        self.mainWin.statusBar.showMessage("Edit > Paste clicked", 3000)
        # Logic for pasting content goes here...

    def helpContent(self,actionData):
        self.mainWin.statusBar.showMessage("Help > Help Content...", 3000)
        # Logic for launching help goes here...

    def preferenceDialog(self,actionData):
        self.mainWin.menuManager.prefwin.show()

    def showModelList(self,show):
        if self.modelListDisp is None:
            self.modelListDisp = ModelExplorer('Model List',self.mainWin)
            self.mainWin.addDockWidget(Qt.LeftDockWidgetArea,self.modelListDisp)
            self.modelListDisp.show()
        else:
            if self.modelListDisp.isVisible():
                self.modelListDisp.hide()
            else:
                self.modelListDisp.show()



    def aboutDialog(self,actionData):
        self.mainWin.statusBar.showMessage("Help > About...", 3000)
        # Logic for showing an about dialog content goes here...

    def getCamera(self,cameraNo = -1):
        if cameraNo == -1:
            return self.mainWin.oglFrame.camera[self.mainWin.oglFrame.cameraNumber]
        else:
            return self.mainWin.oglFrame.camera[cameraNo]

    def newModel(self,actionData):
        self.mainWin.oglFrame.makeCurrent()
        self.selectedModel = ModelDefault(progName = 'def3')
        self.selectedModel.setModelName("new Model")
        self.selectedModel.pointSize = 5.0
        self.selectedModel.segmentColor = glm.vec4(0.0, 1.0, 1.0, 1.0)
        self.selectedModel.faceColor = glm.vec4(0.0, 1.0, 1.0, 1.0)
#        self.selectedModel.addPoint3D(Point3D(-4.0,0.0,-3.0))
#        seg = Segment(start = Point3D(-4.0,-4.0,-1.0), end = Point3D(4.0,4.0,1.0))
#        self.selectedModel.addSegment(seg)
#        seg = Segment(start = Point3D(2.0,0.0,1.0), end = Point3D(4.0,0.0,2.0))
#        self.selectedModel.addSegment(seg)
#        self.selectedModel.createSegmentBuffer()
        self.mainWin.oglFrame.drawModelList.append(self.selectedModel)
        self.mainWin.oglFrame.doneCurrent()
        
    def selectedModelAddTriangle(self,point1,point2,point3):
        if self.selectedModel is not None:
            self.mainWin.oglFrame.makeCurrent()
            self.selectedModel.addTriangle(Triangle(p1 = point1, p2 = point2, p3 = point3))
            self.mainWin.oglFrame.doneCurrent()
    
    
    def selectedModelAddSegment(self,startPos,endPos):
        if self.selectedModel is not None:
            self.mainWin.oglFrame.makeCurrent()
            self.selectedModel.addSegment(Segment(start = Point3D(startPos[0],startPos[1],startPos[2]), end = Point3D(endPos[0],endPos[1],endPos[2])))
            self.mainWin.oglFrame.doneCurrent()

    def selectedModelAddPoint(self,mPos):
        if self.selectedModel is not None:
            camera = self.getCamera()
            vecteur = camera.testRay(mPos)
            self.mainWin.oglFrame.makeCurrent()
            self.selectedModel.addPoint3D(Point3D(vecteur.x,vecteur.y,vecteur.z))
            self.mainWin.oglFrame.doneCurrent()

    def toogle_Grille(self,value):
        self.grilleModel.visible = not self.grilleModel.visible

    def grilleVisible(self,value):
        self.grilleModel.visible = value
        
    def axesVisible(self,value):
        for i in range(3):
            self.axesModel[i].visible = value
        
    def defaultGrille(self):
        self.grilleModel = ModelDefault(Name = 'Grille',progName = 'def3',internal=True)

        for i in range(-30,31):
            if i != 0:
                self.grilleModel.addSegment(Segment(start = Point3D(i,  0.0, 30.0),end = Point3D(i,  0.0, -30.0)))
        for i in range(-30,31):
            if i != 0:
                self.grilleModel.addSegment(Segment(start = Point3D(30.0,  0.0, i),end = Point3D(-30,  0.0, i)))
        self.mainWin.oglFrame.drawModelList.append(self.grilleModel)
        self.grilleModel.visible = False
#        self.defaultAxes()

    def defaultAxes(self):
        axesSize = 1000.0

        self.axesModel[0] = ModelDefault(Name = 'Axe Y',progName = 'def3',internal=True)
        seg = Segment(start = Point3D(0.0, -axesSize, 0.0),end = Point3D(0.0, axesSize, 0.0))
        self.axesModel[0].addSegment(seg)
        self.axesModel[0].segmentColor = glm.vec4(1.0, 0.0, 0.0, 1.0)

        self.mainWin.oglFrame.drawModelList.append(self.axesModel[0])

        self.axesModel[1] = ModelDefault(Name = 'Axe X',progName = 'def3',internal=True)
        seg = Segment(start = Point3D(-axesSize, 0.0, 0.0),end = Point3D(axesSize, 0.0, 0.0))
        self.axesModel[1].addSegment(seg)
        self.axesModel[1].segmentColor = glm.vec4(0.0, 1.0, 0.0, 1.0)
        self.mainWin.oglFrame.drawModelList.append(self.axesModel[1])

        self.axesModel[2] = ModelDefault(Name = 'Axe Z',progName = 'def3',internal=True)
        seg = Segment(start = Point3D(0.0,0.0, -axesSize),end = Point3D(0.0,0.0, axesSize))
        self.axesModel[2].addSegment(seg)
        self.axesModel[2].segmentColor = glm.vec4(0.0, 0.0, 1.0, 1.0)
        self.mainWin.oglFrame.drawModelList.append(self.axesModel[2])
        self.axesVisible(True)

    def picking(self,mPos):
        camera = self.getCamera()
        vecteur = camera.testRay(mPos)
        print("% 6.4f,% 6.4f,% 6.4f" % (vecteur.x,vecteur.y,vecteur.z))        