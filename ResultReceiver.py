import pika
from PyQt5.QtCore import QThread, pyqtSignal

from data_pb2 import Result

'''
接收返回消息的线程
在此处完成返回消息的汇总
'''


class ResultReceiver(QThread):
    frameGet = pyqtSignal()  # 收到一帧的信号
    handleFinished = pyqtSignal(int)  # 某一个文件处理完成的信号

    # 初始化消息队列的参数
    def __init__(self, host='localhost', queue='resultsender'):
        super(ResultReceiver, self).__init__()
        self.host = host
        self.queue = queue

    '''
    开启消息队列的消息接收所需
    '''
    def run(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(self.queue)
        self.channel.basic_consume(self.queue, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()
    
    '''
    接收到的消息的处理
        没接收一帧需要将该帧添加到结果中并发送消息更新进度条
        如果接收的帧是文件里面未处理的最后一帧就发送消息展示一个文件处理完成
    '''
    def callback(self, ch, method, properties, body):
        message = Result()
        message.ParseFromString(body)
        fileIndex = message.fileIndex
        frameIndex = message.frameIndex
        # self.frameGet.emit()
        print(f"Received from file{fileIndex} frame{frameIndex}")
        return ['message recieved']


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
        self._thread = ResultReceiver()
        self._thread.frameGet.connect(
            lambda: self.progressBar.setValue(round((self.progressBar.value() + 1) / 3307 * 100)))

    def onStart(self):
        if not self._thread.isRunning():
            print('main id', QThread.currentThread())
            self._thread.start()  # 启动线程


if __name__ == '__main__':
    import sys
    import cgitb

    cgitb.enable(format='text')
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())
