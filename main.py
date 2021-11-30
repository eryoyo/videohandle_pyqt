import sys

from PyQt5.QtGui import QIcon

import mainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtGui, QtWidgets

# 入口，唯一
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(open('./style.qss', 'rb').read().decode('utf-8'))
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("img/Icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    app.setWindowIcon(icon)
    
    MainWindow = QMainWindow()
    # MainWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint|QtCore.Qt.WindowMinimizeButtonHint)  
    ui = mainWindow.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
