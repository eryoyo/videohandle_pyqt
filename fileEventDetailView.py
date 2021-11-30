import cv2
from PyQt5.QtCore import QRect, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton


# 这个是在事件列表区域里面的详情列表里面的小组件
class fileEventDetailView(QWidget):
    btn_play_clicked = pyqtSignal(int)
    
    def __init__(self, df, filepath):
        super(fileEventDetailView, self).__init__()
        self.setGeometry(QRect(0, 0, 700, 60))
        
        self.df = df
        self.filepath = filepath
        self.index = df["index"]
        self.type = df["type"]
        self.start = df["start"]
        self.end = df["end"]
        self.total = df["total"]

        # 图片所处的位置
        self.label_image = QLabel(self)
        self.label_image.setGeometry(QRect(10, 5, 80, 50))
        cap = cv2.VideoCapture(self.filepath)
        cap.set(cv2.CAP_PROP_POS_FRAMES, self.start)
        _, self.frame = cap.read()
        # 将图片转换为QImage
        self.frame_qimage = QImage(self.frame[:], self.frame.shape[1], self.frame.shape[0], self.frame.shape[1] * 3,
                                   QImage.Format_RGB888)
        # 将图片转换为QPixmap方便显示
        self.frame_qpixmap = QPixmap.fromImage(self.frame_qimage).scaled(80, 60)
        self.label_image.setPixmap(self.frame_qpixmap)
        
        # 中间信息展示
        self.label_start = QLabel(self)
        self.label_start.setGeometry(QRect(120, 20, 200, 20))
        self.label_start.setStyleSheet("background: green")
        self.label_start.setText("起始帧位置：" + str(self.start))
        self.label_start.setAlignment(Qt.AlignCenter)
        self.label_end = QLabel(self)
        self.label_end.setGeometry(QRect(370, 20, 200, 20))
        self.label_end.setStyleSheet("background: green")
        self.label_end.setText("结束帧位置：" + str(self.end))
        self.label_end.setAlignment(Qt.AlignCenter)
        
        # 查看的按钮
        self.btn_play = QPushButton(self)
        self.btn_play.setGeometry(QRect(600, 10, 40, 40))
        icon = QIcon()
        icon.addPixmap(QPixmap("img/Icon.png"), QIcon.Normal, QIcon.Off)
        self.btn_play.setIcon(icon)
        self.btn_play.setIconSize(QSize(40, 40))
        
        self.setAction()
        
    def eventPlay(self):
        self.btn_play.emit(self.start)
        
    def setAction(self):
        # 按钮的槽函数
        self.btn_play.click().connect(self.eventPlay)


from PyQt5.QtWidgets import QApplication
import sys
import pandas as pd

if __name__ == '__main__':
    app = QApplication(sys.argv)

    csv_df = pd.read_csv("./result/smoke_1638263955553461.csv", index_col=0)
    print(csv_df)

    # 显示窗口
    win = fileEventDetailView(csv_df.iloc[0], "/Users/chenjialin/Downloads/smoke.mp4")
    win.show()
    sys.exit(app.exec_())
