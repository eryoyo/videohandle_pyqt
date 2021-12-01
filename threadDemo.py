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
        for i in range(self.frame_num):
            if self.isInterruptionRequested():
                break
            print('value', i)
            self.valueChanged.emit(i)
            QThread.sleep(1)
        # 最后需要将当前视频文件中的检测事件保存起来
        
