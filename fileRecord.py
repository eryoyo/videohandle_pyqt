# 文件列表里面的每一项
# 使用：
# from fileRecord import fileRecord
# a = fileRecord(0, "filePath", 0, 0, "xiyan", 0, "baoli", 0, "xuexing")
# a.keys()
# import pandas as pd
# b = pd.DataFrame(columns=a.keys())
# c = a.__dict__ 也可以使用dict(a)
# d = pd.Series(c) 这个地方可以指定name属性作为添加后的index但是当前情况下没有必要
# b = b.append(d, ignore_index=True)
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
        
    def keys(self):
        # 当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
        # 但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加一个方法
        return "index", "filepath", "status", "xiyan", "xiyan_path", "baoli", "baoli_path", "xuexing", "xuexing_path"
    
    def __getitem__(self, item):
        # 内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值
        return getattr(self, item)
    
