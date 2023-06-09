from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar,QDockWidget,QListWidget,QMessageBox,QListWidgetItem
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
        self.listWidget.itemClicked.connect(self.Clicked)
        self.addItem('No Model')
        self.setWidget(self.listWidget)

        BaseModel.updateListCB(self.loadModels)
        BaseModel.updateSelectionCB(self.updateSelection)
        self.loadModels()
        self.updateSelection(BaseModel.selectedModel)

    def Clicked(self,item):
        if item.text() in BaseModel.newmodelList:
            BaseModel.setSelectedModel(BaseModel.newmodelList[item.text()])
            
        
    def __del__(self):
        BaseModel.updateListCB(None)
        BaseModel.updateSelectionCB(None)
        
    def addItem(self,itemDesc):
        self.listWidget.addItem(itemDesc)

    def setCurrentItem(self,itemNo):
        self.listWidget.setCurrentRow(itemNo)

    def loadModels(self):
        self.listWidget.clear()
        for model in BaseModel.newmodelList:
            if not BaseModel.newmodelList[model].internal:
                self.addItem(BaseModel.newmodelList[model].modelName)   #self.modelID,self.modelName,self
        if self.listWidget.count() <= 0:
            self.addItem('No Model')

    def updateSelection(self,model):
        self.listWidget.clearSelection()
        if model is not None:
            if model.modelName in BaseModel.newmodelList:
                for index in range(self.listWidget.count()):
                    if self.listWidget.item(index).text() == model.modelName:
                        self.listWidget.setCurrentRow(index)
