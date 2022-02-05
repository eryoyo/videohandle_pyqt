import base64
import time

import numpy as np
import pika

from ResultSender import ResultSender
from data_pb2 import Frame
import cv2

'''
模拟的后端处理
'''


class FrameReceiver:

    def __init__(self, host='localhost', queue='framesender'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue)
        self.channel.basic_consume(queue, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        message = Frame()
        message.ParseFromString(body)
        fileIndex = message.fileIndex
        frameIndex = message.frameIndex
        frame = message.b64image
        width = message.width
        height = message.height
        img = base64.b64decode(frame)
        imgarr = np.frombuffer(img, dtype=np.uint8).reshape(width, height, -1)
        print(imgarr.shape)
        time.sleep(0.05)
        resultSender = ResultSender()
        resultSender.produce(fileIndex, frameIndex)
        # cv2.imshow('get', imgarr)
        # cv2.waitKey(50)
        print(f"Received from file{message.fileIndex} frame{message.frameIndex}")
        return ['message recieved']

if __name__ == "__main__":
    print(' [*] Waiting for messages. To exit press CTRL+C')
    rabbitmq = FrameReceiver()
    consume = rabbitmq.callback()
