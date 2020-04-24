import configparser


# 全局变量
class GloVar:
    config_file_path = 'config/config.ini'


# 配置文件路径
class IconPath:
    open_picture_folder = 'config/icon/open_picture.png'
    open_picture = 'config/icon/open_picture.png'
    zoom_picture = 'config/icon/zoom.png'
    zoom_out_picture = 'config/icon/zoom_out.png'
    original_size_picture = 'config/icon/original_size.png'
    screen_shot = 'config/icon/screen_shot.png'


# 配置文件的读取和写入
class Profile:
    # 获取配置文件value
    @staticmethod
    def get_config_value(file, section, option):
        config = configparser.ConfigParser()
        config.read(file, encoding='utf-8')
        value = config.get(section, option)
        return value

    # 设置config的参数
    @staticmethod
    def set_config_value(file, section, option, value):
        config = configparser.ConfigParser()
        config.read(file, encoding='utf-8')
        if section not in config.sections():
            config.add_section(section)
        config.set(section, option, str(value))
        with open(file, 'w+', encoding='utf-8') as cf:
            config.write(cf)

    # 获取节点options
    @staticmethod
    def get_config_options(file, section):
        config = configparser.ConfigParser()
        config.read(file, encoding='utf-8-sig')
        options = config.options(section)
        return options


# 合并路径(传入要合并的几个部分)
class MergePath:
    @staticmethod
    def merge_path(*args):
        path_list = []
        for section in args:
            if '\\\\' in section:
                section = section.replace('\\\\', '/')
            elif '\\' in section:
                section = section.replace('\\', '/')
            else:
                section = section
            path_list.append(section)
        merged_path = '/'.join(path_list)
        if '//' in merged_path:
            merged_path = merged_path.replace('//', '/')
        else:
            merged_path = merged_path
        return merged_path
