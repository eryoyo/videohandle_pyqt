from random import randint

from PyQt5.QtCore import QThread, pyqtSignal
import cv2


# 模拟视频处理的子线程，传入参数包括当前处理视频的Series，每一秒之后就会传出一个信号表示当前的帧数
# index,filepath,status,process_path,xiyan,baoli,xuexing
class threadDemo(QThread):
    valueChanged = pyqtSignal(int)  # 值变化信号

    # 传入当前正在处理的视频文件的Series
    def __init__(self, df):
        super(threadDemo, self).__init__()
        self.df = df
        self.index = df["index"]
        self.filepath = df["filepath"]

        self.cap = cv2.VideoCapture(self.filepath)
        self.frame_num = self.cap.get(7)

    def run(self):
        print('thread id:', QThread.currentThread())
        print("当前处理文件：", self.filepath)
        print("总帧数：", self.frame_num)
        i = 0
        while i < self.frame_num - 1:
            if self.isInterruptionRequested():
                break
            rn = randint(150, 250)
            i += rn
            if i >= self.frame_num:
                i = int(self.frame_num - 1)
            self.valueChanged.emit(i)
            print(self.filepath, '当前处理到value', i)
            QThread.sleep(1)
        # 最后需要将当前视频文件中的检测事件保存起来
        print(self.filepath, "视频处理结束。。。")
        

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QPushButton, QApplication
import pandas as pd


class Window(QWidget):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(self)
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 100)
        layout.addWidget(self.progressBar)
        layout.addWidget(QPushButton('开启线程', self, clicked=self.onStart))

        # 当前线程id
        print('main id', QThread.currentThread())

        # 子线程
        csv_df = pd.read_csv("./file.csv", index_col=0)
        self._thread = threadDemo(csv_df.iloc[0])
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.valueChanged.connect(lambda x: self.progressBar.setValue(round(x / 3307 * 100)))

    def onStart(self):
        if not self._thread.isRunning():
            print('main id', QThread.currentThread())
            self._thread.start()  # 启动线程

    def closeEvent(self, event):
        # if self._thread is None:
        #     super(Window, self).closeEvent(event)
        #     return
        # if self._thread.isRunning():
        #     self._thread.requestInterruption()
        #     self._thread.quit()
        #     self._thread.wait()
            # 强制
            # self._thread.terminate()
        # self._thread.deleteLater()
        super(Window, self).closeEvent(event)


if __name__ == '__main__':
    import sys
    import cgitb

    cgitb.enable(format='text')
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())
