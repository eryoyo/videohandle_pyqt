import sys

from PyQt5.QtGui import QIcon

import mainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtGui, QtWidgets

StyleSheet = """
/*设置红色进度条*/
#progress {
    border: 2px solid #bbbbee;/*边框以及边框颜色*/
    min-height: 25px;
    max-height: 25px;
    border-radius: 6px;
    text-align: center;
}

#progress::chunk {
    border-radius: 6px;
    background-color: #ccccee;
    width: 7px
} 
"""

# 入口，唯一
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("img/Icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    app.setWindowIcon(icon)
    
    MainWindow = QMainWindow()
    # MainWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint|QtCore.Qt.WindowMinimizeButtonHint)  
    ui = mainWindow.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
