from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QRect
from PyQt5.QtWidgets import QWidget, QCheckBox


# 填充在wait列表里面的widget
# 首先是一个图片显示视频的某一帧，然后是序号，然后是视频的文件名和文件路径，下面需要跟上一个进度条
class settingView(QWidget):
    stateChange = pyqtSignal(str)

    def __init__(self, event_py, checked, event):
        super(settingView, self).__init__()
        self.setGeometry(QtCore.QRect(0, 0, 300, 40))

        # 所需变量
        self.event_py = event_py
        self.checked = checked
        self.event = event

        # 设置界面的复选框
        self.checkBox = QCheckBox(self)
        self.checkBox.setGeometry(QRect(10, 10, 200, 20))
        self.checkBox.setObjectName('checkBox')
        self.checkBox.setText(event)
        self.checkBox.setChecked(self.checked)
        self.checkBox.stateChanged.connect(lambda: self.stateChanged(self.event_py))

        QtCore.QMetaObject.connectSlotsByName(self)

    def stateChanged(self, event_py):
        self.stateChange.emit(event_py)

    def setAction(self):
        pass


from PyQt5.QtWidgets import QApplication
import sys
import pandas as pd

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(open('./style.qss', 'rb').read().decode('utf-8'))

    csv_df = pd.read_csv("./file.csv", index_col=0)
    # 显示窗口
    win = settingView('smoke', True, '吸烟')
    win.show()
    sys.exit(app.exec_())
