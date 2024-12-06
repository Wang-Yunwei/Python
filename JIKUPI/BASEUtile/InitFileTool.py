import configparser

config = configparser.ConfigParser()  # 实例化

#path = r"D:/WKZNSVNAPP112/JIKUPI/JIKUPI/jiku_config.ini"  # 自己测试ini文件路径
path = r"/home/wkzn/JIKUPI/jiku_config.ini"  # 正式版本ini文件路径
# path = r"E:\python_jk_mqtt\JIKUPI\jiku_config.ini"  # pang.hy测试ini文件路径
config.read(path, encoding="utf-8-sig")

'''
读取整个section
'''


def get_section(section_name):
    return config.items(section_name)


'''
判断是否存在指定 section
'''


def is_have_section(section_name):
    sections = config.sections()
    if section_name in sections:
        return True
    else:
        return False


'''
判断是否存在指定 section 下的 option
'''


def is_have_option(section_name, option_name):
    if is_have_section(section_name):
        options = config.options(section_name)
        if option_name in options:
            return True
        else:
            return False
    else:
        return False


'''
[主要方法]设置值（只写入）
'''


def set_value(section_name, option_name, value):
    config.set(section_name, option_name, value)
    config.write(open(path, 'w+', encoding="utf-8-sig"))


'''
增加新对象
'''


def add_section(section_name):
    config.add_section(section_name)
    config.write(open(path, 'w+', encoding="utf-8-sig"))


'''
设置值，没有就增加
'''


def add_section_option_value(section_name, option_name, value):
    if not is_have_section(section_name):
        add_section(section_name)
    set_value(section_name, option_name, value)


'''
[主要方法] 初始化某个参数，如果没有就给设置默认值
'''


def init_section_option_value(section_name, option_name, def_value):
    if not is_have_option(section_name, option_name):
        add_section_option_value(section_name, option_name, def_value)


'''
[主要方法]读取某个section下某个option的值(不同类型)
'''


def get_str_value(section_name, option_name):
    return config.get(section_name, option_name)


def get_boolean_value(section_name, option_name):
    return config.getboolean(section_name, option_name)


def get_int_value(section_name, option_name):
    return config.getint(section_name, option_name)


def get_float_value(section_name, option_name):
    return config.getfloat(section_name, option_name)


if __name__ == '__main__':
    print(get_section("websocket_info"))
    print(get_section("mqtt_info"))
    print(get_int_value("mqtt_info", "port_int"))
    print(type(get_int_value("mqtt_info", "port_int")))
    # print(type(get_str_value("mqtt_info", "abc")))
    # print(is_have_section("mqtt_info"))
    # print(is_have_option("mqtt_info", "host_str"))
    # add_section_option_value("test_info", "test1", "abc")
    # set_value("test_info", "test1", "def")
    # init_section_option_value("test_info", "test2", "222")
