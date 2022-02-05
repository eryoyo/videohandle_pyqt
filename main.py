import sys
from concurrent.futures import as_completed

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication

import mainWindow
# 入口，唯一
import testWindow
from UMainWindow import UMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(open('./style.qss', 'rb').read().decode('utf-8'))
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("img/Icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    app.setWindowIcon(icon)

    MainWindow = UMainWindow()
    ui = testWindow.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.sizeChanged.connect(ui.setGeometryAll)
    MainWindow.closeHappen.connect(ui.closeHappen)
    MainWindow.show()
    sys.exit(app.exec_())
