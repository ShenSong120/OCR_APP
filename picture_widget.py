import os
import cv2
import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from global_var import *


# 照片控件
class PictureWidget(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent, picture_path):
        super(PictureWidget, self).__init__(parent)
        # 设置样式
        style = 'font-family: Times New Roman;\
                 font-size: 13pt;\
                 QFileDialog {background-color: beige;}'
        self.setStyleSheet(style)
        self.parent = parent
        self.picture_path = picture_path
        # 图片尺寸
        self.picture_size_width = None
        self.picture_size_height = None
        # 默认原尺寸播放图片
        self.picture_zoom_scale = 1.0
        # 默认的缩放增减倍数(每次增减在上一次基础上增减0.2倍)
        self.zoom_factor = 0.2
        self.init_ui()
        self.show_picture()

    def init_ui(self):
        self.general_layout = QVBoxLayout(self)
        self.general_layout.setSpacing(0)
        self.general_layout.setContentsMargins(0, 3, 0, 0)
        self.picture_h_layout = QHBoxLayout(self)
        self.button_h_layout = QHBoxLayout(self)
        self.button_h_layout.setContentsMargins(0, 0, 0, 0)
        # 打开文件按钮
        self.open_file_button = QToolButton()
        # 打开文件快捷键
        self.open_file_button.setShortcut('o')
        self.open_file_button.setEnabled(False)
        self.open_file_button.setToolTip('打开文件(o)')
        self.open_file_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.open_picture + ')}')
        self.open_file_button.clicked.connect(self.connect_open_file)
        # 放大按钮
        self.zoom_button = QToolButton()
        self.zoom_button.setEnabled(False)
        self.zoom_button.setToolTip('放大')
        self.zoom_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.zoom_picture + ')}')
        self.zoom_button.clicked.connect(self.connect_zoom_button)
        # 原图按钮
        self.original_size_button = QToolButton()
        self.original_size_button.setEnabled(False)
        self.original_size_button.setToolTip('恢复原尺寸')
        self.original_size_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.original_size_picture + ')}')
        self.original_size_button.clicked.connect(self.connect_original_size_button)
        # 缩小按钮
        self.zoom_out_button = QToolButton()
        self.zoom_out_button.setEnabled(False)
        self.zoom_out_button.setToolTip('缩小')
        self.zoom_out_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.zoom_out_picture + ')}')
        self.zoom_out_button.clicked.connect(self.connect_zoom_out_button)
        # 截图操作
        self.screen_shot_button = QToolButton()
        self.screen_shot_button.setEnabled(False)
        self.screen_shot_button.setToolTip('截图')
        self.screen_shot_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.screen_shot + ')}')
        self.screen_shot_button.clicked.connect(self.connect_screen_shot)
        # 显示图片路径
        self.picture_path_label = QLabel(self)
        self.picture_path_label.setText('None')
        # 显示照片尺寸
        self.picture_size_label = QLabel(self)
        self.picture_size_label.setText('size: [0:0], zoom: [1.0X]')

        self.button_h_layout.addSpacing(5)
        self.button_h_layout.addWidget(self.open_file_button)
        self.button_h_layout.addSpacing(5)
        self.button_h_layout.addWidget(self.zoom_button)
        self.button_h_layout.addSpacing(5)
        self.button_h_layout.addWidget(self.original_size_button)
        self.button_h_layout.addSpacing(5)
        self.button_h_layout.addWidget(self.zoom_out_button)
        self.button_h_layout.addSpacing(5)
        self.button_h_layout.addWidget(self.screen_shot_button)
        self.button_h_layout.addStretch(1)
        self.button_h_layout.addWidget(self.picture_path_label)
        self.button_h_layout.addStretch(1)
        self.button_h_layout.addWidget(self.picture_size_label)

        # 填充图片标签
        self.picture_label = QLabel(self)
        self.picture_label.setScaledContents(True)

        # 创建一个滚动区域
        self.picture_scroll_area = QScrollArea()
        self.picture_scroll_area.setWidget(self.picture_label)

        self.picture_h_layout.addWidget(self.picture_scroll_area)

        self.general_layout.addLayout(self.button_h_layout)
        self.general_layout.addSpacing(2)
        self.general_layout.addLayout(self.picture_h_layout)

        self.setLayout(self.general_layout)

    # 打开文件(图片)
    def connect_open_file(self):
        file_path = Profile.get_config_value(file=GloVar.config_file_path, section='param', option='file_path')
        # 文件过滤
        file_filter = 'jpg(*.jpg);;png(*.png);;jpeg(*.jpeg);;bmp(*.bmp)'
        # 返回元祖(第一个元素文件路径, 第二个元素文件类型), 这里只需要第一个文件路径
        picture_path = QFileDialog.getOpenFileName(self, '选择需要打开的文件', file_path, file_filter)[0]
        if picture_path:
            print('打开文件: %s' % picture_path)
            # 展示照片
            self.picture_path = picture_path
            self.show_picture()
            current_file_path = os.path.split(picture_path)[0]
            # 将当前picture_path路径保存到配置文件
            if file_path != current_file_path:
                Profile.set_config_value(file=GloVar.config_file_path, section='param', option='file_path',
                                         value=current_file_path)
        else:
            print('取消打开文件!')

    # 放大操作
    def connect_zoom_button(self):
        current_zoom_scale = round((self.picture_zoom_scale + self.zoom_factor), 1)
        width = int(self.picture_size_width * current_zoom_scale)
        height = int(self.picture_size_height * current_zoom_scale)
        # 不用判断(可以无限放大)
        self.picture_zoom_scale = current_zoom_scale
        self.picture_label.setFixedSize(width, height)
        self.picture_size_label.setText('size: [%d:%d], zoom: [%.1fX]' % (self.picture_size_width,
                                                                          self.picture_size_height,
                                                                          self.picture_zoom_scale))

    # 缩小操作
    def connect_zoom_out_button(self):
        current_zoom_scale = round((self.picture_zoom_scale - self.zoom_factor), 1)
        width = int(self.picture_size_width * current_zoom_scale)
        height = int(self.picture_size_height * current_zoom_scale)
        # 需要判断(不能小于0)
        if current_zoom_scale > 0.0:
            self.picture_zoom_scale = current_zoom_scale
            self.picture_label.setFixedSize(width, height)
            self.picture_size_label.setText('size: [%d:%d], zoom: [%.1fX]' % (self.picture_size_width,
                                                                              self.picture_size_height,
                                                                              self.picture_zoom_scale))

    # 截图操作
    def connect_screen_shot(self):
        pass

    # 原图操作
    def connect_original_size_button(self):
        self.picture_zoom_scale = 1.0
        self.picture_label.setFixedSize(self.picture_size_width, self.picture_size_height)
        self.picture_size_label.setText('size: [%d:%d], zoom: [1.0X]' % (self.picture_size_width,
                                                                         self.picture_size_height))

    # 图片展示操作
    def show_picture(self):
        self.zoom_button.setEnabled(True)
        self.zoom_out_button.setEnabled(True)
        self.original_size_button.setEnabled(True)
        image = cv2.imdecode(np.fromfile(self.picture_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        size = image.shape
        self.picture_size_width = int(size[1])
        self.picture_size_height = int(size[0])
        # widget居中显示
        self.picture_scroll_area.setAlignment(Qt.AlignCenter)
        # # 通过判断图片尺寸来确认图片放置位置
        # if self.picture_size_width < self.picture_scroll_area.width() and self.picture_size_height < self.picture_scroll_area.height():
        #     # widget居中显示
        #     self.picture_scroll_area.setAlignment(Qt.AlignCenter)
        # elif self.picture_size_width < self.picture_scroll_area.width() and self.picture_size_height >= self.picture_scroll_area.height():
        #     # 居中靠上
        #     self.picture_scroll_area.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        # elif self.picture_size_width >= self.picture_scroll_area.width() and self.picture_size_height < self.picture_scroll_area.height():
        #     # 居中中靠左
        #     self.picture_scroll_area.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        # elif self.picture_size_width >= self.picture_scroll_area.width() and self.picture_size_height >= self.picture_scroll_area.height():
        #     # 居上靠左
        #     self.picture_scroll_area.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.picture_label.setFixedSize(self.picture_size_width, self.picture_size_height)
        self.picture_label.setPixmap(QPixmap(self.picture_path))
        self.picture_path_label.setText(str(self.picture_path))
        self.picture_size_label.setText('size: [%d:%d], zoom: [1.0X]' % (self.picture_size_width, self.picture_size_height))
        self.picture_zoom_scale = 1.0

    def resizeEvent(self, event):
        self.signal.emit('resize>')


if __name__ == '__main__':
    picture = 'D:/Code/robot/picture/screen_shot/2020-04-08-14-42-34.jpg'
    app = QApplication(sys.argv)
    win = PictureWidget(None, picture_path=picture)
    win.show()
    sys.exit(app.exec_())
