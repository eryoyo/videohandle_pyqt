import os.path

from PyQt5.QtGui import QPixmap, QImage, QTextOption, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QTextEdit, QFrame, QCheckBox, QHBoxLayout, QScrollArea
from PyQt5 import QtCore
import cv2


# 填充在finish列表里面的widget
# 首先是一个图片，显示视频的某一帧，然后是视频名和视频路径，下面跟上一个复选框，重要的点是根据是否有异常需要显示出不同的颜色
# "index", "filepath", "status", "xiyan", "xiyan_path", "baoli", "baoli_path", "xuexing", "xuexing_path"
class fileRecordView_finish(QWidget):
    def __init__(self, df):
        super(fileRecordView_finish, self).__init__()
        self.setGeometry(QtCore.QRect(0, 0, 300, 80))

        # 所需变量
        self.df = df
        self.index = df.iloc[0, 0]
        self.filepath = df.iloc[0, 1]
        self.status = df.iloc[0, 2]

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
        self.label_filename.setText(self.filename)
        self.label_path.setText("path:")
        self.label_filepath.setText(self.filepath)
        
        # 显示是否检测出相关问题的复选框
        self.layoutWidget = QWidget(self)
        self.layoutWidget.setGeometry(QtCore.QRect(90, 20, 200, 38))
        self.layoutWidget.setObjectName("layoutWidget")
        self.scrollArea = QScrollArea(self.layoutWidget)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 200, 38))
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -810, 460, 1308))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.HLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.HLayout.setContentsMargins(0, 0, 0, 0)
        self.HLayout.setSpacing(5)
        self.HLayout.setObjectName("HLayout")
        self.init_checkbox()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        
    def init_checkbox(self):
        self.checklists = ["xiyan", "baoli", "xuexing", "baoli", "xuexing", "baoli", "xuexing"]
        self.checklists_name = ["吸烟", "暴力", "血腥", "暴力", "血腥", "暴力", "血腥"]
        for i, check in enumerate(self.checklists):
            if self.df.loc[0, check] == 0:
                continue
            checkbox = QCheckBox(self.scrollAreaWidgetContents)
            checkbox.setText(self.checklists_name[i])
            if self.df.loc[0, check] == 2:
                checkbox.setChecked(True)
            self.HLayout.addWidget(checkbox)

    def setAction(self):
        pass


from PyQt5.QtWidgets import QApplication
import sys
import pandas as pd

if __name__ == '__main__':
    app = QApplication(sys.argv)

    csv_df = pd.read_csv("./file.csv", index_col=0)
    print(csv_df)
    # 显示窗口
    win = fileRecordView_finish(csv_df[csv_df["index"] == 0])
    win.show()
    sys.exit(app.exec_())
