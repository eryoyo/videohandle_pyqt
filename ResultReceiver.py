import pika
from PyQt5.QtCore import QThread, pyqtSignal

from data_pb2 import Result

'''
接收返回消息的线程
'''


class ResultReceiver(QThread):
    frameGet = pyqtSignal()  # 收到一帧的信号
    handleFinished = pyqtSignal(int)    # 某一个文件处理完成的信号

    # 初始化消息队列
    def __init__(self, host='localhost', queue='resultsender'):
        super(ResultReceiver, self).__init__()
        self.host = host
        self.queue = queue

    def run(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(self.queue)
        self.channel.basic_consume(self.queue, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()
        
    def callback(self, ch, method, properties, body):
        message = Result()
        message.ParseFromString(body)
        fileIndex = message.fileIndex
        frameIndex = message.frameIndex
        self.frameGet.emit()
        print(f"Received from file{fileIndex} frame{frameIndex}")
        return ['message recieved']
