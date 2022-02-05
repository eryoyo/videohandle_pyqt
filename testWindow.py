# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

############################ wait to do #############################
import base64
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, ALL_COMPLETED
from random import randint
import numpy as np

import cv2
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimediaWidgets
from PyQt5.QtCore import QDateTime, QSize, Qt, QRect, pyqtSignal, QThread, QObject, QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QFileDialog, QProgressBar, QListWidgetItem, QLabel
from atomic import AtomicLong

from FrameSender import FrameSender
from ResultReceiver import ResultReceiver
from fileEventDetailView import fileEventDetailView
from fileRecord import fileRecord
from fileRecordView_finish import fileRecordView_finish
from fileRecordView_wait import fileRecordView_wait
from settingView import settingView
from threadDemo import threadDemo
from videoSlider import videoSlider


class Ui_MainWindow(QObject):
    handleFinished = pyqtSignal(str)  # 值变化信号
    finishFrameUpdate = pyqtSignal(int) # 每一段时间
    frameSending = pyqtSignal(int, int, np.ndarray, int, int)
    
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
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
        self.num_frame = AtomicLong(0)
        # 处理好的视频的帧数之和
        self.num_handled = AtomicLong(0)
        # # 当前处理的视频的总帧数
        # self.num_frame_cur = 0
        # # 当前处理的视频的处理好的帧数
        # self.num_handled_cur = 0
        
        self.frameSender = FrameSender()
        
        self.thread_result = ResultReceiver()
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.task_list = []
        self.executor_send = ThreadPoolExecutor(max_workers=1)
        self.task_list_send = []

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
        # MainWindow.setFixedSize(MainWindow.width(), MainWindow.height());

        # 左侧窗口
        self.widget_left = QtWidgets.QWidget(MainWindow)
        self.widget_left.setGeometry(QRect(0, 0, 401, 900))
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
        self.widget_right = QtWidgets.QWidget(MainWindow)
        # self.widget_right.setMaximumSize(QtCore.QSize(796, 16777215))
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
        # self.layoutWidget1 = QtWidgets.QWidget(self.widget_right_down)
        # self.layoutWidget1.setGeometry(QtCore.QRect(0, 0, 801, 331))
        # self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_right_down = QtWidgets.QHBoxLayout(self.widget_right_down)
        self.horizontalLayout_right_down.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_right_down.setObjectName("horizontalLayout_right_down")

        self.listWidget_right_down_left = QtWidgets.QListWidget(self.widget_right_down)
        self.listWidget_right_down_left.setMaximumSize(QtCore.QSize(88, 16777215))
        self.listWidget_right_down_left.setObjectName("listWidget_right_down_left")

        self.listWidget_right_down_right = QtWidgets.QListWidget(self.widget_right_down)
        self.listWidget_right_down_right.setObjectName("listWidget_right_down_right")
        # self.stackedWidget_right_down_right = QtWidgets.QStackedWidget(self.layoutWidget1)
        # self.stackedWidget_right_down_right.setObjectName("stackedWidget_right_down_right")

        self.load_right_down()
        self.horizontalLayout_right_down.addWidget(self.listWidget_right_down_left)
        # self.horizontalLayout_right_down.addWidget(self.stackedWidget_right_down_right)
        self.horizontalLayout_right_down.addWidget(self.listWidget_right_down_right)

        # 后期补充菜单栏和状态栏，不紧迫
        # MainWindow.setCentralWidget(self.centralwidget)
        # self.menubar = QtWidgets.QMenuBar(MainWindow)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 21))
        # self.menubar.setObjectName("menubar")
        # MainWindow.setMenuBar(self.menubar)
        # self.statusbar = QtWidgets.QStatusBar(MainWindow)
        # self.statusbar.setObjectName("statusbar")
        # MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        # self.stackedWidget_right_down_right.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.addAction()
        self.startHandle()
        self.thread_result.start()

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
        self.sld_video.SliderReleased.connect(self.releaseSlider)
        self.sld_video.SliderPressed.connect(self.pressSlider)
        self.sld_video.SliderMoved.connect(self.moveSlider)  # 进度条拖拽跳转
        self.sld_video.ClickedValue.connect(self.clickedSlider)  # 进度条点击跳转
        self.sld_audio.valueChanged.connect(self.volumeChange)  # 控制声音播放
        self.sld_audio.sliderReleased.connect(self.volumeChanged)  # 打印修改后的音量
        self.handleFinished.connect(self.handleFinish)
        self.frameSending.connect(self.frameSending_func)
        self.thread_result.frameGet.connect(self.frameHandleOne)

        # 控制进度条的源头
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(randint(1, 3) * 1000)

        # 控制转换页面
        self.listView_left_left.currentRowChanged.connect(
            lambda cur: self.stackedWidget_left_right.setCurrentIndex(cur))
        self.listWidget_right_down_left.currentRowChanged.connect(self.load_right_down_Byfile)

        # 设置页面的槽函数
        # 在添加checkbox的时候就添加了槽函数

        # 文件列表槽函数

    def setGeometryAll(self, width, height):
        # self.centralwidget.setGeometry(QRect(0, 0, width, height))
        
        # 左
        self.widget_left.setGeometry(QRect(0, 0, 401, height))
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 401, height))
        self.horizontalLayout_left.setContentsMargins(0, 0, 0, 0)
        self.listView_left_left.setMaximumSize(QSize(88, 16777215))
        self.listWidget_page_finish.setGeometry(QRect(0, 0, 303, height))
        self.listWidget_page_wait.setGeometry(QRect(0, 0, 303, height))
        self.page_upload.setGeometry(QRect(0, 0, 303, height))
        self.btn_open.setGeometry(QRect(25, 25, 200, 60))
        self.listWidget_page_setting.setGeometry(QRect(0, 0, 303, height))

        # 右
        width_right = width - 401 

        height_right_up = int(height * 0.0625)
        x_progress = int(height_right_up * 0.45)
        y_progress = int(height_right_up * 0.25)
        width_progress = int(width_right * 0.6875)
        height_progress = int(height_right_up * 0.5)
        x_progress_label = int(x_progress + width_progress + 20)
        y_progress_label = y_progress
        width_progress_label = int(width_right * 0.225)
        height_progress_label = height_progress

        x_right_middle = 0
        y_right_middle = height_right_up
        width_right_middle = width_right
        height_right_middle = int(height * 0.55)
        x_video = int(width_right_middle * 0.03125)
        y_video = int(height_right_middle * 0.03)
        width_video = int(width_right_middle * 0.9375)
        height_video = int(height_right_middle * 0.80)
        x_slide_video = x_video
        y_slide_video = int(y_video + height_video)
        width_slide_video = int(width_right * 0.85)
        height_slide_video = int(height_right_middle * 0.07)
        x_slide_video_label = int(x_slide_video + width_slide_video + 5)
        y_slide_video_label = y_slide_video
        width_slide_video_label = int(width_right * 0.0625)
        height_slide_video_label = height_slide_video

        x_right_middle_down = x_slide_video
        y_right_middle_down = int(y_slide_video + height_slide_video)
        width_right_middle_down = int(width_right * 0.9375)
        height_right_middle_down = int(height_right_middle * 0.08)
        x_right_down = 0
        y_right_down = height_right_up + height_right_middle
        height_right_down = height - height_right_middle - height_right_up
        width_right_down = width_right
        self.widget_right.setGeometry(QRect(401, 0, width_right, height))

        # 界面右侧上部
        self.widget_right_up.setGeometry(QRect(0, 0, width_right, height_right_up))
        # self.widget_right_up.setStyleSheet('background: rgb(%d, %d, %d);margin: 0px;' % (
        #     randint(0, 255), randint(0, 255), randint(0, 255)))
        self.progress.setGeometry(QRect(x_progress, y_progress, width_progress, height_progress))
        self.progress_label.setGeometry(QRect(x_progress_label, y_progress_label, width_progress_label,
                                              height_progress_label))
        # self.progress_label.setStyleSheet('background: rgb(%d, %d, %d);margin: 0px;' % (
        #     randint(0, 255), randint(0, 255), randint(0, 255)))

        # 界面右侧中部
        self.widget_right_middle.setGeometry(QRect(x_right_middle, y_right_middle, width_right_middle,
                                                   height_right_middle))
        # self.widget_right_middle.setStyleSheet('background: rgb(%d, %d, %d);margin: 0px;' % (
        #          randint(0, 255), randint(0, 255), randint(0, 255)))
        self.wgt_video.setGeometry(QRect(x_video, y_video, width_video, height_video))
        self.sld_video.setGeometry(QRect(x_slide_video, y_slide_video, width_slide_video, height_slide_video))
        self.lab_video.setGeometry(QRect(x_slide_video_label, y_slide_video_label, width_slide_video_label,
                                           height_slide_video_label))
        self.widget_right_middle_down.setGeometry(x_right_middle_down, y_right_middle_down, width_right_middle_down,
                                                  height_right_middle_down)
        # self.widget_right_middle_down.setStyleSheet('background: rgb(%d, %d, %d);margin: 0px;' % (
        #     randint(0, 255), randint(0, 255), randint(0, 255)))
        self.btn_play.setGeometry(QRect(100, 0, 80, 30))
        self.sld_audio.setGeometry(QRect(300, 0, 80, 30))
        self.lab_audio.setGeometry(QRect(400, 0, 80, 30))

        # 界面右侧下部
        self.widget_right_down.setGeometry(x_right_down, y_right_down, width_right_down, height_right_down)
        # self.widget_right_down.setStyleSheet('background: rgb(%d, %d, %d);margin: 0px;' % (
        #          randint(0, 255), randint(0, 255), randint(0, 255)))
        self.horizontalLayout_right_down.setContentsMargins(0, 0, 0, 0)
        self.listWidget_right_down_left.setMaximumSize(QSize(88, 16777215))

    '''
    在界面上面的组件都加载完成之后开始继续处理视频文件，
    首先需要计算出当前的视频处理进度，主要靠视频当前处理结束的帧以及视频文件的总帧数来计算
    之后将剩余的进程都塞到进程池当中处理
    '''
    def startHandle(self):
        # 计算视频总帧数以及处理好的视频的帧数
        # 此处主要是计算num_handled和num_frame两个值
        for i in range(len(self.csv_df)):
            cur = self.csv_df.iloc[i]
            cap = cv2.VideoCapture(cur['filepath'])
            cur_frame = int(cap.get(7))
            if cur['status'] == 1:
                self.num_handled += cur_frame
            self.num_frame += cur_frame
        self.progress_label.setText(str(self.num_handled.value) + '/' + str(self.num_frame.value))

        # 以单个视频文件为粒度将所有的视频文件塞到线程池当中进行并行处理，异步操作
        df_wait = self.csv_df[self.csv_df["status"] == 0]
        len_wait = len(df_wait)
        if len_wait == 0:
            return
        if not self.executor:
            self.executor = ThreadPoolExecutor(max_workers=5)
        for i in range(len_wait):
            task = self.executor.submit(self.handleVideo, df_wait.iloc[i])
            self.task_list.append(task)

    '''
    处理每一个视频文件，主要处理办法是逐帧取图然后进行处理，
    此处为异步处理，也就是将所有的请求塞到消息队列之中
    @param:
        cur: 当前视频文件的相关信息
    '''
    def handleVideo(self, cur):
        index = cur['index']
        print('start', index)
        cap = cv2.VideoCapture(cur['filepath'])
        if cap.isOpened():
            i = 0
            while True:
                time.sleep(0.005)
                ret, img_src = cap.read()
                if not ret: 
                    break
                shape_frame = img_src.shape
                self.frameSending.emit(index, i, img_src, shape_frame[0], shape_frame[1])
                i += 1
        else:
            print('视频打开失败！')
        # 因为单帧处理变为异步操作所以在所有的帧处理请求加入到消息队列之中之后并不意味着视频文件的处理完成，在此处不需要结束响应
        # self.handleFinished.emit(cur['filepath'])
    
    def frameSending_func(self, index, i, img_src, frame_width, frame_height):
        if not self.executor_send:
            self.executor_send = ThreadPoolExecutor(max_workers=5)
        task = self.executor_send.submit(self.frameSending_func_impl, index, i, img_src, frame_width, frame_height)
        self.task_list_send.append(task)

    def frameSending_func_impl(self, index, i, img_src, frame_width, frame_height):
        print(str(index), '*', str(i), '*', str(frame_width), '*', str(frame_height))
        frame = base64.b64encode(img_src)
        self.frameSender.produce(index, i, frame, frame_width, frame_height)
        
    def frameHandleOne(self):
        self.num_handled += 1
        
    '''
    一个视频文件处理完成之后响应的槽函数，在消息队列进程当中发射该信号
    主要是完成界面上组件的更新和程序内部值的更新
        当前文件的状态
        等待列表组件
        完成列表组件
    @param:
        index: 处理结束的视频文件的编号，唯一
    '''
    def handleFinish(self, index):
        # 将当前文件的状态修改为已完成
        self.csv_df.iloc[index, 2] = 1
        self.csv_df.to_csv('file.csv')
        # 将当前的文件从wait里面去掉，首先将等待列表里面的所有组件删除
        # 再逐个添加
        for _ in range(self.listWidget_page_wait.count()):
            item = self.listWidget_page_wait.takeItem(0)
            self.listWidget_page_wait.removeItemWidget(item)
            del item
        self.load_page_wait()
        # 将当前文件添加到处理结束finish列表里面
        item = QListWidgetItem(self.listWidget_page_finish)
        item.setSizeHint(QSize(300, 80))
        item_finish = fileRecordView_finish(self.df_cur)
        item_finish.itemSelected.connect(self.finishitem_selected)
        self.listWidget_page_finish.setItemWidget(item, item_finish)
        print("finish------", index)

    '''
    加载设置界面
    '''
    def load_setting(self):
        print("开始加载设置文件：")
        with open("./config.json", 'r') as setting_file:
            self.dict_setting = json.load(setting_file)
            print(self.dict_setting)
        for i in range(len(self.list_event_py)):
            item = QListWidgetItem(self.listWidget_page_setting)
            item.setSizeHint(QSize(300, 40))
            item_setting = settingView(self.list_event_py[i], self.dict_setting[self.list_event_py[i]],
                                       self.list_event[i])
            item_setting.stateChange.connect(self.checkStateChange)
            self.listWidget_page_setting.setItemWidget(item, item_setting)
        print("设置界面加载完毕")

    '''
    加载处理完毕视频列表界面
    '''
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

    '''
    加载正在处理视频列表界面
    '''
    def load_page_wait(self):
        print("开始加载或更新等待处理的视频列表界面。。。")
        df_wait = self.csv_df[self.csv_df["status"] == 0]
        # print(df_wait)
        for i in range(len(df_wait)):
            item = QListWidgetItem(self.listWidget_page_wait)
            item.setSizeHint(QSize(300, 80))
            item_wait = fileRecordView_wait(df_wait.iloc[i])
            item_wait.itemSelected.connect(self.waititem_selected)
            self.listWidget_page_wait.setItemWidget(item, item_wait)
        print("等待处理视频列表界面加载或更新完毕。。。")

    '''
    槽函数：finish界面的文件项被选择了
    '''
    def finishitem_selected(self, index):
        # 首先清空right_down的内容
        for _ in range(self.listWidget_right_down_left.count()):
            item = self.listWidget_right_down_left.takeItem(0)
            # 删除widget
            self.listWidget_right_down_left.removeItemWidget(item)
            del item
        print(str(index) + "finish被选择了")
        curItem = self.csv_df[self.csv_df["index"] == index].iloc[0]
        # 视频加载
        pathUrl = QtCore.QUrl("file://" + curItem["filepath"])
        print(pathUrl)
        self.player.setMedia(QMediaContent(pathUrl))  # 选取视频文件
        self.player.play()  # 播放视频
        # 视频处理列表需要加载，一个视频对应一个处理文件
        self.load_right_down(index=index)

    '''
    槽函数：wait界面的文件项被选择了
    '''
    def waititem_selected(self, index):
        print(str(index) + "wait被选择了")
        curItem = self.csv_df[self.csv_df["index"] == index].iloc[0]
        # 视频加载
        pathUrl = QtCore.QUrl("file://" + curItem["filepath"])
        print(pathUrl)
        self.player.setMedia(QMediaContent(pathUrl))  # 选取视频文件
        self.player.play()  # 播放视频

    '''
    根据index的设置来加载对应的事件界面
    '''
    def load_right_down(self, index=-1):
        if index == -1:
            finish_df = self.csv_df[self.csv_df["status"] == 1]
            if len(finish_df) != 0:
                loadItem = finish_df.iloc[0]
                self.load_right_down_Byitem(loadItem)
        else:
            loadItem = self.csv_df[self.csv_df["index"] == index].iloc[0]
            self.load_right_down_Byitem(loadItem)

    '''
    根据file文件中的某一项来加载对应的事件页面
    '''
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

        self.list_happen = list_happen
        # 加载right_down_right
        self.process_path = loadItem["process_path"]
        self.filepath = loadItem["filepath"]
        if len(self.list_happen) == 0:
            return
        self.load_right_down_Byfile()

    '''
    根据事件文件的名称来加载对应的视频文件事件项
    '''
    def load_right_down_Byfile(self, event_index=0, ):
        event_df = pd.read_csv(self.process_path)
        event = self.list_happen[event_index]
        print("开始处理：", event)
        event_df_cur = event_df[event_df["type"] == event]
        self.load_page_right_down_right(event_df_cur, self.filepath)
        print("完成处理：", event)

    '''
    加载每一个事件类型的子页面  
    '''
    def load_page_right_down_right(self, event_df_cur, filepath):
        for _ in range(self.listWidget_right_down_right.count()):
            item = self.listWidget_right_down_right.takeItem(0)
            self.listWidget_right_down_right.removeItemWidget(item)
            del item
        for i in range(len(event_df_cur)):
            item = QListWidgetItem(self.listWidget_right_down_right)
            item.setSizeHint(QSize(700, 60))
            item_finish = fileEventDetailView(event_df_cur.iloc[i], filepath)
            item_finish.btn_play_clicked.connect(self.play_item)
            self.listWidget_right_down_right.setItemWidget(item, item_finish)

    '''
    槽函数：点击来视频事件列表里面的某一项   
    '''
    def play_item(self, start):
        self.player.setPosition(start)

    # 屏幕截图的功能，暂未使用
    def castVideo(self):
        screen = QGuiApplication.primaryScreen()
        cast_jpg = './' + QDateTime.currentDateTime().toString("yyyy-MM-dd hh-mm-ss-zzz") + '.jpg'
        screen.grabWindow(self.wgt_video.winId()).save(cast_jpg)

    '''
    控制音量
    '''
    def volumeChange(self, position):
        volume = round(position / self.sld_audio.maximum() * 100)
        # print("vlume %f" % volume)
        self.player.setVolume(volume)
        self.lab_audio.setText("volume:" + str(volume) + "%")

    '''
    修改音量后输出修改后的音量
    '''
    def volumeChanged(self):
        print("修改后的音量：volume %f" % self.player.volume())

    '''
    人为控制播放器进度条
    '''
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

    '''
    人为控制播放器进度条
    '''
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

    '''
    点击来视频的进度条，主要用来将人为控制视频进度和视频播放器控制进度两个信号分开
    '''
    def pressSlider(self):
        self.VIDEO_SLIDER_STATUS = True
        print("video slider pressed")

    '''
    松开点击视频进度条
    '''
    def releaseSlider(self):
        self.VIDEO_SLIDER_STATUS = False

    '''
    当没有人为控制进度条的时候使用视频播放器自动控制
    '''
    def changeSlide(self, position):
        if not self.VIDEO_SLIDER_STATUS:  # 进度条被鼠标点击时不更新
            self.vidoeLength = self.player.duration() + 0.1
            self.sld_video.setValue(round((position / self.vidoeLength) * 100))
            self.lab_video.setText("%.2f%%" % ((position / self.vidoeLength) * 100))
            if self.sld_video.value() == 100:
                self.btn_play.setText("播放")
                self.player.setPosition(0)
                self.player.pause()
    
    '''
    上传新要处理的视频文件，需要更新系统的变量以及组件
    '''
    def openVideoFile(self):
        # 上传文件响应的槽函数，这个是上传单个文件，主要是将该视频文件添加到csv_df中，
        # 当前处理视频文件的线程打开方式是一个视频文件处理完启动下一个视频文件的处理，所以需要在当前文件添加到csv_df中之后
        # 首先判断当前是否还有文件在等待处理，如果有就结束，假如没有就启动当前添加文件的处理
        filename = QFileDialog.getOpenFileNames(filter='videos: (*.mp4)')[0]
        if len(filename) == 0:
            print('没有选择任何文件')
            return
        print('选择了文件', filename)
        index = len(self.csv_df)
        record_cur = fileRecord(index, filename[0], 0, '')
        for i, cur_event in enumerate(self.list_event_py):
            if self.dict_setting[cur_event]:
                record_cur.__setattr__(cur_event, 1)
        self.csv_df = self.csv_df.append(pd.Series(record_cur.__dict__), ignore_index=True)
        self.csv_df.to_csv('file.csv')
        # 开启处理该文件
        # 将该文件的总帧数添加到整个系统中添加文件的总帧数
        df_cur = self.csv_df[self.csv_df["index"] == index].iloc[0]
        cap = cv2.VideoCapture(df_cur['filepath'])
        frame_cur = cap.get(7)
        self.num_frame += frame_cur
        # 将该文件添加到处理列表当中
        item = QListWidgetItem(self.listWidget_page_wait)
        item.setSizeHint(QSize(300, 80))
        item_wait = fileRecordView_wait(self.df_cur)
        item_wait.itemSelected.connect(self.waititem_selected)
        self.listWidget_page_wait.setItemWidget(item, item_wait)
        if not self.executor:
            self.executor = ThreadPoolExecutor(max_workers=2)
        task = self.executor.submit(self.handleVideo, df_cur)
        self.task_list.append(task)

    '''
    控制视频播放与否的按钮对应的槽函数
    '''
    def changeVideoStatus(self):
        if self.VIDEO_STATUS:
            self.player.pause()
            self.btn_play.setText("播放")
            self.VIDEO_STATUS = False
        else:
            self.player.play()
            self.btn_play.setText("暂停")
            self.VIDEO_STATUS = True

    '''
    设置界面的设置选项有所改变响应的槽函数，当设置改变之后要改变系统的变量以及相应的设置文件更新
    @param:
        choice: 对应着改变的设置选项
    '''
    def checkStateChange(self, choice):
        print(choice)
        self.dict_setting[choice] = False if self.dict_setting[choice] else True
        with open("./config.json", "w") as file_setting:
            json.dump(self.dict_setting, file_setting)
            print("设置更新完成")
            print(self.dict_setting)

    '''
    每隔一段时间之后更新一次系统进度条
    '''
    def updateProgress(self):
        # 更新整体进度值
        self.progress.setValue(int(self.num_handled.value * 100 / self.num_frame.value))
        self.progress_label.setText(str(self.num_handled.value) + '/' + str(self.num_frame.value))
        
    '''
    程序退出前线程的安全处理，需要将线程池当中为开始的线程取消掉
    然后将已经开始处理的线程结束之后再退出
    '''
    def closeHappen(self):
        print("正在结束剩余线程请等待。。。")
        # 反向序列化之前塞入的任务队列，并逐个取消
        for task in reversed(self.task_list):
            task.cancel()
        for task in reversed(self.task_list_send):
            task.cancel()
        # 等待正在执行任务执行完成
        wait(self.task_list, return_when=ALL_COMPLETED)
        wait(self.task_list_send, return_when=ALL_COMPLETED)
        print("程序退出。。。")
