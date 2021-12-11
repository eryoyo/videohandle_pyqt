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
    def __init__(self, index, filepath, status=0, process_path="", taibiao_1=0, taibiao_2=0, 
                 taibiao_3=0, taibiao_4=0, taibiao_5=0, taibiao_6=0, taibiao_7=0, taibiao_8=0, 
                 taibiao_9=0, taibiao_10=0, taibiao_11=0, taibiao_12=0, taibiao_13=0, taibiao_14=0, 
                 taibiao_15=0, taibiao_16=0, ttv=0, voa=0, xtr=0, smoke=0):
        self.index = index
        self.filepath = filepath
        self.status = status
        self.process_path = process_path
        self.taibiao_1 = taibiao_1
        self.taibiao_2 = taibiao_2
        self.taibiao_3 = taibiao_3
        self.taibiao_4 = taibiao_4
        self.taibiao_5 = taibiao_5
        self.taibiao_6 = taibiao_6
        self.taibiao_7 = taibiao_7
        self.taibiao_8 = taibiao_8
        self.taibiao_9 = taibiao_9
        self.taibiao_10 = taibiao_10
        self.taibiao_11 = taibiao_11
        self.taibiao_12 = taibiao_12
        self.taibiao_13 = taibiao_13
        self.taibiao_14 = taibiao_14
        self.taibiao_15 = taibiao_15
        self.taibiao_16 = taibiao_16
        self.ttv = ttv
        self.voa = voa
        self.xtr = xtr
        self.smoke = smoke
        
    def keys(self):
        # 当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
        # 但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加一个方法
        return "index", "filepath", "status", "process_path", "taibiao_1", "taibiao_2", "taibiao_3", "taibiao_4", "taibiao_5", "taibiao_6", \
                              "taibiao_7", "taibiao_8", "taibiao_9", "taibiao_10", "taibiao_11", "taibiao_12", \
                              "taibiao_13", "taibiao_14", "taibiao_15", "taibiao_16", "ttv", "voa", "xtr", "smoke"
    
    def __getitem__(self, item):
        # 内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值
        return getattr(self, item)
    
