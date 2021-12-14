import os.path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QTextOption, QColor, QMouseEvent
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QTextEdit, QFrame, QProgressBar
from PyQt5 import QtCore
import cv2


# 填充在wait列表里面的widget
# 首先是一个图片显示视频的某一帧，然后是序号，然后是视频的文件名和文件路径，下面需要跟上一个进度条
class fileRecordView_wait(QWidget):
    itemSelected = pyqtSignal(int)
    
    def __init__(self, df):
        super(fileRecordView_wait, self).__init__()
        self.setGeometry(QtCore.QRect(0, 0, 300, 80))

        # 所需变量
        self.df = df
        self.index = df.iloc[0]
        self.filepath = df.iloc[1]
        self.status = df.iloc[2]

        # 图片所处的位置
        self.label_image = QLabel(self)
        self.label_image.setGeometry(QtCore.QRect(5, 5, 80, 50))
        cap = cv2.VideoCapture(self.filepath)
        _, self.frame = cap.read()
        # 将图片转换为QImage
        self.frame_qimage = QImage(self.frame[:], self.frame.shape[1], self.frame.shape[0], self.frame.shape[1] * 3,
                                   QImage.Format_RGB888)
        # 将图片转换为QPixmap方便显示
        self.frame_qpixmap = QPixmap.fromImage(self.frame_qimage).scaled(80, 60)
        self.label_image.setPixmap(self.frame_qpixmap)

        # 文件名称和文件路径
        self.filename = os.path.split(self.filepath)[1]
        self.label_filename = QLabel(self)
        self.label_path = QLabel(self)
        self.label_filepath = QTextEdit(self)
        self.label_filepath.setReadOnly(True)
        self.label_filepath.setWordWrapMode(QTextOption.NoWrap)
        self.label_filepath.setFrameShape(QFrame.NoFrame)
        self.label_filepath.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.label_filename.setGeometry(QtCore.QRect(90, 3, 210, 20))
        self.label_path.setGeometry(13, 60, 40, 18)
        self.label_filepath.setGeometry(QtCore.QRect(50, 60, 245, 18))
        self.label_filename.setText(str(self.index) + "----" + self.filename)
        self.label_path.setText("path:")
        self.label_filepath.setText(self.filepath)
        
        # 进度条 现在已经提出来了
        # self.layoutWidget = QWidget(self)
        # self.layoutWidget.setGeometry(QtCore.QRect(90, 20, 200, 38))
        # self.layoutWidget.setObjectName("layoutWidget")
        # # self.layoutWidget.setStyleSheet("background: black")
        # self.progress_wait = QProgressBar(self.layoutWidget)
        # self.progress_wait.setValue(25)
        # self.progress_wait.setGeometry(QtCore.QRect(5, 5, 180, 30))
        # self.progress_wait.setObjectName("progress_wait")
        QtCore.QMetaObject.connectSlotsByName(self)
            
    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        self.itemSelected.emit(self.index)

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
    win = fileRecordView_wait(csv_df[csv_df["index"] == 0].iloc[0])
    win.show()
    sys.exit(app.exec_())
