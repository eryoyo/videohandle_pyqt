from PyQt5.QtCore import *
from PyQt5.QtWidgets import QSlider

class videoSlider(QSlider): 
    ClickedValue = pyqtSignal(int)
    SliderReleased = pyqtSignal()
    SliderMoved = pyqtSignal(int)
    SliderPressed = pyqtSignal()

    def __init__(self, father):
        super().__init__(Qt.Horizontal, father)

    def mousePressEvent(self, QMouseEvent):     #单击事件
        super().mousePressEvent(QMouseEvent)
        value = QMouseEvent.localPos().x()
        # self.setValue(int(value)/9)
        value = round(value/self.width()*self.maximum())  # 根据鼠标点击的位置和slider的长度算出百分比
        self.ClickedValue.emit(value)
    
    def sliderReleased(self) -> None:
        self.SliderReleased.emit()
        
    def sliderMoved(self, position: int) -> None:
        self.SliderMoved.emit(position)
        
    def sliderPressed(self) -> None:
        self.SliderPressed.emit()
