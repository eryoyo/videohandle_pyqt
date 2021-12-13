# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

############################ wait to do #############################
import json
from random import randint

import cv2
import pandas as pd

from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimediaWidgets
from PyQt5.QtCore import QDateTime, QTimer, QSize, Qt
from PyQt5.QtGui import QGuiApplication, QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QFileDialog, QProgressBar, QListWidgetItem, QLabel, QMessageBox, QGridLayout, QCheckBox

from fileEventDetailView import fileEventDetailView
from fileRecord import fileRecord
from fileRecordView_finish import fileRecordView_finish
from fileRecordView_wait import fileRecordView_wait
from settingView import settingView
from threadDemo import threadDemo
from videoSlider import videoSlider


class Ui_MainWindow(object):
    def __init__(self):
        # 状态变量集散地

        # 控制播放与否的状态变量，False表示处于暂停状态，选中某一个视频之后默认就开始播放
        self.VIDEO_STATUS = True
        # 控制播放器进度条是否被点击，也就是当前视频进度正在受到人为调整
        self.VIDEO_SLIDER_STATUS = False

        # 中转变量集散地

        # 设置的字典
        self.dict_setting = {}
        # 文件列表
        self.csv_df = pd.read_csv("./file.csv", index_col=0)
        # 事件列表
        self.list_event_py = ["taibiao_1", "taibiao_2", "taibiao_3", "taibiao_4", "taibiao_5", "taibiao_6", 
                              "taibiao_7", "taibiao_8", "taibiao_9", "taibiao_10", "taibiao_11", "taibiao_12", 
                              "taibiao_13", "taibiao_14", "taibiao_15", "taibiao_16", "ttv", "voa", "xtr", 
                              "zhuangjia", "daoju", "qiangzhi", "smoke"]
        self.list_event = ["台标1", "台标2", "台标3", "台标4", "台标5", "台标6", "台标7", "台标8", "台标9", "台标10", "台标11", 
                           "台标12", "台标13", "台标14", "台标15", "台标16", "ttv", "voa", "xtr", "装甲", "刀具", "枪支", "吸烟"]
        # 总帧数
        self.num_frame = 0
        # 处理好的视频的帧数之和
        self.num_handled = 0
        # 当前处理的视频的总帧数
        self.num_frame_cur = 0
        # 当前处理的视频的处理好的帧数
        self.num_handled_cur = 0

    def setupUi(self, MainWindow):
        # 最外围的主窗口，不要改动
        MainWindow.setObjectName("MainWindow")
        # 非最初的1200*900，原因是窗口的底部会有一定像素的遮挡，需要适当放大，经过实验得到最优的高906
        MainWindow.resize(1200, 906)
        # 已解决，在app上设置应用图标
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("img/Icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(self.icon)
        # 禁止窗口进行最大化操作，固定窗口大小
        MainWindow.setFixedSize(MainWindow.width(), MainWindow.height());
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 窗口左右两边分隔栏，默认为平分，主要操作是将左侧的最大长度设置一下可以达到不平分的效果
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(0, 0, 1200, 879))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        # 左侧窗口
        self.widget_left = QtWidgets.QWidget(self.splitter)
        self.widget_left.setMaximumSize(QtCore.QSize(396, 16777215))
        self.widget_left.setObjectName("widget_left")
        # 布局之用
        self.layoutWidget = QtWidgets.QWidget(self.widget_left)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 401, 881))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_left = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_left.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_left.setObjectName("horizontalLayout_left")
        # 左侧主体 
        # 需求是当点击list里面的选项，stacked需要跟着动，
        # 然后stacked显示的是视频文件的详情列表，又是一个list
        # 整个系统的文件列表分为待处理的，已处理完毕的，使用dataframe维护，类型列区分两种类型，所以有csv文件
        self.listView_left_left = QtWidgets.QListWidget(self.layoutWidget)
        self.listView_left_left.setMaximumSize(QtCore.QSize(88, 16777215))
        self.listView_left_left.setObjectName("listView_left_left")
        self.choice = ["处理完成", "处理中", "上传文件", "设置"]
        for i in range(len(self.choice)):
            item = QListWidgetItem(self.icon, self.choice[i], self.listView_left_left)
            # 设置item的默认宽高(这里只有高度比较有用)
            item.setSizeHint(QSize(86, 60))
            # 文字居中
            item.setTextAlignment(Qt.AlignCenter)
        self.horizontalLayout_left.addWidget(self.listView_left_left)

        # 页面左侧的四个单独的页面
        self.stackedWidget_left_right = QtWidgets.QStackedWidget(self.layoutWidget)
        self.stackedWidget_left_right.setObjectName("stackedWidget_left_right")
        # self.stackedWidget_left_right.setStyleSheet("background: black")
        # 根据不同的选项来从dataframe加载文件
        self.page_finish = QtWidgets.QWidget(self.stackedWidget_left_right)
        self.page_finish.setObjectName("page_finish")
        self.listWidget_page_finish = QtWidgets.QListWidget(self.page_finish)
        self.listWidget_page_finish.setGeometry(QtCore.QRect(0, 0, 303, 881))
        self.load_page_finish()
        self.stackedWidget_left_right.addWidget(self.page_finish)
        self.page_wait = QtWidgets.QWidget(self.stackedWidget_left_right)
        self.page_wait.setObjectName("page_wait")
        self.listWidget_page_wait = QtWidgets.QListWidget(self.page_wait)
        self.listWidget_page_wait.setGeometry(QtCore.QRect(0, 0, 303, 881))
        self.load_page_wait()
        self.stackedWidget_left_right.addWidget(self.page_wait)
        # 上传文件，主要是将扫描的文件添加到dataframe中，将相应的列表项填好，并且重新加载上两个页面
        self.page_upload = QtWidgets.QWidget(self.stackedWidget_left_right)
        self.page_upload.setObjectName("page_upload")
        self.btn_open = QtWidgets.QPushButton(self.page_upload)
        self.btn_open.setGeometry(QtCore.QRect(25, 25, 200, 60))
        self.btn_open.setObjectName("btn_open")
        self.stackedWidget_left_right.addWidget(self.page_upload)
        # 设置页面，里面需要有一个多选框列表
        self.page_setting = QtWidgets.QWidget(self.stackedWidget_left_right)
        self.page_setting.setObjectName("page_setting")
        self.listWidget_page_setting = QtWidgets.QListWidget(self.page_setting)
        self.listWidget_page_setting.setGeometry(QtCore.QRect(0, 0, 303, 881))
        self.load_setting()
        self.stackedWidget_left_right.addWidget(self.page_setting)
        self.horizontalLayout_left.addWidget(self.stackedWidget_left_right)

        # 右侧窗口
        self.widget_right = QtWidgets.QWidget(self.splitter)
        self.widget_right.setMaximumSize(QtCore.QSize(796, 16777215))
        self.widget_right.setObjectName("widget_right")
        # 右侧上边的进度条，需要有定时器实时更新
        self.widget_right_up = QtWidgets.QWidget(self.widget_right)
        self.widget_right_up.setGeometry(QtCore.QRect(0, 0, 800, 50))
        self.widget_right_up.setObjectName("widget_right_up")
        self.progress = QProgressBar(self.widget_right_up)
        self.progress.setValue(0)
        self.progress.setGeometry(QtCore.QRect(22, 20, 550, 50))
        self.progress.setObjectName("progress")
        self.progress_label = QLabel(self.widget_right_up)
        self.progress_label.setObjectName("progress_label")
        self.progress_label.setGeometry(QtCore.QRect(582, 10, 180, 50))

        # 右侧中部的视频播放，主要控制路径为中部的播放按钮和进度条以及右侧下部的播放按钮
        self.widget_right_middle = QtWidgets.QWidget(self.widget_right)
        self.widget_right_middle.setGeometry(QtCore.QRect(0, 50, 800, 500))
        self.widget_right_middle.setObjectName("widget_right_middle")

        # 右侧中部的播放器窗口
        self.wgt_video = QtMultimediaWidgets.QVideoWidget(self.widget_right_middle)
        self.wgt_video.setGeometry(QtCore.QRect(22, 10, 750, 380))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.wgt_video.setPalette(palette)
        self.wgt_video.setAutoFillBackground(True)
        self.wgt_video.setObjectName("wgt_video")

        # 视频配套的滚动条
        self.sld_video = videoSlider(self.widget_right_middle)
        self.sld_video.setGeometry(QtCore.QRect(22, 400, 700, 30))
        self.sld_video.setMaximum(100)
        self.sld_video.setOrientation(QtCore.Qt.Horizontal)
        self.sld_video.setObjectName("sld_video")
        # 视频滚动条对应的进度关系
        self.lab_video = QtWidgets.QLabel(self.widget_right_middle)
        self.lab_video.setGeometry(QtCore.QRect(730, 400, 50, 30))
        self.lab_video.setObjectName("lab_video")

        self.widget_right_middle_down = QtWidgets.QWidget(self.widget_right_middle)
        self.widget_right_middle_down.setGeometry(QtCore.QRect(22, 435, 750, 60))
        # self.widget_right_middle_down.setStyleSheet('background: rgb(%d, %d, %d);margin: 0px;' % (
        #         randint(0, 255), randint(0, 255), randint(0, 255)))
        self.btn_play = QtWidgets.QPushButton(self.widget_right_middle_down)
        self.btn_play.setGeometry(QtCore.QRect(100, 0, 80, 60))
        self.btn_play.setObjectName("btn_play")
        self.sld_audio = QtWidgets.QSlider(self.widget_right_middle_down)
        self.sld_audio.setGeometry(QtCore.QRect(300, 0, 80, 60))
        self.sld_audio.setProperty("value", 99)
        self.sld_audio.setOrientation(QtCore.Qt.Horizontal)
        self.sld_audio.setObjectName("sld_audio")
        self.lab_audio = QtWidgets.QLabel(self.widget_right_middle_down)
        self.lab_audio.setGeometry(QtCore.QRect(400, 0, 80, 60))
        self.lab_audio.setObjectName("lab_audio")

        # 下部，主要是按照对应的处理后文件生成的展示
        self.widget_right_down = QtWidgets.QWidget(self.widget_right)
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

        self.load_right_down()
        self.horizontalLayout_right_down.addWidget(self.listWidget_right_down_left)
        self.horizontalLayout_right_down.addWidget(self.stackedWidget_right_down_right)

        # 后期补充菜单栏和状态栏，不紧迫
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.stackedWidget_right_down_right.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.addAction()
        self.startHandle()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "视频检测"))
        self.lab_video.setText(_translate("MainWindow", "0%"))
        self.btn_open.setText(_translate("MainWindow", "上传视频文件"))
        self.btn_play.setText(_translate("MainWindow", "暂停"))
        self.lab_audio.setText(_translate("MainWindow", "volume:100%"))

    # 添加响应的槽函数位置，统一配置
    def addAction(self):
        # 控制视频相关
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.wgt_video)  # 视频播放输出的widget，就是上面定义的
        self.btn_open.clicked.connect(self.openVideoFile)  # 打开视频文件按钮
        self.btn_play.clicked.connect(self.changeVideoStatus)  # play
        self.player.positionChanged.connect(self.changeSlide)  # change Slide
        self.sld_video.setTracking(False)
        self.sld_video.sliderReleased.connect(self.releaseSlider)
        self.sld_video.sliderPressed.connect(self.pressSlider)
        self.sld_video.sliderMoved.connect(self.moveSlider)  # 进度条拖拽跳转
        self.sld_video.ClickedValue.connect(self.clickedSlider)  # 进度条点击跳转
        self.sld_audio.valueChanged.connect(self.volumeChange)  # 控制声音播放
        self.sld_audio.sliderReleased.connect(self.volumeChanged)  # 打印修改后的音量

        # 控制进度条的源头
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.updateProgress)
        # self.timer.start(randint(1, 3) * 1000)

        # 控制转换页面
        self.listView_left_left.currentRowChanged.connect(
            lambda cur: self.stackedWidget_left_right.setCurrentIndex(cur))
        self.listWidget_right_down_left.currentRowChanged.connect(self.stackedWidget_right_down_right.setCurrentIndex)

        # 设置页面的槽函数
        # 在添加checkbox的时候就添加了槽函数
        
        # 文件列表槽函数
        
    # 启动线程开始处理视频
    # 首先计算出总的视频的帧数和处理好的视频的帧数
    # 然后选择等待处理列表里面的一个视频开始处理，获取这个视频的总帧数
    def startHandle(self):
        # 计算视频总帧数以及处理好的视频的帧数
        for i in range(len(self.csv_df)):
            cur = self.csv_df.iloc[i]
            cap = cv2.VideoCapture(cur['filepath'])
            cur_frame = cap.get(7)
            if cur['status'] == 1:
                self.num_handled += cur_frame
            self.num_frame += cur_frame
        self.progress_label.setText(str(self.num_handled) + '/' + str(self.num_frame))
        
        # 开启子线程开始处理视频文件
        df_wait = self.csv_df[self.csv_df["status"] == 0]
        if len(df_wait) == 0:
            return
        self.df_cur = df_wait.iloc[0]
        cap = cv2.VideoCapture(self.df_cur['filepath'])
        self.num_frame_cur = cap.get(7)
        self._thread = threadDemo(self.df_cur)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.valueChanged.connect(self.updateProgress)
        self._thread.start()  # 启动线程

    # 加载设置界面
    def load_setting(self):
        print("开始加载设置文件：")
        with open("./config.json", 'r') as setting_file:
            self.dict_setting = json.load(setting_file)
            print(self.dict_setting)
        for i in range(len(self.list_event_py)):
            item = QListWidgetItem(self.listWidget_page_setting)
            item.setSizeHint(QSize(300, 40))
            item_setting = settingView(self.list_event_py[i], self.dict_setting[self.list_event_py[i]], self.list_event[i])
            item_setting.stateChange.connect(self.checkStateChange)
            self.listWidget_page_setting.setItemWidget(item, item_setting)
        print("设置界面加载完毕")

    # 加载处理完毕视频列表界面
    def load_page_finish(self):
        print("开始加载处理完毕的视频列表界面。。。")
        df_finish = self.csv_df[self.csv_df["status"] == 1]
        for i in range(len(df_finish)):
            item = QListWidgetItem(self.listWidget_page_finish)
            item.setSizeHint(QSize(300, 80))
            item_finish = fileRecordView_finish(df_finish.iloc[i])
            item_finish.itemSelected.connect(self.finishitem_selected)
            self.listWidget_page_finish.setItemWidget(item, item_finish)
        print("处理完毕视频列表界面加载完毕。。。")

    # 加载正在处理视频列表界面
    def load_page_wait(self):
        print("开始加载等待处理的视频列表界面。。。")
        df_wait = self.csv_df[self.csv_df["status"] == 0]
        # print(df_wait)
        for i in range(len(df_wait)):
            item = QListWidgetItem(self.listWidget_page_wait)
            item.setSizeHint(QSize(300, 80))
            item_wait = fileRecordView_wait(df_wait.iloc[i])
            item_wait.itemSelected.connect(self.waititem_selected)
            self.listWidget_page_wait.setItemWidget(item, item_wait)
        print("等待处理视频列表界面加载完毕。。。")
        
    # 槽函数：finish界面的文件项被选择了
    def finishitem_selected(self, index):
        print(str(index) + "finish被选择了")
        curItem = self.csv_df[self.csv_df["index"] == index].iloc[0]
        # 视频加载
        pathUrl = QtCore.QUrl("file://" + curItem["filepath"])
        print(pathUrl)
        self.player.setMedia(QMediaContent(pathUrl))  # 选取视频文件
        self.player.play()  # 播放视频
        # 视频处理列表需要加载，一个视频对应一个处理文件
        self.load_right_down(index=index)
            
    # 槽函数：wait界面的文件项被选择了
    def waititem_selected(self, index):
        print(str(index) + "wait被选择了")
        curItem = self.csv_df[self.csv_df["index"] == index].iloc[0]
        # 视频加载
        pathUrl = QtCore.QUrl("file://" + curItem["filepath"])
        print(pathUrl)
        self.player.setMedia(QMediaContent(pathUrl))  # 选取视频文件
        self.player.play()  # 播放视频
        
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
        
    # 屏幕截图的功能，暂未使用
    def castVideo(self):
        screen = QGuiApplication.primaryScreen()
        cast_jpg = './' + QDateTime.currentDateTime().toString("yyyy-MM-dd hh-mm-ss-zzz") + '.jpg'
        screen.grabWindow(self.wgt_video.winId()).save(cast_jpg)

    # 控制音量
    def volumeChange(self, position):
        volume = round(position / self.sld_audio.maximum() * 100)
        # print("vlume %f" % volume)
        self.player.setVolume(volume)
        self.lab_audio.setText("volume:" + str(volume) + "%")

    # 修改音量后输出修改后的音量
    def volumeChanged(self):
        print("修改后的音量：volume %f" % self.player.volume())

    # 人为控制播放器进度条
    def clickedSlider(self, position):
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            self.lab_video.setText("%.2f%%" % position)
            if self.sld_video.value() == 100:
                self.btn_play.setText("播放")
                self.player.setPosition(0)
                self.player.pause()
        else:
            self.sld_video.setValue(0)

    # 人为控制播放器进度条
    def moveSlider(self, position):
        self.VIDEO_SLIDER_STATUS = True
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            self.lab_video.setText("%.2f%%" % position)
            if self.sld_video.value() == 100:
                self.btn_play.setText("播放")
                self.player.setPosition(0)
                self.player.pause()

    # 点击来视频的进度条，主要用来将人为控制视频进度和视频播放器控制进度两个信号分开
    def pressSlider(self):
        self.VIDEO_SLIDER_STATUS = True
        print("video slider pressed")

    # 松开点击视频进度条
    def releaseSlider(self):
        self.VIDEO_SLIDER_STATUS = False

    # 当没有人为控制进度条的时候使用视频播放器自动控制
    def changeSlide(self, position):
        if not self.VIDEO_SLIDER_STATUS:  # 进度条被鼠标点击时不更新
            self.vidoeLength = self.player.duration() + 0.1
            self.sld_video.setValue(round((position / self.vidoeLength) * 100))
            self.lab_video.setText("%.2f%%" % ((position / self.vidoeLength) * 100))
            if self.sld_video.value() == 100:
                self.btn_play.setText("播放")
                self.player.setPosition(0)
                self.player.pause()

    def openVideoFile(self):
        # temp = QFileDialog.getOpenFileUrl()[0]
        # print(temp.toString()[7:])
        # self.player.setMedia(QMediaContent(temp))  # 选取视频文件
        # self.player.play()  # 播放视频
        # print("availableMetaData: " + str(self.player.availableMetaData()))
        # 上传文件响应的槽函数，这个是上传单个文件，主要是将该视频文件添加到csv_df中，
        # 当前处理视频文件的线程打开方式是一个视频文件处理完启动下一个视频文件的处理，所以需要在当前文件添加到csv_df中之后
        # 首先判断当前是否还有文件在等待处理，如果有就结束，假如没有就启动当前添加文件的处理
        filename = QFileDialog.getOpenFileNames(filter='videos: (*.mp4)')[0]
        if len(filename) == 0:
            print('没有选择任何文件')
            return
        print('选择了文件', filename)
        df_wait = self.csv_df[self.csv_df["status"] == 0]
        len_handled = len(df_wait)
        index = len(self.csv_df)
        record_cur = fileRecord(index, filename[0], 0, '')
        for i, cur_event in enumerate(self.list_event_py):
            if self.dict_setting[cur_event]:
                record_cur.__setattr__(cur_event, 1)
        self.csv_df = self.csv_df.append(pd.Series(record_cur.__dict__), ignore_index=True)
        self.csv_df.to_csv('file.csv')
        # 开启处理该文件
        # 将该文件的总帧数添加到整个系统中添加文件的总帧数
        self.df_cur = self.csv_df[self.csv_df["index"] == index].iloc[0]
        cap = cv2.VideoCapture(self.df_cur['filepath'])
        frame_cur = cap.get(7)
        self.num_frame += frame_cur
        # 将该文件添加到处理列表当中
        item = QListWidgetItem(self.listWidget_page_wait)
        item.setSizeHint(QSize(300, 80))
        item_wait = fileRecordView_wait(self.df_cur)
        item_wait.itemSelected.connect(self.waititem_selected)
        self.listWidget_page_wait.setItemWidget(item, item_wait)
        if len_handled == 0:
            self.num_frame_cur = frame_cur
            self._thread = threadDemo(self.df_cur)
            self._thread.finished.connect(self._thread.deleteLater)
            self._thread.valueChanged.connect(self.updateProgress)
            self._thread.start()  # 启动线程

    # 控制视频播放与否的按钮
    def changeVideoStatus(self):
        if self.VIDEO_STATUS:
            self.player.pause()
            self.btn_play.setText("播放")
            self.VIDEO_STATUS = False
        else:
            self.player.play()
            self.btn_play.setText("暂停")
            self.VIDEO_STATUS = True

    # 设置选项改变
    def checkStateChange(self, choice):
        print(choice)
        self.dict_setting[choice] = False if self.dict_setting[choice] else True
        with open("./config.json", "w") as file_setting:
            json.dump(self.dict_setting, file_setting)
            print("设置更新完成")
            print(self.dict_setting)

    # 每隔一秒更新一次系统进度条和当前的进度条
    def updateProgress(self, i):
        # if self.progress.value() >= 100:
        #     self.timer.stop()
        #     self.timer.deleteLater()
        #     del self.timer
        #     return
        self.num_handled_cur = i + 1
        if self.num_handled_cur == self.num_frame_cur:
            self.num_handled += self.num_frame_cur
            self.num_handled_cur = 0
            self.num_frame_cur = 0
            # 将当前文件的状态修改为已完成
            index = self.df_cur['index']
            self.csv_df.iloc[index, 2] = 1
            self.csv_df.to_csv('file.csv')
            # 将当前的文件从wait里面去掉
            item = self.listWidget_page_wait.takeItem(0)
            self.listWidget_page_wait.removeItemWidget(item)
            # 将当前文件添加到处理结束finish列表里面
            item = QListWidgetItem(self.listWidget_page_finish)
            item.setSizeHint(QSize(300, 80))
            item_finish = fileRecordView_finish(self.df_cur)
            item_finish.itemSelected.connect(self.finishitem_selected)
            self.listWidget_page_finish.setItemWidget(item, item_finish)
            
            # 选择一个新的视频进行处理
            df_wait = self.csv_df[self.csv_df["status"] == 0]
            if len(df_wait) == 0:
                return
            self.df_cur = df_wait.iloc[0]
            cap = cv2.VideoCapture(self.df_cur['filepath'])
            self.num_frame_cur = cap.get(7)
            self._thread = threadDemo(self.df_cur)
            self._thread.finished.connect(self._thread.deleteLater)
            self._thread.valueChanged.connect(self.updateProgress)
            self._thread.start()  # 启动线程
        # 更新整体进度值
        self.progress.setValue(int((self.num_handled_cur + self.num_handled) * 100 / self.num_frame))
        self.progress_label.setText(str(self.num_handled + self.num_handled_cur) + '/' + str(self.num_frame))
        # self.listWidget_page_wait.takeItem(0)..progress_wait.setValue(100 * self.num_handled_cur / self.num_frame_cur)

    # 利用子线程来处理视频，在过程中需要实时改变系统进度条的值，也就是当前已处理完的帧
    def handleVideo(self):
        pass
