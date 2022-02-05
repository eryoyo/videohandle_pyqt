import pika
from data_pb2 import Frame

'''
发送图片到后端
'''


class FrameSender:

    def __init__(self, queue='framesender'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue)

    def produce(self, fileIndex, frameIndex, b64image, width, height):
        message = Frame(
            fileIndex=fileIndex, 
            frameIndex=frameIndex, 
            b64image=b64image,
            width=width,
            height=height
        )
        message2 = message.SerializeToString()
        self.channel.basic_publish(exchange='',
                                   routing_key='framesender',
                                   body=message2)
        print('message produced')
        return 'message produced'
