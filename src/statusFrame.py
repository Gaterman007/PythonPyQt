from PyQt5.QtWidgets import QLineEdit,QLabel, QStatusBar

class StatusBar:
    def __init__(self,mainWin):
        self.mainWin = mainWin
        self.statusbar = QStatusBar()
        mainWin.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready", 3000)
#        self.wcLabel = QLabel(f"{self.getWordCount()} Words")
        self.textbox = QLineEdit(self.statusbar)
        self.textbox.setText("enter command")
        self.textbox.setSelection(0,len("enter command"))
#        self.wcLabel = QLabel("12 Words")
        self.statusbar.addPermanentWidget(self.textbox)
        self.textbox.returnPressed.connect(self.onClick)

    def showMessage(self,message,time):
        self.statusbar.showMessage(message, time)

    def onClick(self):
        self.mainWin.api.statusFrameExec(input = self.textbox.text())
        self.textbox.setText("enter command")
        self.textbox.setSelection(0,len("enter command"))
