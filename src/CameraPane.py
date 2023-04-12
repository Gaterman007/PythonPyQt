from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar,QDockWidget,QListWidget,QMessageBox,QListWidgetItem
from Model import BaseModel
from Camera import Cameras

class CameraPane(QDockWidget):
    def __init__(self,title, parent=None, flags=Qt.WindowFlags()):
        super().__init__(title,parent,flags)
        self.parent = parent
        self.hide()
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFloating(False)
        self.setMaximumWidth(450)
        self.listWidget = QListWidget()
        self.addItem('No Camera')
        self.setWidget(self.listWidget)
        self.listWidget.itemClicked.connect(self.Clicked)

        self.loadCameras()
        
    def Clicked(self,item):
        Cameras.inst().setCamera(item.text())
#        if item.text() in BaseModel.newmodelList:
#            BaseModel.setSelectedModel(BaseModel.newmodelList[item.text()])
            
    def addItem(self,itemDesc):
        self.listWidget.addItem(itemDesc)
        
    def loadCameras(self):
        self.listWidget.clear()
        cameras = Cameras.inst()
        if len(cameras) <= 0:
            self.addItem('No Camera')
        for cameraName in cameras:
            self.addItem(cameraName)