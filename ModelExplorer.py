from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar,QDockWidget,QListWidget
from Model import BaseModel

class ModelExplorer(QDockWidget):
    def __init__(self,title, parent=None, flags=Qt.WindowFlags()):
        super().__init__(title,parent,flags)
        self.parent = parent
        #self.parent.oglFrame
        self.hide()
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFloating(False)
        self.setMaximumWidth(450)
        self.listWidget = QListWidget()
        self.addItem('No Model')
        self.setWidget(self.listWidget)

        BaseModel.updateListCB(self.loadModels)
        self.loadModels(BaseModel.modelList)

        
    def __del__(self):
        BaseModel.updateListCB(None)
        
    def addItem(self,itemDesc):
        self.listWidget.addItem(itemDesc)

    def loadModels(self,modelList):
        self.listWidget.clear()
        for model in modelList:
            if not model[2].internal:
                self.addItem(model[1])   #self.modelID,self.modelName,self
        if self.listWidget.count() <= 0:
            self.addItem('No Model')
