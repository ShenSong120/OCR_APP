from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from global_var import *


# 保存文件
class SaveFile(QDialog):

    signal = pyqtSignal(str)

    def __init__(self, parent=None, default_name=''):
        super(SaveFile, self).__init__(parent)
        # 起始路径
        self.start_path = Profile.get_config_value(GloVar.config_file_path, 'param', 'save_path')
        # 默认文件名
        self.default_name = default_name
        # 文件路径选择以及文件名字输入
        self.file_path_text = QLineEdit(self)
        self.file_path_text.setReadOnly(True)
        self.file_path_text.setText(self.start_path)
        self.select_path_action = QAction(self.file_path_text)
        self.select_path_action.setIcon(QIcon(IconPath.select_path))
        self.select_path_action.triggered.connect(self.select_path)
        self.file_path_text.addAction(self.select_path_action, QLineEdit.TrailingPosition)
        self.file_name_text = QLineEdit(self)
        self.file_name_text.setFocus()
        self.file_name_text.setText(self.default_name)
        self.file_name_text.selectAll()
        self.des_label = QLabel()
        self.des_label.setText('默认后缀名.jpg, 保存为其他类型时输入全称即可.')
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(20)
        self.form_layout.addRow('文件路径:', self.file_path_text)
        self.form_layout.addRow('文件名字:', self.file_name_text)
        self.form_layout.addRow('描述说明:', self.des_label)
        # 确定和取消按钮
        self.sure_button = QPushButton('确定', self)
        self.sure_button.clicked.connect(self.click_sure)
        self.sure_button.setFixedWidth(100)
        self.cancel_button = QPushButton('取消', self)
        self.cancel_button.clicked.connect(self.click_cancel)
        self.cancel_button.setFixedWidth(100)
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.sure_button)
        self.button_layout.addWidget(self.cancel_button)
        # 全局布局
        self.general_layout = QVBoxLayout(self)
        self.general_layout.setContentsMargins(0, 5, 0, 5)
        self.general_layout.addSpacing(20)
        self.general_layout.addLayout(self.form_layout)
        self.general_layout.addSpacing(20)
        self.general_layout.addLayout(self.button_layout)
        self.setLayout(self.general_layout)
        self.setMinimumWidth(400)
        self.setWindowTitle('保存照片')

    def select_path(self):
        dir_choose = QFileDialog.getExistingDirectory(self, '选取文件夹', self.start_path,
                                                      options=QFileDialog.DontUseNativeDialog)
        if dir_choose:
            self.start_path = dir_choose
            self.file_path_text.setText(dir_choose)
            Profile.set_config_value(GloVar.config_file_path, 'param', 'save_path', dir_choose)

    def click_sure(self):
        file_name = self.file_name_text.text()
        file = MergePath.merge_path(self.start_path, file_name)
        self.signal.emit('save_file>' + str(file))

    def click_cancel(self):
        self.signal.emit('cancel>')
