import BASEUtile.Config as Config
import BASEUtile.BusinessConstant as BusinessConstant


# class StateFlag():
#     '''
#     机库各个串口是否使用状态标记，利用此标记，做串口访问；如果串口被占用，则返回失败结果
#     '''
#
#     def __init__(self, configini):
#         self.door_isused = False
#         self.bar_isused = False
#         self.charge_isused = False
#         self.bar_iswaiting = False  # 是否有推拉杆在等待，默认情况，推拉杆命令可以等待5秒
#         self.weather_isused = False
#         self.configini = configini

def get_is_used_serial_door():
    """
    获取门usb口是否可用
    """
    return BusinessConstant.IS_USED_SERIAL_DOOR


def set_used_serial_door():
    """
    设置门usb口被占用
    """
    BusinessConstant.IS_USED_SERIAL_DOOR = True


def set_used_serial_free_door():
    """
    设置门usb口被释放
    """
    BusinessConstant.IS_USED_SERIAL_DOOR = False


def get_is_used_serial_bar():
    """
    获取推杆usb口是否可用
    """
    if Config.get_down_version() == "V2.0" or Config.get_down_version() == "V3.0":
        return get_is_used_serial_door()
    else:
        return BusinessConstant.IS_USED_SERIAL_BAR


def set_used_serial_bar():
    """
    设置推杆usb口被占用
    """
    if Config.get_down_version() == "V2.0" or Config.get_down_version() == "V3.0":
        set_used_serial_door()
    else:
        BusinessConstant.IS_USED_SERIAL_BAR = True


def set_used_serial_free_bar():
    """
    设置推杆usb口被释放
    """
    if Config.get_down_version() == "V2.0" or Config.get_down_version() == "V3.0":
        set_used_serial_free_door()
    else:
        BusinessConstant.IS_USED_SERIAL_BAR = False


def get_is_used_serial_turn_lift():
    """
    获取旋转台usb口是否可用
    """
    return get_is_used_serial_door()


def set_used_serial_turn_lift():
    """
    设置旋转台usb口被占用
    """
    set_used_serial_door()


def set_used_serial_free_turn_lift():
    """
    设置旋转台usb口被释放
    """
    set_used_serial_free_door()


def get_is_used_serial_updown_lift():
    """
    获取升降台usb口是否可用
    """
    return get_is_used_serial_weather()


def set_used_serial_updown_lift():
    """
    设置升降台usb口被占用
    """
    set_used_serial_weather()


def set_used_serial_free_updown_lift():
    """
    设置升降台usb口被释放
    """
    set_used_serial_free_weather()


def get_is_used_serial_charge():
    """
    获取充电usb口是否可用
    """
    return BusinessConstant.IS_USED_SERIAL_CHARGE


def set_used_serial_charge():
    """
    设置充电usb口被占用
    """
    BusinessConstant.IS_USED_SERIAL_CHARGE = True


def set_used_serial_free_charge():
    """
    设置充电usb口被释放
    """
    BusinessConstant.IS_USED_SERIAL_CHARGE = False


def get_is_used_serial_weather():
    """
    获取天气usb口是否可用
    """
    return BusinessConstant.IS_USED_SERIAL_WEATHER


def set_used_serial_weather():
    """
    设置天气usb口被释放
    """
    BusinessConstant.IS_USED_SERIAL_WEATHER = True


def set_used_serial_free_weather():
    """
    设置天气usb口被释放
    """
    BusinessConstant.IS_USED_SERIAL_WEATHER = False


def get_is_used_serial_gps():
    """
    获取天气usb口是否可用
    """
    return BusinessConstant.IS_USED_SERIAL_GPS


def set_used_serial_gps():
    """
    设置天气usb口被释放
    """
    BusinessConstant.IS_USED_SERIAL_GPS = True


def set_used_serial_free_gps():
    """
    设置天气usb口被释放
    """
    BusinessConstant.IS_USED_SERIAL_GPS = False


def get_is_used_serial_alarm_controller():
    """
    获取警报器usb口是否可用
    """
    return get_is_used_serial_weather()


def set_used_serial_alarm_controller():
    """
    设置警报器usb口被占用
    """
    set_used_serial_weather()


def set_used_serial_free_alarm_controller():
    """
    设置警报器usb口被释放
    """
    set_used_serial_free_weather()
