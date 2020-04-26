import os
import cv2
import sys
import numpy as np
import numpy.core._dtype_ctypes  # 打包需要用到
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from picture_label import PictureLabel
from global_var import *
from file_save_dialog import SaveFile


# 照片控件
class PictureWidget(QWidget):

    signal = pyqtSignal(str)

    def __init__(self, parent):
        super(PictureWidget, self).__init__(parent)
        # 设置初始位置和大小
        self.setGeometry(150, 50, 1000, 700)
        # 设置样式
        style = 'font-family: Times New Roman;\
                 font-size: 13pt;\
                 QFileDialog {background-color: beige;}'
        self.setStyleSheet(style)
        self.parent = parent
        # 配置文件读取picture默认路径
        picture = Profile.get_config_value(file=GloVar.config_file_path, section='param', option='picture')
        if os.path.exists(picture):
            self.picture_path = picture
        else:
            self.picture_path = None
        # 当前图片(非路径, 可以直接保存)
        self.image = None
        # 截图位置信息
        self.position = [0, 0, 0, 0]
        # 图片尺寸
        self.picture_size_width = None
        self.picture_size_height = None
        # 默认原尺寸播放图片
        self.picture_zoom_scale = 1.0
        # 默认的缩放增减倍数(每次增减在上一次基础上增减0.2倍)
        self.zoom_factor = 0.1
        # 可以打开的文件类型
        self.file_type_list = ['jpg', 'png', 'jpeg', 'bmp']
        # 悬浮窗最小高度
        self.float_frame_height = 60
        self.init_ui()
        # self.show_picture()

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
        self.open_file_button.setToolTip('打开文件(o)')
        self.open_file_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.open_picture + ')}')
        self.open_file_button.clicked.connect(self.connect_open_file)
        # 放大按钮
        self.zoom_button = QToolButton()
        self.zoom_button.setEnabled(False)
        self.zoom_button.setToolTip('图片放大')
        self.zoom_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.zoom_picture + ')}')
        self.zoom_button.clicked.connect(self.connect_zoom_button)
        # 原图按钮
        self.original_size_button = QToolButton()
        self.original_size_button.setEnabled(False)
        self.original_size_button.setToolTip('1:1视图')
        self.original_size_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.original_size_picture + ')}')
        self.original_size_button.clicked.connect(self.connect_original_size_button)
        # 合适尺寸按钮
        self.suitable_size_button = QToolButton()
        self.suitable_size_button.setEnabled(False)
        self.suitable_size_button.setToolTip('适应窗口')
        self.suitable_size_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.suitable_size + ')}')
        self.suitable_size_button.clicked.connect(self.connect_suitable_size_button)
        # 缩小按钮
        self.zoom_out_button = QToolButton()
        self.zoom_out_button.setEnabled(False)
        self.zoom_out_button.setToolTip('图片缩小')
        self.zoom_out_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.zoom_out_picture + ')}')
        self.zoom_out_button.clicked.connect(self.connect_zoom_out_button)
        # 截图操作
        self.screen_shot_button = QToolButton()
        self.screen_shot_button.setToolTip('截取图片')
        self.screen_shot_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.screen_shot + ')}')
        self.screen_shot_button.clicked.connect(self.connect_screen_shot)
        # 上一张图片
        self.last_picture_button = QToolButton()
        self.last_picture_button.setMinimumSize(QSize(50, 50))
        self.last_picture_button.setShortcut('left')
        self.last_picture_button.setEnabled(False)
        self.last_picture_button.setToolTip('上一张图片')
        self.last_picture_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.last_picture + ')}')
        self.last_picture_button.clicked.connect(self.connect_show_last_picture)
        # 下一张图片
        self.next_picture_button = QToolButton()
        self.next_picture_button.setMinimumSize(QSize(50, 50))
        self.next_picture_button.setShortcut('right')
        self.next_picture_button.setEnabled(False)
        self.next_picture_button.setToolTip('上一张图片')
        self.next_picture_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.next_picture + ')}')
        self.next_picture_button.clicked.connect(self.connect_show_next_picture)
        # 向左旋转
        self.turn_left_button = QToolButton()
        self.turn_left_button.setMinimumSize(QSize(50, 50))
        self.turn_left_button.setEnabled(False)
        self.turn_left_button.setToolTip('左转90度')
        self.turn_left_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.left_picture + ')}')
        self.turn_left_button.clicked.connect(self.connect_turn_left_picture)
        # 向右旋转
        self.turn_right_button = QToolButton()
        self.turn_right_button.setMinimumSize(QSize(50, 50))
        self.turn_right_button.setEnabled(False)
        self.turn_right_button.setToolTip('右转90度')
        self.turn_right_button.setStyleSheet('QToolButton{border-image: url(' + IconPath.right_picture + ')}')
        self.turn_right_button.clicked.connect(self.connect_turn_right_picture)
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
        self.button_h_layout.addWidget(self.zoom_out_button)
        self.button_h_layout.addSpacing(5)
        self.button_h_layout.addWidget(self.suitable_size_button)
        self.button_h_layout.addSpacing(5)
        self.button_h_layout.addWidget(self.original_size_button)
        self.button_h_layout.addSpacing(5)
        self.button_h_layout.addWidget(self.screen_shot_button)
        self.button_h_layout.addStretch(1)
        self.button_h_layout.addWidget(self.picture_path_label)
        self.button_h_layout.addStretch(1)
        self.button_h_layout.addWidget(self.picture_size_label)

        # 填充图片标签
        # self.picture_label = QLabel(self)
        self.picture_label = PictureLabel(self)
        self.picture_label.signal[str].connect(self.receive_signal)
        self.picture_label.setScaledContents(True)

        # 创建一个滚动区域
        self.picture_scroll_area = QScrollArea()
        self.picture_scroll_area.setWidget(self.picture_label)
        self.picture_h_layout.addWidget(self.picture_scroll_area)
        # 悬浮控件
        self.floating_layout = QVBoxLayout(self.picture_scroll_area)
        self.floating_layout.setContentsMargins(0, 0, 0, 0)
        self.floating_frame = QFrame()
        self.floating_frame.setStyleSheet('background-color: #646464')
        self.floating_frame.installEventFilter(self)
        self.float_button_layout = QHBoxLayout(self.floating_frame)
        self.float_button_layout.addStretch(2)
        self.float_button_layout.addWidget(self.last_picture_button)
        self.float_button_layout.addStretch(1)
        self.float_button_layout.addWidget(self.turn_left_button)
        self.float_button_layout.addStretch(1)
        self.float_button_layout.addWidget(self.turn_right_button)
        self.float_button_layout.addStretch(1)
        self.float_button_layout.addWidget(self.next_picture_button)
        self.float_button_layout.addStretch(2)
        # 设置透明度
        self.floating_frame_opacity = QGraphicsOpacityEffect()
        self.floating_frame_opacity.setOpacity(0.0)
        self.floating_frame.setGraphicsEffect(self.floating_frame_opacity)
        self.floating_frame.setAutoFillBackground(True)
        self.floating_frame.setMinimumHeight(self.float_frame_height)
        self.floating_layout.addStretch(1)
        self.floating_layout.addWidget(self.floating_frame)

        self.general_layout.addLayout(self.button_h_layout)
        self.general_layout.addSpacing(2)
        self.general_layout.addLayout(self.picture_h_layout)

        self.setLayout(self.general_layout)

    # 获取信号
    def receive_signal(self, signal_str):
        flag = signal_str.split('>')[0]
        info = signal_str.split('>')[1]
        if flag == 'screen_shot':
            point = eval(info)
            self.save_screen_shot(point)

    # 打开文件(图片)
    def connect_open_file(self):
        file_path = Profile.get_config_value(file=GloVar.config_file_path, section='param', option='file_path')
        # 文件过滤
        file_filter = 'jpg(*.jpg);;png(*.png);;jpeg(*.jpeg);;bmp(*.bmp)'
        # 返回元祖(第一个元素文件路径, 第二个元素文件类型), 这里只需要第一个文件路径
        picture_path = QFileDialog.getOpenFileName(self, '选择需要打开的文件', file_path, file_filter)[0]
        if picture_path:
            picture_path = MergePath.merge_path(picture_path)
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
        self.picture_size_label.setText('size: [%d:%d], zoom: [%.2fX]' % (self.picture_size_width,
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
            self.picture_size_label.setText('size: [%d:%d], zoom: [%.2fX]' % (self.picture_size_width,
                                                                              self.picture_size_height,
                                                                              self.picture_zoom_scale))

    # 截图操作
    def connect_screen_shot(self):
        self.picture_label.setCursor(Qt.CrossCursor)
        self.picture_label.box_flag = True

    # 合适尺寸
    def connect_suitable_size_button(self):
        self.show_picture()

    # 原图操作
    def connect_original_size_button(self):
        self.picture_zoom_scale = 1.0
        self.picture_label.setFixedSize(self.picture_size_width, self.picture_size_height)
        self.picture_size_label.setText('size: [%d:%d], zoom: [1.0X]' % (self.picture_size_width,
                                                                         self.picture_size_height))

    # 切到上一张图片
    def connect_show_last_picture(self):
        current_directory = os.path.dirname(self.picture_path)
        picture_list = []
        for file in os.listdir(current_directory):
            file_path = MergePath.merge_path(current_directory, file)
            if os.path.isfile(file_path):
                file_suffix = file_path.split('.')[1].lower()
                if file_suffix in self.file_type_list:
                    picture_list.append(file_path)
        picture_list_length = len(picture_list)
        if picture_list_length == 1:
            pass
        else:
            current_index = picture_list.index(self.picture_path)
            last_index = current_index - 1
            if last_index < 0:
                last_index = picture_list_length - 1
            self.picture_path = picture_list[last_index]
            self.show_picture()

    # 切到下一张图片
    def connect_show_next_picture(self):
        current_directory = os.path.dirname(self.picture_path)
        picture_list = []
        for file in os.listdir(current_directory):
            file_path = MergePath.merge_path(current_directory, file)
            if os.path.isfile(file_path):
                file_suffix = file_path.split('.')[1].lower()
                if file_suffix in self.file_type_list:
                    picture_list.append(file_path)
        picture_list_length = len(picture_list)
        if picture_list_length == 1:
            pass
        else:
            current_index = picture_list.index(self.picture_path)
            next_index = current_index + 1
            if next_index >= picture_list_length:
                next_index = 0
            self.picture_path = picture_list[next_index]
            self.show_picture()

    def connect_turn_left_picture(self):
        self.image = np.rot90(self.image)
        file_suffix = '.' + os.path.splitext(os.path.split(self.picture_path)[1])[1]
        cv2.imencode(file_suffix, self.image)[1].tofile(self.picture_path)
        self.show_picture()

    def connect_turn_right_picture(self):
        self.image = np.rot90(self.image)
        self.image = np.rot90(self.image)
        self.image = np.rot90(self.image)
        file_suffix = '.' + os.path.splitext(os.path.split(self.picture_path)[1])[1]
        cv2.imencode(file_suffix, self.image)[1].tofile(self.picture_path)
        self.show_picture()

    def connect_save_picture(self):
        pass

    # 图片展示操作
    def show_picture(self):
        if self.picture_path is None:
            return
        self.zoom_button.setEnabled(True)
        self.zoom_out_button.setEnabled(True)
        self.original_size_button.setEnabled(True)
        self.suitable_size_button.setEnabled(True)
        self.last_picture_button.setEnabled(True)
        self.next_picture_button.setEnabled(True)
        self.turn_left_button.setEnabled(True)
        self.turn_right_button.setEnabled(True)
        self.image = cv2.imdecode(np.fromfile(self.picture_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        size = self.image.shape
        self.picture_size_width = int(size[1])
        self.picture_size_height = int(size[0])
        # widget居中显示
        self.picture_scroll_area.setAlignment(Qt.AlignCenter)
        # 设置picture_label尺寸
        if self.picture_size_height <= self.picture_scroll_area.height() and \
                self.picture_size_width <= self.picture_scroll_area.width():
            picture_label_size_height = self.picture_size_height
            picture_label_size_width = self.picture_size_width
            self.picture_zoom_scale = round(1.0, 6)
        else:
            # 真实照片比例
            picture_size_scale = float(self.picture_size_height / self.picture_size_width)
            # 临界比例(根据页面网格布局得到, 不可随便修改)
            limit_size_scale = float(self.picture_scroll_area.height() / self.picture_scroll_area.width())
            if picture_size_scale >= limit_size_scale:
                picture_label_size_height = self.picture_scroll_area.height() - 10
                picture_label_size_width = int(
                    (picture_label_size_height / self.picture_size_height) * self.picture_size_width)
                self.picture_zoom_scale = round((picture_label_size_height / self.picture_size_height), 6)
            else:
                picture_label_size_width = self.picture_scroll_area.width() - 10
                picture_label_size_height = int(
                    (picture_label_size_width / self.picture_size_width) * self.picture_size_height)
                self.picture_zoom_scale = round((picture_label_size_width / self.picture_size_width), 6)
        self.picture_label.setFixedSize(picture_label_size_width, picture_label_size_height)
        self.picture_label.setPixmap(QPixmap(self.picture_path))
        self.picture_path_label.setText(os.path.split(self.picture_path)[1])
        self.picture_size_label.setText('size: [%d:%d], zoom: [%.2fX]' % (self.picture_size_width,
                                                                          self.picture_size_height,
                                                                          self.picture_zoom_scale))

    # 保存截图
    def save_screen_shot(self, point):
        self.picture_label.box_flag = False
        self.picture_label.x0 = 0
        self.picture_label.y0 = 0
        self.picture_label.x1 = 0
        self.picture_label.y1 = 0
        self.picture_label.setCursor(Qt.ArrowCursor)
        # 调出保存照片对话框
        self.position[0] = int(point[0] / self.picture_zoom_scale)
        self.position[1] = int(point[1] / self.picture_zoom_scale)
        self.position[2] = int(point[2] / self.picture_zoom_scale)
        self.position[3] = int(point[3] / self.picture_zoom_scale)
        default_name = '[' + str(self.position[0]) + ',' + str(self.position[1]) + ']' +\
                       '[' + str(self.position[2]) + ',' + str(self.position[2]) + ']'
        self.file_save_dialog = SaveFile(default_name=default_name)
        self.file_save_dialog.signal[str].connect(self.recevie_file_info)
        self.file_save_dialog.exec()

    def recevie_file_info(self, signal_str):
        flag = signal_str.split('>')[0]
        file = signal_str.split('>')[1]
        if flag == 'save_file':
            # 保存图像
            cut_img = self.image[self.position[1]:self.position[3], self.position[0]:self.position[2]]
            if '.' in file:
                file_suffix = '.' + file.split('.')[1]
                cv2.imencode(file_suffix, cut_img)[1].tofile(file)
            else:
                file_suffix = '.jpg'
                cv2.imencode(file_suffix, cut_img)[1].tofile(file + file_suffix)
        else:
            pass
        self.file_save_dialog.deleteLater()
        # 取消红色框
        self.picture_label.update()

    # 窗口尺寸更改
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.show_picture()

    # 事件过滤
    def eventFilter(self, obj, event):
        if obj is self.floating_frame:
            event_type = event.type()
            if event_type == QEvent.Enter:
                self.floating_frame_opacity.setOpacity(0.8)
                self.floating_frame.setGraphicsEffect(self.floating_frame_opacity)
                self.floating_frame.setAutoFillBackground(True)
            elif event_type == QEvent.Leave:
                self.floating_frame_opacity.setOpacity(0.0)
                self.floating_frame.setGraphicsEffect(self.floating_frame_opacity)
                self.floating_frame.setAutoFillBackground(True)
        return super().eventFilter(obj, event)


if __name__ == '__main__':
    picture = '/home/ss/Pictures/desktop.jpg'
    app = QApplication(sys.argv)
    win = PictureWidget(None)
    win.setWindowTitle('截图工具')
    win.show()
    sys.exit(app.exec_())
