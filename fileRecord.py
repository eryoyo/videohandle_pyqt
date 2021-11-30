# 文件列表里面的每一项
# 使用：
# from fileRecord import fileRecord
# a = fileRecord(0, "/Users/chenjialin/Downloads/smoke.mp4", 0, "./result/smoke_1638263955553461.csv", 0, 0, 0)
# a.keys()
# import pandas as pd
# b = pd.DataFrame(columns=a.keys())
# c = a.__dict__ 也可以使用dict(a)
# d = pd.Series(c) 这个地方可以指定name属性作为添加后的index但是当前情况下没有必要
# b = b.append(d, ignore_index=True)
class fileRecord(object):
    def __init__(self, index, filepath, status=0, process_path="", xiyan=0, baoli=0, xuexing=0):
        self.index = index
        self.filepath = filepath
        self.status = status
        self.process_path = process_path
        self.xiyan = xiyan
        self.baoli = baoli
        self.xuexing = xuexing
        
    def keys(self):
        # 当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
        # 但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加一个方法
        return "index", "filepath", "status", "process_path", "xiyan","baoli", "xuexing"
    
    def __getitem__(self, item):
        # 内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值
        return getattr(self, item)
    
