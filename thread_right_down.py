from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QListWidgetItem

from fileEventDetailView import fileEventDetailView
import pandas as pd


class thread_right_down(QThread):
    thread_finished = pyqtSignal(QtWidgets.QWidget)
    
    def __init__(self, index):
        super(thread_right_down, self).__init__()
        self.index = index
        self.csv_df = pd.read_csv("./file.csv", index_col=0)
        self.list_event_py = ["taibiao_1", "taibiao_2", "taibiao_3", "taibiao_4", "taibiao_5", "taibiao_6",
                              "taibiao_7", "taibiao_8", "taibiao_9", "taibiao_10", "taibiao_11", "taibiao_12",
                              "taibiao_13", "taibiao_14", "taibiao_15", "taibiao_16", "ttv", "voa", "xtr",
                              "zhuangjia", "daoju", "qiangzhi", "smoke"]
        self.list_event = ["台标1", "台标2", "台标3", "台标4", "台标5", "台标6", "台标7", "台标8", "台标9", "台标10", "台标11",
                           "台标12", "台标13", "台标14", "台标15", "台标16", "ttv", "voa", "xtr", "装甲", "刀具", "枪支", "吸烟"]

        self.icon = QIcon()
        self.icon.addPixmap(QPixmap("img/Icon.png"), QIcon.Normal, QIcon.Off)
        
        self.widget_right_down = QtWidgets.QWidget()
        self.widget_right_down.setGeometry(QtCore.QRect(0, 550, 800, 328))
        self.widget_right_down.setObjectName("widget_right_down")
        self.layoutWidget1 = QtWidgets.QWidget(self.widget_right_down)
        self.layoutWidget1.setGeometry(QtCore.QRect(0, 0, 801, 331))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_right_down = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_right_down.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_right_down.setObjectName("horizontalLayout_right_down")

        self.listWidget_right_down_left = QtWidgets.QListWidget(self.layoutWidget1)
        self.listWidget_right_down_left.setMaximumSize(QtCore.QSize(88, 16777215))
        self.listWidget_right_down_left.setObjectName("listWidget_right_down_left")

        self.stackedWidget_right_down_right = QtWidgets.QStackedWidget(self.layoutWidget1)
        self.stackedWidget_right_down_right.setObjectName("stackedWidget_right_down_right")

        self.listWidget_right_down_left.currentRowChanged.connect(self.stackedWidget_right_down_right.setCurrentIndex)
        
    def run(self):
        print('thread id:', QThread.currentThread())
        self.load_right_down(self.index)
        self.thread_finished.emit(self.widget_right_down)

    # 根据index的设置来加载对应的事件界面
    def load_right_down(self, index=-1):
        if index == -1:
            finish_df = self.csv_df[self.csv_df["status"] == 1]
            if len(finish_df) != 0:
                loadItem = finish_df.iloc[0]
                self.load_right_down_Byitem(loadItem)
        else:
            loadItem = self.csv_df[self.csv_df["index"] == index].iloc[0]
            self.load_right_down_Byitem(loadItem)
            print("当前加载", loadItem['filepath'])

    # 根据file文件中的某一项来加载对应的事件页面
    def load_right_down_Byitem(self, loadItem):
        # 加载right_down_left
        list_happen = []
        for i, event in enumerate(self.list_event_py):
            if loadItem[event] == 2:
                list_happen.append(event)
                # 添加菜单栏
                item = QListWidgetItem(self.icon, self.list_event[i], self.listWidget_right_down_left)
                # 设置item的默认宽高(这里只有高度比较有用)
                item.setSizeHint(QSize(86, 60))
                # 文字居中
                item.setTextAlignment(Qt.AlignCenter)

        # 加载right_down_right
        process_path = loadItem["process_path"]
        self.load_right_down_Byfile(process_path, list_happen, loadItem["filepath"])

    # 根据事件文件的名称来加载对应的视频文件事件项
    def load_right_down_Byfile(self, process_path, list_happen, filepath):
        event_df = pd.read_csv(process_path)
        for event in list_happen:
            print("开始处理：", event)
            event_df_cur = event_df[event_df["type"] == event]
            page_right_down_right = QtWidgets.QWidget(self.stackedWidget_right_down_right)
            page_right_down_right.setObjectName("page_right_down_right")
            listWidget_page_right_down_right = QtWidgets.QListWidget(page_right_down_right)
            listWidget_page_right_down_right.setGeometry(QtCore.QRect(0, 0, 703, 328))
            self.load_page_right_down_right(event_df_cur, listWidget_page_right_down_right, filepath)
            self.stackedWidget_right_down_right.addWidget(page_right_down_right)
            print("完成处理：", event)

    # 加载每一个事件类型的子页面    
    def load_page_right_down_right(self, event_df_cur, listWidget_page_right_down_right, filepath):
        for i in range(len(event_df_cur)):
            item = QListWidgetItem(listWidget_page_right_down_right)
            item.setSizeHint(QSize(700, 60))
            item_finish = fileEventDetailView(event_df_cur.iloc[i], filepath)
            item_finish.btn_play_clicked.connect(self.play_item)
            listWidget_page_right_down_right.setItemWidget(item, item_finish)

    # 槽函数：点击来视频事件列表里面的某一项        
    def play_item(self, start):
        self.player.setPosition(start)
