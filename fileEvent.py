# 从视频中检测到的事项
# 使用：
# a = ["index", "type", "start", "end", "total"]
# b = pd.DataFrame(columns=a)
# from fileEvent import fileEvent
# c = fileEvent(0, "xiyan", 30, 2300, 4500)
# d = c.__dict__
# d
# {'index': 0, 'type': 'xiyan', 'start': 30, 'end': 2300, 'total': 4500}
# e = pd.Series(d)
# b = b.append(e, ignore_index=True)
# b = b.append(e, ignore_index=True)
# b = b.append(e, ignore_index=True)
# b.to_csv("./result/smoke_1638263955553461.csv")
# f = pd.read_csv("./result/smoke_1638263955553461.csv")
# f = pd.read_csv("./result/smoke_1638263955553461.csv")
# f = pd.read_csv("./result/smoke_1638263955553461.csv", index_col=0)
# f.index = list(np.arange(42))
# f["index"] = pd.Series(list(np.arange(42)), index=list(np.arange(42)))
# f.to_csv("./result/smoke_1638263955553461.csv")
class fileEvent(object):
    def __init__(self, index, type, start, end, total):
        self.index = index
        self.type = type
        self.start = start
        self.end = end
        self.total = total

    def keys(self):
        # 当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
        # 但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加一个方法
        return "index", "type", "start", "end", "total"

    def __getitem__(self, item):
        # 内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值
        return getattr(self, item)

