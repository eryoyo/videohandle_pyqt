# 文件列表里面的每一项
class fileRecord(object):
    def __init__(self, index, filepath, status=0, xiyan=0, xiyan_path=None, baoli=0, baoli_path=None, xuexing=0, xuexing_path=None):
        self.index = index
        self.filepath = filepath
        self.status = status
        self.xiyan = xiyan
        self.xiyan_path = xiyan_path
        self.baoli = baoli
        self.baoli_path = baoli_path
        self.xuexing = xuexing
        self.xuexing_path = xuexing_path
        
