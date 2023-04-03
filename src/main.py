import sys
import os

from oglWin import OglFrame
from menuManager import MenuManager
from statusFrame import StatusBar
from API import API
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar,QDockWidget,QListWidget


class EngineWindow(QMainWindow):
    """Main EngineWindow."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3D Editor")                                # set window title
        self.setWindowIcon(QtGui.QIcon('Image\\3dGlobe.png'))                  # set icon for program
        mainDir = os.path.dirname(__file__)                             # get program directory
        self.mainParentdir = os.path.join(mainDir, os.pardir)           # get path of parent directory
        self.mainParentdir = os.path.realpath(self.mainParentdir)       # get real path eliminating any symbolic links
        self.imageDir = os.path.join(self.mainParentdir, "image")       # get image path
        self.shaderDir = os.path.join(self.mainParentdir, "shaders")    # get shaders path

        self.oglFrame = OglFrame(self)        
        self.setCentralWidget(self.oglFrame)
        self.api = API(self)
        self.menuManager = MenuManager(self)
        self.resize(1600, 900)
        self.statusBar = StatusBar(self)
        self.oglFrame.setFocus()
        
        
    def on_focusChanged(self, old, now):
        fwidget = QApplication.focusWidget()
        if fwidget is not None:
            print("focus widget name ", fwidget.objectName())


        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = EngineWindow()
    win.show()
    exitret = app.exec_()
    win.oglFrame.cleanUp()
    sys.exit(exitret)