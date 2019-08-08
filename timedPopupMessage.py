from PyQt4 import QtGui
import PyQt4.QtCore as QtCore

class TimerMessageBox(QtGui.QMessageBox):
    def __init__(self, title, text, timeout=1, parent=None):
        super(TimerMessageBox, self).__init__(parent)
        
        self.setWindowTitle(title)
        self.time_to_wait = timeout
        self.setText(text)
        self.setIcon(QtGui.QMessageBox.Information)
        #self.setStandardButtons(QtGui.QMessageBox.NoButton)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start()
        #self.setWindowFlags(QtCore.Qt.WindowOkButtonHint | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowContextHelpButtonHint)
        
    
            
        

    def changeContent(self):
        #self.setText("wait (closing automatically in {0} secondes.)".format(self.time_to_wait))
        self.time_to_wait -= 1
        if self.time_to_wait <= 0:
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()