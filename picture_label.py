from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class PictureLabel(QLabel):
    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(PictureLabel, self).__init__(parent)
        self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0
        self.mouse_press_flag = False
        self.mouse_move_flag = False
        self.box_flag = False

    # 鼠标点击事件
    def mousePressEvent(self, event):
        self.mouse_press_flag = True
        self.x0 = event.x()
        self.y0 = event.y()
        self.x1 = self.x0
        self.y1 = self.y0

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        self.mouse_press_flag = False
        self.mouse_move_flag = False
        if self.box_flag is True:
            self.signal.emit('screen_shot>' + str([self.x0, self.y0, self.x1, self.y1]))

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        if self.mouse_press_flag is True:
            self.mouse_move_flag = True
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()

    # 绘制事件
    def paintEvent(self, event):
        super().paintEvent(event)
        # 框选动作
        if self.mouse_move_flag is True and self.box_flag is True:
            rect = QRect(self.x0, self.y0, abs(self.x1 - self.x0), abs(self.y1 - self.y0))
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.drawRect(rect)
        # 其余情况(不绘制图, 一个小点,几乎不能看到)
        else:
            point = [QPoint(self.x0, self.y0)]
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
            painter.drawPoints(QPolygon(point))

    # 保存模板
    def save_template(self):
        pass
        # cv2.imencode('.bmp', cut_img)[1].tofile(template_name)
