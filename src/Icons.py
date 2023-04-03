from PyQt5.QtGui import QIcon, QFont, QColor, QCursor
from PyQt5 import QtWidgets, QtGui

class Icons:
    _instance = None
 
    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def inst(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            # Creating action using the first constructor
            cls._instance.StdToolbar = QtGui.QPixmap('Image\\StandardTB.png')
        return cls._instance

    def getCursorNo(self,iconNo,rowNo = 0,HotSpotX = 6,HotSpotY = 27):
        return QCursor(self.StdToolbar.copy(iconNo * 32,rowNo * 32,32,32),HotSpotX, HotSpotY)
        
    def getIconNo(self,iconNo,rowNo = 0):
        return QIcon(self.StdToolbar.copy(iconNo * 32,rowNo * 32,32,32))
