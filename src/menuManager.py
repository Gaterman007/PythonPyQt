from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QColor, QCursor
from PyQt5.QtWidgets import QInputDialog, QLabel, QLineEdit, QMainWindow, QMenuBar, QMenu, QAction, QToolBar, QFileDialog, QPushButton, QDialog, QWidget, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QTabWidget, QTreeView
from PyQt5.Qt import QStandardItemModel,QStandardItem,QItemSelectionModel,QItemSelection
from API import *
from Icons import Icons

class ActionList:
    actionCmdList = {}
    def __init__(self,mainWin):
        self.mainWin = mainWin
#        self.icon = Icons()
    
    def removeAction(self,cmdStr):
        self.actionCmdList.pop(cmdStr)

    def getAction(self,cmdStr):
        return self.actionCmdList[cmdStr]

    def getActionList(self):
        return self.actionCmdList

    def makeAction(self,cmdStr,strMenu,connect = None,connectData = None,iconNo = -1,toolTip = '',statusTip = ''):
        self.actionCmdList[cmdStr] = QAction(strMenu, self.mainWin)
        if iconNo != -1:
            self.actionCmdList[cmdStr].setIcon(Icons.inst().getIconNo(iconNo))
        if statusTip != '':
            self.actionCmdList[cmdStr].setStatusTip(statusTip)
        if toolTip != '':
            self.actionCmdList[cmdStr].setToolTip(toolTip)
        if connect is not None:
            self.actionCmdList[cmdStr].triggered.connect(lambda:connect(connectData))
        return self.actionCmdList[cmdStr]

    def setText(self,cmdStr,text):
        self.actionCmdList[cmdStr].setText(text)

    def getText(self,cmdStr):
        return self.actionCmdList[cmdStr].text()

    def setToolTip(self,cmdStr,text):
        self.actionCmdList[cmdStr].setToolTip(text)

    def getToolTip(self,cmdStr):
        return self.actionCmdList[cmdStr].toolTip()

    def setStatusTip(self,cmdStr,text):
        self.actionCmdList[cmdStr].setStatusTip(text)

    def getStatusTip(self,cmdStr):
        return self.actionCmdList[cmdStr].statusTip()

    def setIcon(self,cmdStr,iconNo):
        if iconNo != -1:
            self.actionCmdList[cmdStr].setIcon(Icons.inst().getIconNo(iconNo))
        else:
            self.actionCmdList[cmdStr].setIcon(None)

    def getIcon(self,cmdStr):
        return self.actionCmdList[cmdStr].icon()
    
    def setConnect(self,cmdStr,connect):
        if connect is not None:
            self.actionCmdList[cmdStr].triggered.connect(connect)
        else:
            self.actionCmdList[cmdStr].triggered.disconnect()

class StandardItem(QStandardItem):
    def __init__(self,txt='',font_size = 12,set_bold= False,color = QColor(0,0,0)):
        super().__init__()
        
        fnt = QFont('Open Sans',font_size)
        fnt.setBold(set_bold)
        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)

class FileTreeView(QTreeView):
    def __init__(self,mainWidget):
        super().__init__(mainWidget)
        self.setHeaderHidden(True)
        self.treemodel = QStandardItemModel()
        self.rootnode = self.treemodel.invisibleRootItem()
        self.setModel(self.treemodel)
        self.expandAll()
        
    def addNode(self,Name,parentNode = None):
        newNode = StandardItem(Name)
        if parentNode is None:
            self.rootnode.appendRow(newNode)
        else:
            parentNode.appendRow(newNode)
        return newNode

    def insertNode(self,Name,parentNode = None,rowIndex = -1):
        newNode = StandardItem(Name)
        if parentNode is None:
            if rowIndex == -1:
                self.rootnode.appendRow(newNode)
            else:
                self.rootnode.insertRow(rowIndex,newNode)
        else:
            if rowIndex == -1:
                parentNode.appendRow(newNode)
            else:
                parentNode.insertRow(rowIndex,newNode)
        return newNode
            

    def removeNode(self,NodeToRemove):
        if NodeToRemove.parent() is None:
            self.rootnode.removeRow(NodeToRemove.index().row())
        else:
            NodeToRemove.parent().removeRow(NodeToRemove.index().row())

    def clear(self):
        self.treemodel.clear()
        self.rootnode = self.treemodel.invisibleRootItem()

    def selectNode(self,nodeSelect):
        self.clearSelection()
        flags = QItemSelectionModel.Select
        self.selectionModel().clear()
        selection = QItemSelection()
        selection.select(nodeSelect.index(), nodeSelect.index())
        self.selectionModel().select(selection, flags)


    def mousePressEvent(self, event):
        item = self.indexAt(event.pos())
        indexs = self.selectedIndexes()
        if len(indexs) > 0:
            selectedItem = indexs[0].model().itemFromIndex(indexs[0])
            if item.model() is not None:
                itemIndex = item.model().itemFromIndex(item)
                if selectedItem == itemIndex:
                    self.clearSelection()
                    return
            else:
                self.clearSelection()
        if not item.isValid():
            self.clearSelection()
        QTreeView.mousePressEvent(self, event)

class PreferenceDialog(QDialog):
    def __init__(self,mainWin):
        super().__init__(mainWin)
        self.actionList = ActionList(mainWin)
        self.mainWin = mainWin
        # setting window title
        self.setWindowTitle("Preference")
 
        # setting geometry to the window
        self.setGeometry(300, 400, 500, 400)

        self.tabs = QTabWidget(self.mainWin)

        tab1 = QWidget(self.tabs)
        self.tabs.addTab(tab1,"Menus")
        tab2 = QWidget(self.tabs)
        self.tabs.addTab(tab2,"Toolbars")
        tab3 = QWidget(self.tabs)
        self.tabs.addTab(tab3,"Hotkeys")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.close)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignBottom)
        mainLayout.addWidget(self.tabs)
        mainLayout.addWidget(self.buttonBox)


        self.treeview1 = FileTreeView(tab1)
# default Action
        self.addActionToTreeView1("New","&New",self.mainWin.api.newFile,"new",0,"Create a new file",'')
        self.addActionToTreeView1("Open","&Open...",self.mainWin.api.openFile,None,1,'','')
        self.addActionToTreeView1("Save","&Save",self.mainWin.api.saveFile,None,2,'','')
        self.addActionToTreeView1("Cut","C&ut",self.mainWin.api.cutContent,None,3,'','')
        self.addActionToTreeView1("Copy","&Copy",self.mainWin.api.copyContent,None,4,'','')
        self.addActionToTreeView1("Paste","&Paste",self.mainWin.api.pasteContent,None,5,'','')
        self.addActionToTreeView1("Help content","&Help Content",self.mainWin.api.helpContent,None,-1,'','')
        self.addActionToTreeView1("Preference","&Preference",self.mainWin.api.preferenceDialog,None,-1,'','')
        self.addActionToTreeView1("About","&About",self.mainWin.api.aboutDialog,None,-1,'','')
        self.addActionToTreeView1("Select","&Select",self.mainWin.api.selectMode,ToolMode.SELECT,7,'','')
        self.addActionToTreeView1("Rectangle","&Rectangle",self.mainWin.api.selectMode,ToolMode.RECTANGLE,11,'','')
        self.addActionToTreeView1("Line","&Line",self.mainWin.api.selectMode,ToolMode.LINE,8,'','')
        self.addActionToTreeView1("NewModel","&new Model",self.mainWin.api.newModel,None,6,'Create a new Model','New Model')
        self.addActionToTreeView1("ToogleGride","&Toogle Gride",self.mainWin.api.toogle_Grille,None,6,'show or hide Grille','show/hide Grille')
        self.addActionToTreeView1("showModelExplorer","&Model Explorer",self.mainWin.api.showModelList,None,-1,'','')
        self.treeview1.expandAll()
        
 
 
 
        midButtons = QWidget(tab1)
        bAddSub = QPushButton("Add >>",midButtons)
        bAdd = QPushButton("Add >",midButtons)
        bRemove = QPushButton("<< Remove",midButtons)
        bAddSub.clicked.connect(self.addToSubTree)
        bAdd.clicked.connect(self.addToTree)
        bRemove.clicked.connect(self.removeFromTree)
        midButtonsLayout = QVBoxLayout()
        midButtonsLayout.addWidget(bAdd)
        midButtonsLayout.addWidget(bAddSub)
        midButtonsLayout.addWidget(bRemove)
        midButtons.setLayout(midButtonsLayout)
        # creating a vertical layout
        tab1Layout = QHBoxLayout()
        tab1.setLayout(tab1Layout)

 
 
        treeview2Frame = QWidget(tab1)
        treeview2Layout = QVBoxLayout()
        treeview2Layout.setAlignment(Qt.AlignBottom)
        bNewNode = QPushButton("New Node",treeview2Frame)
        bNewNode.clicked.connect(self.newNode)
        self.treeview2 = FileTreeView(tab1)
        fileNode = self.treeview2.addNode("File")
        editNode = self.treeview2.addNode("Edit")
        helpNode = self.treeview2.addNode("Help")
        
        node = self.treeview2.addNode("New",fileNode)
        node.setData(self.getNodeData("New"))
        node = self.treeview2.addNode("Open",fileNode)
        node.setData(self.getNodeData("Open"))
        node = self.treeview2.addNode("Save",fileNode)
        node.setData(self.getNodeData("Save"))
#        self.treeview2.addNode("Cut",editNode)
#        self.treeview2.addNode("Copy",editNode)
#        self.treeview2.addNode("Paste",editNode)
#        self.treeview2.addNode("Help content",helpNode)
#        self.treeview2.addNode("About",helpNode)
        self.treeview2.expandAll()

        treeview2Layout.addWidget(self.treeview2)
        treeview2Layout.addWidget(bNewNode)
        treeview2Frame.setLayout(treeview2Layout)

        rightButtons = QWidget(tab1)
        bUp = QPushButton("↑",rightButtons)
        bDown = QPushButton("↓",rightButtons)
        bUp.clicked.connect(self.moveUpTree)
        bDown.clicked.connect(self.moveDownTree)
        rightButtonsLayout = QVBoxLayout()
        rightButtonsLayout.addWidget(bUp)
        rightButtonsLayout.addWidget(bDown)
        rightButtons.setLayout(rightButtonsLayout)
        rightButtons.setFixedWidth(50)

        tab1Layout.addWidget(self.treeview1)
        tab1Layout.addWidget(midButtons)
        tab1Layout.addWidget(treeview2Frame)
        tab1Layout.addWidget(rightButtons)





        mid2Buttons = QWidget(tab2)
        bAdd2 = QPushButton("Add >>",mid2Buttons)
        bRemove2 = QPushButton("<< Remove",mid2Buttons)
        mid2ButtonsLayout = QVBoxLayout()
        mid2ButtonsLayout.addWidget(bAdd2)
        mid2ButtonsLayout.addWidget(bRemove2)
        mid2Buttons.setLayout(mid2ButtonsLayout)
        # creating a vertical layout
        tab2Layout = QHBoxLayout()
        tab2.setLayout(tab2Layout)
        self.treeview3 = QTreeView(tab2)
        self.treeview3.setHeaderHidden(True)
        self.treeview4 = QTreeView(tab2)
        self.treeview4.setHeaderHidden(True)
        tab2Layout.addWidget(self.treeview3)
        tab2Layout.addWidget(mid2Buttons)
        tab2Layout.addWidget(self.treeview4)

        # setting lay out
        self.setLayout(mainLayout)

        self.setWindowTitle("Preference")
        self.setWindowModality(Qt.ApplicationModal)
        
    def moveUpTree(self):
        indexSelectedTV2 = self.treeview2.selectedIndexes()
        if len(indexSelectedTV2) > 0:
            firstSelected = indexSelectedTV2[0]
            itemSelectedTV2 = firstSelected.model().itemFromIndex(firstSelected)
            indexAboveSelected = self.treeview2.indexAbove(firstSelected)
            if indexAboveSelected.model() is not None:
                aboveSelectedItem = indexAboveSelected.model().itemFromIndex(indexAboveSelected)
                dataParent = itemSelectedTV2.parent()
                dataText = itemSelectedTV2.text()
                dataItem = itemSelectedTV2.data()
                datarow = itemSelectedTV2.row()
                self.treeview2.removeNode(itemSelectedTV2)
                if dataParent == aboveSelectedItem.parent():
                    newNode = self.treeview2.insertNode(dataText,aboveSelectedItem.parent(),aboveSelectedItem.row())
                    newNode.setData(dataItem)
                    self.treeview2.selectNode(newNode)
                else:
                    if datarow == 0:
                        newNode = self.treeview2.insertNode(dataText,aboveSelectedItem.parent(),aboveSelectedItem.row())
                        newNode.setData(dataItem)
                        self.treeview2.selectNode(newNode)
                    else:
                        newNode = self.treeview2.insertNode(dataText,aboveSelectedItem.parent(),aboveSelectedItem.row()+1)
                        newNode.setData(dataItem)
                        self.treeview2.selectNode(newNode)

    
    def moveDownTree(self):
        indexSelectedTV2 = self.treeview2.selectedIndexes()
        if len(indexSelectedTV2) > 0:
            firstSelected = indexSelectedTV2[0]
            itemSelectedTV2 = firstSelected.model().itemFromIndex(firstSelected)
            indexBelowSelected = self.treeview2.indexBelow(firstSelected)
            if indexBelowSelected.model() is not None:
                belowSelectedItem = indexBelowSelected.model().itemFromIndex(indexBelowSelected)
                dataParent = itemSelectedTV2.parent()
                dataText = itemSelectedTV2.text()
                dataItem = itemSelectedTV2.data()
                datarowCount = itemSelectedTV2.rowCount()
                self.treeview2.removeNode(itemSelectedTV2)
#                print("\nup")
#                print(dataText)
#                print(datarowCount)
#                print(belowSelectedItem.rowCount())
#                print(belowSelectedItem.text())
                if dataParent == belowSelectedItem.parent():
                    newNode = self.treeview2.insertNode(dataText,belowSelectedItem,0)
                    newNode.setData(dataItem)
                    self.treeview2.selectNode(newNode)
                else:
#                    print(dataParent,belowSelectedItem.parent())
                    if datarowCount == 0:
                        newNode = self.treeview2.insertNode(dataText,belowSelectedItem.parent(),belowSelectedItem.row())
                        newNode.setData(dataItem)
                        self.treeview2.selectNode(newNode)
                    else:
                        newNode = self.treeview2.insertNode(dataText,belowSelectedItem.parent(),belowSelectedItem.row()+1)
                        newNode.setData(dataItem)
                        self.treeview2.selectNode(newNode)
                    

    def addToTree(self):
        selectedIndexs = self.treeview1.selectedIndexes()
        if len(selectedIndexs) > 0:
            itemSelected = selectedIndexs[0].model().itemFromIndex(selectedIndexs[0])
            selectedIndexsTV2 = self.treeview2.selectedIndexes()
            if len(selectedIndexsTV2) == 0:
                newNode = self.treeview2.addNode(itemSelected.text())
                newNode.setData(itemSelected.data())
                self.treeview2.selectNode(newNode)
            else:
                itemSelectedTV2 = selectedIndexsTV2[0].model().itemFromIndex(selectedIndexsTV2[0])
                newNode = self.treeview2.insertNode(itemSelected.text(),itemSelectedTV2.parent(),itemSelectedTV2.row()+1)
                newNode.setData(itemSelected.data())
                self.treeview2.selectNode(newNode)
        
    def addToSubTree(self):
        selectedIndexs = self.treeview1.selectedIndexes()
        if len(selectedIndexs) > 0:
            itemSelected = selectedIndexs[0].model().itemFromIndex(selectedIndexs[0])
            selectedIndexsTV2 = self.treeview2.selectedIndexes()
            if len(selectedIndexsTV2) == 0:
                newNode = self.treeview2.addNode(itemSelected.text())
                newNode.setData(itemSelected.data())
                self.treeview2.selectNode(newNode)
            else:
                itemSelectedTV2 = selectedIndexsTV2[0].model().itemFromIndex(selectedIndexsTV2[0])
                newNode = self.treeview2.addNode(itemSelected.text(),itemSelectedTV2)
                newNode.setData(itemSelected.data())
                self.treeview2.selectNode(newNode)
        
    def removeFromTree(self):
        selectedIndexsTV2 = self.treeview2.selectedIndexes()
        if len(selectedIndexsTV2) > 0:
            itemSelectedTV2 = selectedIndexsTV2[0].model().itemFromIndex(selectedIndexsTV2[0])
            textRemoved = itemSelectedTV2.text()
            self.treeview2.removeNode(itemSelectedTV2)
#        self.treeview2.clearSelection()

    def newNode(self):
        text, ok = QInputDialog.getText(self, 'New Node', 'Enter Name')
        if ok:
            indexSelected = self.treeview2.selectedIndexes()
            if len(indexSelected) > 0:
                itemSelected = indexSelected[0].model().itemFromIndex(indexSelected[0])
                self.treeview2.insertNode(text,itemSelected.parent(),itemSelected.row()+1)
            else:
                self.treeview2.insertNode(text)

    def addActionToTreeView1(self,cmdStr,strMenu,connect = None,connectData = None,iconNo = -1,toolTip = '',statusTip = ''):
        node = self.treeview1.addNode(cmdStr)
        action = self.actionList.makeAction(cmdStr,strMenu,connect,connectData,iconNo,toolTip,statusTip)
        node.setData(action)

    def getNodeData(self,cmdStr):
        return self.actionList.getAction(cmdStr).data()
        
    def updateAction(self,actionList):
        self.treeview1.clear()
        actionList = actionList.getActionList()
        for actionStr in actionList:
            self.treeview1.addNode(actionStr)
        
    def show(self):
        self.exec_()


class MenuManager:
    def __init__(self,mainWin):
        self.mainWin = mainWin
        self.prefwin = PreferenceDialog(self.mainWin)

        self.menuList = []
        self._createActions()
        self._createMenuBar()
        self._createToolBars()
#        print(self.menuList[1].title())

        
        
    def _createMenuBar(self):
        menuBar = self.mainWin.menuBar()
        # File menu
        fileMenu = QMenu("&File", self.mainWin)
        self.menuList.append(fileMenu)
        menuBar.addMenu(fileMenu)

        fileMenu.addAction(self.getAction('New'))
        fileMenu.addAction(self.getAction('Open'))
        fileMenu.addAction(self.getAction('Save'))
        fileMenu.addSeparator()
        fileMenu.addAction(self.getAction('Preference'))
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)


        # Edit menu
        editMenu = menuBar.addMenu("&Edit")
        self.menuList.append(editMenu)

        editMenu.addAction(self.getAction('Cut'))
        editMenu.addAction(self.getAction('Copy'))
        editMenu.addAction(self.getAction('Paste'))
        editMenu.addAction(self.getAction('ToogleGride'))
        editMenu.addAction(self.getAction('showModelExplorer'))
        # Help menu
        #QIcon(QtGui.QPixmap('pencil.png')),
        helpMenu = menuBar.addMenu("&Help")
        self.menuList.append(helpMenu)
        helpMenu.addAction(self.getAction('Help content'))
        helpMenu.addAction(self.getAction('About'))
        
    def _createToolBars(self):
        # Using a title
        fileToolBar = self.mainWin.addToolBar("File")
        fileToolBar.addAction(self.getAction('New'))
        fileToolBar.addAction(self.getAction('Open'))
        fileToolBar.addAction(self.getAction('Save'))
        # Using a QToolBar object
        editToolBar = QToolBar("Edit", self.mainWin)
        self.mainWin.addToolBar(editToolBar)
        editToolBar.addAction(self.getAction('Cut'))
        editToolBar.addAction(self.getAction('Copy'))
        editToolBar.addAction(self.getAction('Paste'))
        editToolBar.addAction(self.getAction('NewModel'))
        
        
        
        modeToolBar = QToolBar("Mode", self.mainWin)
        self.mainWin.addToolBar(modeToolBar)
        modeToolBar.addAction(self.getAction('Select'))
        modeToolBar.addAction(self.getAction('Line'))
        modeToolBar.addAction(self.getAction('Rectangle'))
#        # Using a QToolBar object and a toolbar area
#        helpToolBar = QToolBar("Help", self.mainWin)
#        self.mainWin.addToolBar(Qt.LeftToolBarArea, helpToolBar)

    def _createActions(self):
        
        self.exitAction = QAction("&Exit", self.mainWin)
        self.exitAction.triggered.connect(self.mainWin.close)


    def getAction(self,cmdStr):
        return self.prefwin.actionList.getAction(cmdStr)

    def removeMenu(self):
        menuRM = self.menuList.pop(1)
        menuAction = menuRM.menuAction()
        self.mainWin.menuBar().removeAction(menuAction)
        menuAction.deleteLater()
        menuRM.deleteLater()