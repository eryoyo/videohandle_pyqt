from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QResizeEvent, QCloseEvent
from PyQt5.QtWidgets import QMainWindow

'''
显示用的主要窗口
'''
class UMainWindow(QMainWindow):
    sizeChanged = pyqtSignal(int, int)  # 值变化信号
    closeHappen = pyqtSignal()
    
    def __init__(self):
        super(UMainWindow, self).__init__()
        
    '''
    重写的resizeEvent方法，以便窗口大小自适应
    @params:a0其中有size和oldsize
    '''
    def resizeEvent(self, a0: QResizeEvent) -> None:
        super(UMainWindow, self).resizeEvent(a0)
        size = a0.size()
        self.sizeChanged.emit(size.width(), size.height())
        
    '''
    窗口关闭时响应的槽函数
    '''
    def closeEvent(self, a0: QCloseEvent) -> None:
        super(UMainWindow, self).closeEvent(a0)
        self.closeHappen.emit()
        
