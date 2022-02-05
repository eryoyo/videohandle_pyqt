import pika
from data_pb2 import Frame

'''
发送结果到后端
'''


class ResultSender:

    def __init__(self, queue='resultsender'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue)

    def produce(self, fileIndex, frameIndex):
        message = Frame(
            fileIndex=fileIndex, 
            frameIndex=frameIndex
        )
        message2 = message.SerializeToString()
        self.channel.basic_publish(exchange='',
                                   routing_key='resultsender',
                                   body=message2)
        print('result message produced')
        return 'result message produced'
