import json
from random import randint

import cv2
import pandas as pd

from PyQt5.QtCore import QRect, Qt, QSize, QUrl
from PyQt5.QtGui import QPalette, QColor, QBrush, QResizeEvent, QPixmap, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QListWidget, \
    QStackedWidget, QProgressBar, QLabel, QPushButton, QSlider, QApplication, QListWidgetItem, QFileDialog

from fileEventDetailView import fileEventDetailView
from fileRecord import fileRecord
from fileRecordView_finish import fileRecordView_finish
from fileRecordView_wait import fileRecordView_wait
from settingView import settingView
from threadDemo import threadDemo
from videoSlider import videoSlider


class PlainWindow(QWidget):
    def __init__(self):
        super(PlainWindow, self).__init__()

        # 变量
        # 控制播放与否的状态变量，False表示处于暂停状态，选中某一个视频之后默认就开始播放
        self.VIDEO_STATUS = True
        # 控制播放器进度条是否被点击，也就是当前视频进度正在受到人为调整
        self.VIDEO_SLIDER_STATUS = False

        self.choice = ["处理完成", "处理中", "上传文件", "设置"]
        self.icon = QIcon()
        self.icon.addPixmap(QPixmap("img/Icon.png"), QIcon.Normal, QIcon.Off)
        with open("./config.json", 'r') as setting_file:
            self.dict_setting = json.load(setting_file)
            print(self.dict_setting)

        # 文件列表
        self.csv_df = pd.read_csv("./file.csv", index_col=0)
        # 事件列表
        self.list_event_py = ["taibiao_1", "taibiao_2", "taibiao_3", "taibiao_4", "taibiao_5", "taibiao_6",
                              "taibiao_7", "taibiao_8", "taibiao_9", "taibiao_10", "taibiao_11", "taibiao_12",
                              "taibiao_13", "taibiao_14", "taibiao_15", "taibiao_16", "ttv", "voa", "xtr",
                              "zhuangjia", "daoju", "qiangzhi", "smoke"]
        self.list_event = ["台标1", "台标2", "台标3", "台标4", "台标5", "台标6", "台标7", "台标8", "台标9", "台标10", "台标11",
                           "台标12", "台标13", "台标14", "台标15", "台标16", "ttv", "voa", "xtr", "装甲", "刀具", "枪支", "吸烟"]
        self.df_cur = -1
        # 总帧数
        self.num_frame = 0
        # 处理好的视频的帧数之和
        self.num_handled = 0
        # 当前处理的视频的总帧数
        self.num_frame_cur = 0
        # 当前处理的视频的处理好的帧数
        self.num_handled_cur = 0
        
        # 组件注册
        self.setWindowTitle("视频内容检测系统")
        self.setObjectName("MainWindow")
        self.setGeometry(QRect(0, 0, 1200, 906))
        
        # 左侧窗口
        self.widget_left = QWidget(self)
        
        self.horizontalLayout_left = QHBoxLayout(self.widget_left)
        self.listView_left_left = QListWidget(self.widget_left)
        self.stackedWidget_left_right = QStackedWidget(self.widget_left)
        self.page_finish = QListWidget(self.stackedWidget_left_right)
        self.page_wait = QListWidget(self.stackedWidget_left_right)
        self.page_upload = QWidget(self.stackedWidget_left_right)
        self.button_open = QPushButton(self.page_upload)
        self.page_setting = QListWidget(self.stackedWidget_left_right)
        self.stackedWidget_left_right.addWidget(self.page_finish)
        self.stackedWidget_left_right.addWidget(self.page_wait)
        self.stackedWidget_left_right.addWidget(self.page_upload)
        self.stackedWidget_left_right.addWidget(self.page_setting)
        self.horizontalLayout_left.addWidget(self.listView_left_left)
        self.horizontalLayout_left.addWidget(self.stackedWidget_left_right)
        
        # 右
        self.widget_right = QWidget(self)
        
        # 界面右侧上部
        self.widget_right_up = QWidget(self.widget_right)
        self.progress = QProgressBar(self.widget_right_up)
        self.progress_label = QLabel(self.widget_right_up)
        
        # 界面右侧中部
        self.widget_right_middle = QWidget(self.widget_right)
        self.player = QMediaPlayer()
        self.widget_video = QVideoWidget(self.widget_right_middle)
        self.slide_video = videoSlider(self.widget_right_middle)
        self.label_video = QLabel(self.widget_right_middle)
        self.widget_right_middle_down = QWidget(self.widget_right_middle)
        self.button_play = QPushButton(self.widget_right_middle_down)
        self.slide_audio = QSlider(self.widget_right_middle_down)
        self.label_audio = QLabel(self.widget_right_middle_down)
        
        # 界面右侧下部
        self.widget_right_down = QWidget(self.widget_right)
        self.horizontalLayout_right_down = QHBoxLayout(self.widget_right_down)
        self.listWidget_right_down_left = QListWidget(self.widget_right_down)
        self.listWidget_right_down_right = QListWidget(self.widget_right_down)
        self.horizontalLayout_right_down.addWidget(self.listWidget_right_down_left)
        self.horizontalLayout_right_down.addWidget(self.listWidget_right_down_right)
        
        self.setVideoStyle()
        self.setGeometryAll(1200, 900)
        self.setContent()
        self.setObjectNameAll()
        self.setAction()
        self.startHandle()
        
    def setVideoStyle(self):
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        self.widget_video.setPalette(palette)
        self.widget_video.setAutoFillBackground(True)
        
    def setObjectNameAll(self):
        # 左
        self.widget_left.setObjectName("widget_left")
        self.horizontalLayout_left.setObjectName("horizontalLayout_left")
        self.listView_left_left.setObjectName("listView_left_left")
        self.stackedWidget_left_right.setObjectName("stackedWidget_left_right")
        self.page_finish.setObjectName("page_finish")
        self.page_wait.setObjectName("page_wait")
        self.page_upload.setObjectName("page_upload")
        self.button_open.setObjectName("button_open")
        self.page_setting.setObjectName("page_setting")

        # 右
        self.widget_right.setObjectName("widget_right")

        # 界面右侧上部
        self.widget_right_up.setObjectName("widget_right_up")
        self.progress.setObjectName("progress")
        self.progress_label.setObjectName("progress_label")

        # 界面右侧中部
        self.widget_right_middle.setObjectName("widget_right_middle")
        self.widget_video.setObjectName("widget_video")
        self.slide_video.setObjectName("slide_video")
        self.label_video.setObjectName("label_video")
        self.widget_right_middle_down.setObjectName("widget_right_middle_down")
        self.button_play.setObjectName("button_play")
        self.slide_audio.setObjectName("slide_audio")
        self.label_audio.setObjectName("label_audio")

        # 界面右侧下部
        self.widget_right_down.setObjectName("widget_right_down")
        self.horizontalLayout_right_down.setObjectName("horizontalLayout_right_down")
        self.listWidget_right_down_left.setObjectName("listWidget_right_down_left")
        self.listWidget_right_down_right.setObjectName("listWidget_right_down_right")
        
    def setGeometryAll(self, width, height):
        # 左
        self.widget_left.setGeometry(QRect(0, 0, 401, height))
        self.horizontalLayout_left.setContentsMargins(0, 0, 0, 0)
        self.listView_left_left.setMaximumSize(QSize(88, 16777215))
        self.page_finish.setGeometry(QRect(0, 0, 303, height))
        self.page_wait.setGeometry(QRect(0, 0, 303, height))
        self.page_upload.setGeometry(QRect(0, 0, 303, height))
        self.button_open.setGeometry(QRect(25, 25, 200, 60))
        self.page_setting.setGeometry(QRect(0, 0, 303, height))
        
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
        self.widget_right.setGeometry(QRect(401, 0, width_right, 16777215))

        # 界面右侧上部
        self.widget_right_up.setGeometry(QRect(0, 0, width_right, height_right_up))
        self.widget_right_up.setStyleSheet('background: rgb(%d, %d, %d);margin: 0px;' % (
                 randint(0, 255), randint(0, 255), randint(0, 255)))
        self.progress.setGeometry(QRect(x_progress, y_progress, width_progress, height_progress))
        self.progress_label.setGeometry(QRect(x_progress_label, y_progress_label, width_progress_label, 
                                              height_progress_label))
        self.progress_label.setStyleSheet('background: rgb(%d, %d, %d);margin: 0px;' % (
                 randint(0, 255), randint(0, 255), randint(0, 255)))

        # 界面右侧中部
        self.widget_right_middle.setGeometry(QRect(x_right_middle, y_right_middle, width_right_middle, 
                                                   height_right_middle))
        # self.widget_right_middle.setStyleSheet('background: rgb(%d, %d, %d);margin: 0px;' % (
        #          randint(0, 255), randint(0, 255), randint(0, 255)))
        self.widget_video.setGeometry(QRect(x_video, y_video, width_video, height_video))
        self.slide_video.setGeometry(QRect(x_slide_video, y_slide_video, width_slide_video, height_slide_video))
        self.label_video.setGeometry(QRect(x_slide_video_label, y_slide_video_label, width_slide_video_label, 
                                           height_slide_video_label))
        self.widget_right_middle_down.setGeometry(x_right_middle_down, y_right_middle_down, width_right_middle_down, 
                                                  height_right_middle_down)
        self.widget_right_middle_down.setStyleSheet('background: rgb(%d, %d, %d);margin: 0px;' % (
                 randint(0, 255), randint(0, 255), randint(0, 255)))
        self.button_play.setGeometry(QRect(100, 0, 80, 30))
        self.slide_audio.setGeometry(QRect(300, 0, 80, 30))
        self.label_audio.setGeometry(QRect(400, 0, 80, 30))

        # 界面右侧下部
        self.widget_right_down.setGeometry(x_right_down, y_right_down, width_right_down, height_right_down)
        # self.widget_right_down.setStyleSheet('background: rgb(%d, %d, %d);margin: 0px;' % (
        #          randint(0, 255), randint(0, 255), randint(0, 255)))
        self.horizontalLayout_right_down.setContentsMargins(0, 0, 0, 0)
        self.listWidget_right_down_left.setMaximumSize(QSize(88, 16777215))
        
    def setContent(self):
        # 左侧目录
        for i in range(len(self.choice)):
            item = QListWidgetItem(self.icon, self.choice[i], self.listView_left_left)
            # 设置item的默认宽高(这里只有高度比较有用)
            item.setSizeHint(QSize(86, 60))
            # 文字居中
            item.setTextAlignment(Qt.AlignCenter)
        # 左侧目录详情
        # self.load_page_finish()
        # self.load_page_wait()
        self.button_open.setText("上传视频文件")
        self.load_setting()
        self.progress.setValue(0)
        self.slide_video.setMaximum(100)
        self.label_video.setText("0%")
        self.player.setVideoOutput(self.widget_video)  # 视频播放输出的widget，就是上面定义的
        self.button_play.setText("暂停⏸️")
        self.slide_audio.setOrientation(Qt.Horizontal)
        self.slide_audio.setProperty("value", 99)
        self.label_audio.setText("音量：100%")
        
    def setAction(self):
        # 控制视频相关
        self.button_open.clicked.connect(self.openVideoFile)  # 打开视频文件按钮
        self.button_play.clicked.connect(self.changeVideoStatus)  # play
        self.player.positionChanged.connect(self.changeSlide)  # change Slide
        self.slide_video.setTracking(False)
        self.slide_video.SliderReleased.connect(self.releaseSlider)
        self.slide_video.SliderPressed.connect(self.pressSlider)
        self.slide_video.SliderMoved.connect(self.moveSlider)  # 进度条拖拽跳转
        self.slide_video.ClickedValue.connect(self.clickedSlider)  # 进度条点击跳转
        self.slide_audio.valueChanged.connect(self.volumeChange)  # 控制声音播放
        self.slide_audio.sliderReleased.connect(self.volumeChanged)  # 打印修改后的音量

        # 控制进度条的源头
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.updateProgress)
        # self.timer.start(randint(1, 3) * 1000)

        # 控制转换页面
        self.listView_left_left.currentRowChanged.connect(
            lambda cur: self.stackedWidget_left_right.setCurrentIndex(cur))
        self.listWidget_right_down_left.currentRowChanged.connect(self.load_right_down_Byfile)

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
        # self._thread.finished.connect(self.threadFinish)
        self._thread.valueChanged.connect(self.updateProgress)
        self._thread.start()  # 启动线程

    # 加载处理完毕视频列表界面
    def load_page_finish(self):
        print("开始加载处理完毕的视频列表界面。。。")
        df_finish = self.csv_df[self.csv_df["status"] == 1]
        for i in range(len(df_finish)):
            item = QListWidgetItem(self.page_finish)
            item.setSizeHint(QSize(300, 80))
            item_finish = fileRecordView_finish(df_finish.iloc[i])
            item_finish.itemSelected.connect(self.finishitem_selected)
            self.page_finish.setItemWidget(item, item_finish)
        print("处理完毕视频列表界面加载完毕。。。")

    # 加载正在处理视频列表界面
    def load_page_wait(self):
        print("开始加载等待处理的视频列表界面。。。")
        df_wait = self.csv_df[self.csv_df["status"] == 0]
        for i in range(len(df_wait)):
            item = QListWidgetItem(self.page_wait)
            item.setSizeHint(QSize(300, 80))
            item_wait = fileRecordView_wait(df_wait.iloc[i])
            item_wait.itemSelected.connect(self.waititem_selected)
            self.page_wait.setItemWidget(item, item_wait)
        print("等待处理视频列表界面加载完毕。。。")

    # 加载设置界面
    def load_setting(self):
        print("开始加载设置界面：")
        for i in range(len(self.list_event_py)):
            item = QListWidgetItem(self.page_setting)
            item.setSizeHint(QSize(300, 40))
            item_setting = settingView(self.list_event_py[i], self.dict_setting[self.list_event_py[i]],
                                       self.list_event[i])
            item_setting.stateChange.connect(self.checkStateChange)
            self.page_setting.setItemWidget(item, item_setting)
        print("设置界面加载完毕")
        
    # 窗口大小自适应槽函数
    def resizeEvent(self, a0: QResizeEvent) -> None:
        size = a0.size()
        self.setGeometryAll(size.width(), size.height())

    # 槽函数：finish界面的文件项被选择了
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
        pathUrl = QUrl("file://" + curItem["filepath"])
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
        pathUrl = QUrl("file://" + curItem["filepath"])
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

        self.list_happen = list_happen
        # 加载right_down_right
        self.process_path = loadItem["process_path"]
        self.filepath = loadItem["filepath"]
        if len(self.list_happen) == 0:
            return
        self.load_right_down_Byfile()

    # 根据事件文件的名称来加载对应的视频文件事件项
    def load_right_down_Byfile(self, event_index=0):
        event_df = pd.read_csv(self.process_path, index_col=0)
        event = self.list_happen[event_index]
        print("开始处理：", event)
        event_df_cur = event_df[event_df["type"] == event]
        self.load_page_right_down_right(event_df_cur, self.filepath)
        print("完成处理：", event)

    # 加载每一个事件类型的子页面    
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

    # 槽函数：点击来视频事件列表里面的某一项        
    def play_item(self, start):
        self.player.setPosition(start)

    # 屏幕截图的功能，暂未使用
    def castVideo(self):
        ...
        # screen = QGuiApplication.primaryScreen()
        # cast_jpg = './' + QDateTime.currentDateTime().toString("yyyy-MM-dd hh-mm-ss-zzz") + '.jpg'
        # screen.grabWindow(self.wgt_video.winId()).save(cast_jpg)

    # 控制音量
    def volumeChange(self, position):
        volume = round(position / self.slide_audio.maximum() * 100)
        # print("vlume %f" % volume)
        self.player.setVolume(volume)
        self.label_audio.setText("volume:" + str(volume) + "%")

    # 修改音量后输出修改后的音量
    def volumeChanged(self):
        print("修改后的音量：volume %f" % self.player.volume())

    # 人为控制播放器进度条
    def clickedSlider(self, position):
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            self.label_video.setText("%.2f%%" % position)
            if self.slide_video.value() == 100:
                self.button_play.setText("播放")
                self.player.setPosition(0)
                self.player.pause()
        else:
            self.slide_video.setValue(0)

    # 人为控制播放器进度条
    def moveSlider(self, position):
        self.VIDEO_SLIDER_STATUS = True
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            self.label_video.setText("%.2f%%" % position)
            if self.slide_video.value() == 100:
                self.button_play.setText("播放")
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
            self.slide_video.setValue(round((position / self.vidoeLength) * 100))
            self.label_video.setText("%.2f%%" % ((position / self.vidoeLength) * 100))
            if self.slide_video.value() == 100:
                self.button_play.setText("播放")
                self.player.setPosition(0.1)
                self.player.pause()

    def openVideoFile(self):
        temp = QFileDialog.getOpenFileUrl()[0]
        temp = temp.toString()[7:]
        print(temp)
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.widget_video)  # 视频播放输出的widget，就是上面定义的
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(temp)))  # 选取视频文件
        self.player.play()  # 播放视频
        print("availableMetaData: " + str(self.player.availableMetaData()))
        # 上传文件响应的槽函数，这个是上传单个文件，主要是将该视频文件添加到csv_df中，
        # 当前处理视频文件的线程打开方式是一个视频文件处理完启动下一个视频文件的处理，所以需要在当前文件添加到csv_df中之后
        # 首先判断当前是否还有文件在等待处理，如果有就结束，假如没有就启动当前添加文件的处理
        # filename = QFileDialog.getOpenFileNames(filter='videos: (*.mp4)')[0]
        # if len(filename) == 0:
        #     print('没有选择任何文件')
        #     return
        # print('选择了文件', filename)
        # df_wait = self.csv_df[self.csv_df["status"] == 0]
        # len_handled = len(df_wait)
        # index = len(self.csv_df)
        # record_cur = fileRecord(index, filename[0], 0, '')
        # for i, cur_event in enumerate(self.list_event_py):
        #     if self.dict_setting[cur_event]:
        #         record_cur.__setattr__(cur_event, 1)
        # self.csv_df = self.csv_df.append(pd.Series(record_cur.__dict__), ignore_index=True)
        # self.csv_df.to_csv('file.csv')
        # # 开启处理该文件
        # # 将该文件的总帧数添加到整个系统中添加文件的总帧数
        # self.df_cur = self.csv_df[self.csv_df["index"] == index].iloc[0]
        # cap = cv2.VideoCapture(self.df_cur['filepath'])
        # frame_cur = cap.get(7)
        # self.num_frame += frame_cur
        # # 将该文件添加到处理列表当中
        # item = QListWidgetItem(self.page_wait)
        # item.setSizeHint(QSize(300, 80))
        # item_wait = fileRecordView_wait(self.df_cur)
        # item_wait.itemSelected.connect(self.waititem_selected)
        # self.page_wait.setItemWidget(item, item_wait)
        # if len_handled == 0:
        #     self.num_frame_cur = frame_cur
        #     self._thread = threadDemo(self.df_cur)
        #     self._thread.finished.connect(self.threadFinish)
        #     self._thread.valueChanged.connect(self.updateProgress)
        #     self._thread.start()  # 启动线程

    # 控制视频播放与否的按钮
    def changeVideoStatus(self):
        if self.VIDEO_STATUS:
            self.player.pause()
            self.button_play.setText("播放")
            self.VIDEO_STATUS = False
        else:
            self.player.play()
            self.button_play.setText("暂停")
            self.VIDEO_STATUS = True

    # 设置选项改变
    def checkStateChange(self, choice):
        print(choice)
        self.dict_setting[choice] = False if self.dict_setting[choice] else True
        with open("./config.json", "w") as file_setting:
            json.dump(self.dict_setting, file_setting)
            print("设置更新完成")
            print(self.dict_setting)

    # 槽函数：根据处理视频的子线程发出的信号来更新一次系统进度条和当前的进度条
    def updateProgress(self, i):
        self.num_handled_cur = i + 1
        # 更新整体进度值
        self.progress.setValue(int((self.num_handled_cur + self.num_handled) * 100 / self.num_frame))
        self.progress_label.setText(str(self.num_handled + self.num_handled_cur) + '/' + str(self.num_frame))
        # self.listWidget_page_wait.takeItem(0)..progress_wait.setValue(100 * self.num_handled_cur / self.num_frame_cur)

    # 一个视频处理结束之后产生的信号
    def threadFinish(self):
        self._thread.deleteLater()
        self.num_handled += self.num_frame_cur
        self.num_handled_cur = 0
        self.num_frame_cur = 0
        # 将当前文件的状态修改为已完成
        index = self.df_cur['index']
        self.csv_df.iloc[index, 2] = 1
        self.csv_df.to_csv('file.csv')
        # 将当前的文件从wait里面去掉
        item = self.page_wait.takeItem(0)
        self.page_wait.removeItemWidget(item)
        # 将当前文件添加到处理结束finish列表里面
        item = QListWidgetItem(self.page_finish)
        item.setSizeHint(QSize(300, 80))
        item_finish = fileRecordView_finish(self.df_cur)
        item_finish.itemSelected.connect(self.finishitem_selected)
        self.page_finish.setItemWidget(item, item_finish)

        # 选择一个新的视频进行处理
        df_wait = self.csv_df[self.csv_df["status"] == 0]
        if len(df_wait) == 0:
            return
        self.df_cur = df_wait.iloc[0]
        cap = cv2.VideoCapture(self.df_cur['filepath'])
        self.num_frame_cur = cap.get(7)
        self._thread = threadDemo(self.df_cur)
        self._thread.finished.connect(self.threadFinish)
        self._thread.valueChanged.connect(self.updateProgress)
        self._thread.start()  # 启动线程

    # 利用子线程来处理视频，在过程中需要实时改变系统进度条的值，也就是当前已处理完的帧
    def handleVideo(self):
        pass


if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    app.setStyleSheet(open('./style.qss', 'rb').read().decode('utf-8'))
    w = PlainWindow()
    w.show()
    sys.exit(app.exec_())
