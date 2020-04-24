from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class PictureLabel(QLabel):
    def __init__(self, parent):
        super(PictureLabel, self).__init__(parent)

    # 鼠标点击事件
    def mousePressEvent(self, event):
        self.mouse_press_flag = True
        self.x0 = event.x()
        self.y0 = event.y()
        self.x0 = self.x0
        self.y1 = self.y0

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        if self.mouse_move_flag is True:
            # 如果框选屏幕大小(返回框选的尺寸信息)
            if GloVar.box_screen_flag is True:
                # 框选的车机屏幕大小
                self.box_screen_size[0] = self.x0
                self.box_screen_size[1] = self.y0
                self.box_screen_size[2] = abs(self.x1-self.x0)
                self.box_screen_size[3] = abs(self.y1-self.y0)
                # 起点和终点所占video_label比例
                self.box_screen_scale[0] = round(float(self.x0/self.size().width()),  6)
                self.box_screen_scale[1] = round(float(self.y0/self.size().height()), 6)
                self.box_screen_scale[2] = round(float(self.x1/self.size().width()),  6)
                self.box_screen_scale[3] = round(float(self.y1/self.size().height()), 6)
                # 将box_screen_scale尺寸存入配置文件(不需要每次打开都进行框选)
                Profile(type='write', file=GloVar.config_file_path, section='param', option='box_screen_scale',
                        value=str(self.box_screen_scale))
                GloVar.box_screen_flag = False
                GloVar.select_template_flag = False
                GloVar.add_action_button_flag = True
                self.setCursor(Qt.ArrowCursor)
                Logger('[框选车机屏幕]--起点及尺寸: %s' % str(self.box_screen_size))
            # 如果是机械臂滑动动作
            elif RobotArmAction.uArm_action_type == RobotArmAction.uArm_slide:
                start = self.calculating_point(self.x0, self.y0)
                end = self.calculating_point(self.x1, self.y1)
                position = start + end
                info_list = [RobotArmAction.uArm_slide, position]
                # 发送机械臂操作信息
                self.signal.emit('position_info>' + str(info_list))
            # 其余情况判断是否暂停(若有暂停, 则可以进行模板框选)
            else:
                self.save_template()
        else:
            if RobotArmAction.uArm_action_type == RobotArmAction.uArm_click:
                position = self.calculating_point(self.x0, self.y0)
                info_list = [RobotArmAction.uArm_click, position]
                # 发送机械臂操作信息
                self.signal.emit('position_info>' + str(info_list))
            elif RobotArmAction.uArm_action_type == RobotArmAction.uArm_double_click:
                position = self.calculating_point(self.x0, self.y0)
                info_list = [RobotArmAction.uArm_double_click, position]
                # 发送机械臂操作信息
                self.signal.emit('position_info>' + str(info_list))
            elif RobotArmAction.uArm_action_type == RobotArmAction.uArm_long_click:
                position = self.calculating_point(self.x0, self.y0)
                info_list = [RobotArmAction.uArm_long_click, position]
                # 发送机械臂操作信息
                self.signal.emit('position_info>' + str(info_list))
        self.mouse_press_flag = False
        self.mouse_move_flag = False

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
        # 滑动动作直线显示
        if RobotArmAction.uArm_action_type == RobotArmAction.uArm_slide:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 5, Qt.SolidLine))
            painter.drawLine(QPoint(self.x0, self.y0), QPoint(self.x1, self.y1))
            if self.video_play_flag is False:
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawRect(QRect(self.box_screen_size[0], self.box_screen_size[1], self.box_screen_size[2],
                                       self.box_screen_size[3]))
        # 点击动作画圆显示
        elif RobotArmAction.uArm_action_type in [RobotArmAction.uArm_click, RobotArmAction.uArm_long_click,
                                                 RobotArmAction.uArm_double_click]:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 5, Qt.SolidLine))
            painter.drawEllipse(self.x0-5, self.y0-5, 10, 10)
            if self.video_play_flag is False:
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawRect(QRect(self.box_screen_size[0], self.box_screen_size[1], self.box_screen_size[2],
                                       self.box_screen_size[3]))
        # 框选动作
        elif GloVar.select_template_flag is True:
            rect = QRect(self.x0, self.y0, abs(self.x1 - self.x0), abs(self.y1 - self.y0))
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.drawRect(rect)
            if self.video_play_flag is False:
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawRect(QRect(self.box_screen_size[0], self.box_screen_size[1], self.box_screen_size[2],
                                       self.box_screen_size[3]))
        # 其余情况(不绘制图, 一个小点,几乎不能看到)
        else:
            point = [QPoint(self.x0, self.y0)]
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
            painter.drawPoints(QPolygon(point))
            if self.video_play_flag is False:
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.drawRect(QRect(self.box_screen_size[0], self.box_screen_size[1], self.box_screen_size[2],
                                       self.box_screen_size[3]))

    # 保存模板
    def save_template(self):
        if GloVar.select_template_flag is True:
            # x_unit, y_unit = 1280 / 1280, 1024 / 1024
            x_unit, y_unit = self.x_unit, self.y_unit
            x0, y0, x1, y1 = int(self.x0 * x_unit), int(self.y0 * y_unit), int(self.x1 * x_unit), int(self.y1 * y_unit)
            cut_img = self.mask_image[y0:y1, x0:x1]
            # 直播状态
            if self.video_play_flag is False:
                # 如果是case中框选视频模板动作
                if GloVar.draw_frame_flag == GloVar.result_template:
                    # 接收模板路径
                    mask_path = GloVar.mask_path
                    # default_name = 'type-name'
                    default_name = RecordAction.current_video_type + '/' + RecordAction.current_video_name
                elif GloVar.draw_frame_flag == GloVar.assert_template:
                    mask_path = GloVar.mask_path
                    # 获取断言模板图片名字
                    if os.path.exists(mask_path):
                        assert_template_list = os.listdir(mask_path)
                        if len(assert_template_list) > 0:
                            if (GloVar.assert_template + '-') in assert_template_list[-1]:
                                num = int(assert_template_list[-1].split('-')[1].split('.')[0])
                            else:
                                num = len(assert_template_list)
                        else:
                            num = 0
                    else:
                        num = 0
                    default_name = GloVar.assert_template + '-' + str(num + 1)
                else:
                    # 接收模板路径
                    mask_path = GloVar.mask_path
                    default_name = '截图'
                    # default_name = '[' + str(x0) + ',' + str(y0) + ']' + '[' + str(x1) + ',' + str(y1) + ']'
            # 本地视频播放
            elif self.video_play_flag is True:
                # 数据处理产生的模板
                if GloVar.data_process_flag is True:
                    mask_path = os.path.split(GloVar.mask_path)[0]
                    default_name = os.path.split(GloVar.mask_path)[1]
                # 离线视频产生的模板
                else:
                    mask_path = GloVar.mask_path
                    default_name = '截图'
                    # default_name = '[' + str(x0) + ',' + str(y0) + ']' + '[' + str(x1) + ',' + str(y1) + ']'
            else:
                Logger('[当前状态不允许保存模板!]')
                return
            # 如果模板路径为None(说明不允许框选模板)
            if mask_path is not None:
                # value, ok = QInputDialog.getText(self, '标注输入框', '请输入文本', QLineEdit.Normal, '应用')
                value, ok = QInputDialog.getText(self, '标注输入框', '请输入文本', QLineEdit.Normal, default_name)
                # 如果输入有效值
                if ok:
                    # 如果是数据处理(需要对图像特殊处理)
                    if GloVar.data_process_flag is True:
                        # 将模板灰度化/并在模板起始位置打标记
                        rect_image = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)  # ##灰度化
                        # 在模板起始位置打标记(以便于模板匹配时快速找到模板位置, 每一列前四个像素分别代表 千/百/十/个 位)
                        # rect_image[0][0] = y0 // 10
                        # rect_image[0][1] = y1 // 10
                        # rect_image[0][2] = x0 // 10
                        # rect_image[0][3] = x1 // 10
                        rect_image = self.write_position_info_to_roi(rect_image, 0, y0)
                        rect_image = self.write_position_info_to_roi(rect_image, 1, y1)
                        rect_image = self.write_position_info_to_roi(rect_image, 2, x0)
                        rect_image = self.write_position_info_to_roi(rect_image, 3, x1)
                        cut_img = rect_image
                        # 模板存放位置
                        mask_path = mask_path
                        if os.path.exists(mask_path) is False:
                            os.makedirs(mask_path)
                        template_name = MergePath([mask_path, value + '.bmp']).merged_path
                        cv2.imencode('.bmp', cut_img)[1].tofile(template_name)
                    # 非数据处理情况
                    else:
                        # 如果输入的参数中带有'-'代表需要分级保存, 并需要新建文件夹
                        if '/' in value:
                            # 直播时的情况
                            if self.video_play_flag is False:
                                folder_layer_count = len(value.split('/')) - 1
                                if folder_layer_count == 1:
                                    mask_path = MergePath([mask_path, value.split('/')[0]]).merged_path
                                elif folder_layer_count == 2:
                                    mask_path = MergePath([mask_path, value.split('/')[0], value.split('/')[1]]).merged_path
                                else:
                                    Logger('[输入的模板名称错误!]')
                                    return
                                if os.path.exists(mask_path) is False:
                                    os.makedirs(mask_path)
                                # 如果是框选数据匹配模板的话(框选模板保存为灰度图)
                                if GloVar.draw_frame_flag == GloVar.result_template:
                                    # 将模板灰度化/并在模板起始位置打标记
                                    rect_image = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)  # ##灰度化
                                    # 在模板起始位置打标记(以便于模板匹配时快速找到模板位置)
                                    # rect_image[0][0] = y0 // 10
                                    # rect_image[0][1] = y1 // 10
                                    # rect_image[0][2] = x0 // 10
                                    # rect_image[0][3] = x1 // 10
                                    rect_image = self.write_position_info_to_roi(rect_image, 0, y0)
                                    rect_image = self.write_position_info_to_roi(rect_image, 1, y1)
                                    rect_image = self.write_position_info_to_roi(rect_image, 2, x0)
                                    rect_image = self.write_position_info_to_roi(rect_image, 3, x1)
                                    cut_img = rect_image
                                    template_name = MergePath([mask_path, value.split('/')[-1] + '.bmp']).merged_path
                                    cv2.imencode('.bmp', cut_img)[1].tofile(template_name)
                                    # 视频动作中模板框选完成
                                    self.signal.emit(GloVar.result_template_finished + '>' + template_name)
                                # 断言模板
                                elif GloVar.draw_frame_flag == GloVar.assert_template:
                                    # 将模板灰度化/并在模板起始位置打标记
                                    rect_image = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)  # ##灰度化
                                    # 在模板起始位置打标记(以便于模板匹配时快速找到模板位置)
                                    rect_image = self.write_position_info_to_roi(rect_image, 0, y0)
                                    rect_image = self.write_position_info_to_roi(rect_image, 1, y1)
                                    rect_image = self.write_position_info_to_roi(rect_image, 2, x0)
                                    rect_image = self.write_position_info_to_roi(rect_image, 3, x1)
                                    cut_img = rect_image
                                    template_name = MergePath([mask_path, RecordAction.current_video_name, default_name,
                                                               value + '.bmp']).merged_path
                                    cv2.imencode('.bmp', cut_img)[1].tofile(template_name)
                                    # 视频动作中模板框选完成
                                    self.signal.emit(GloVar.assert_template_finished + '>' + template_name)
                                else:
                                    template_name = MergePath([mask_path, value.split('/')[-1] + '.jpg']).merged_path
                                    cv2.imencode('.jpg', cut_img)[1].tofile(template_name)
                            # 本地视频播放的情况下
                            elif self.video_play_flag is True:
                                template_name = 'null'
                                Logger('[输入的模板名称错误!]')
                            # 其余情况(不播放视频)
                            else:
                                template_name = 'null'
                                Logger('[此时状态不应该有模板输入!]')
                        # 如果输入的参数中不带有'-', 则图片正常保存即可
                        else:
                            # 直播
                            if self.video_play_flag is False:
                                mask_path = MergePath([mask_path]).merged_path
                            # 本地视频播放
                            elif self.video_play_flag is True:
                                mask_path = mask_path
                            # 其余情况(不播放视频)
                            else:
                                mask_path = mask_path
                            if os.path.exists(mask_path) is False:
                                os.makedirs(mask_path)
                            # 如果是框选数据匹配模板的话(框选模板保存为灰度图)
                            if GloVar.draw_frame_flag == GloVar.result_template:
                                # 将模板灰度化/并在模板起始位置打标记
                                rect_image = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)  # ##灰度化
                                # 在模板起始位置打标记(以便于模板匹配时快速找到模板位置)
                                rect_image = self.write_position_info_to_roi(rect_image, 0, y0)
                                rect_image = self.write_position_info_to_roi(rect_image, 1, y1)
                                rect_image = self.write_position_info_to_roi(rect_image, 2, x0)
                                rect_image = self.write_position_info_to_roi(rect_image, 3, x1)
                                cut_img = rect_image
                                template_name = MergePath([mask_path, value.split('/')[-1] + '.bmp']).merged_path
                                cv2.imencode('.bmp', cut_img)[1].tofile(template_name)
                                # 视频动作中模板框选完成
                                self.signal.emit(GloVar.result_template_finished + '>' + template_name)
                            # 断言模板
                            elif GloVar.draw_frame_flag == GloVar.assert_template:
                                # 将模板灰度化/并在模板起始位置打标记
                                rect_image = cv2.cvtColor(cut_img, cv2.COLOR_BGR2GRAY)  # ##灰度化
                                # 在模板起始位置打标记(以便于模板匹配时快速找到模板位置)
                                rect_image = self.write_position_info_to_roi(rect_image, 0, y0)
                                rect_image = self.write_position_info_to_roi(rect_image, 1, y1)
                                rect_image = self.write_position_info_to_roi(rect_image, 2, x0)
                                rect_image = self.write_position_info_to_roi(rect_image, 3, x1)
                                cut_img = rect_image
                                template_name = MergePath([mask_path, value + '.bmp']).merged_path
                                cv2.imencode('.bmp', cut_img)[1].tofile(template_name)
                                # 视频动作中模板框选完成
                                self.signal.emit(GloVar.assert_template_finished + '>' + template_name)
                            else:
                                template_name = MergePath([mask_path, value + '.jpg']).merged_path
                                cv2.imencode('.jpg', cut_img)[1].tofile(template_name)
                    # case中框选模板标志位复位
                    GloVar.draw_frame_flag = GloVar.other_template
                    Logger('[框选的模板保存路径为]: %s' % template_name)
                else:
                    Logger('[框选动作取消!]')
            # 保存完图片后, 让红色框消失
            self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0