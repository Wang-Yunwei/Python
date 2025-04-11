import BASEUtile.BusinessConstant as BusinessConstant
import BASEUtile.Config as Config


# 全局常量参数

def get_serial_usb_door():
    return BusinessConstant.SERIAL_USB_DOOR


def get_serial_bps_door():
    if Config.get_down_version() == "V2.0" or Config.get_down_version() == "V1.0":
        return BusinessConstant.SERIAL_BPS_57600
    else:
        return BusinessConstant.SERIAL_BPS_115200


def get_serial_timeout_door():
    return BusinessConstant.SERIAL_TIMEOUT_DOOR


def get_serial_bytesize_door():
    return BusinessConstant.SERIAL_BYTE_SIZE_8


def get_serial_parity_door():
    return BusinessConstant.SERIAL_PARITY_EVEN


def get_serial_stopbits_door():
    return BusinessConstant.SERIAL_STOP_BITS_1


def get_serial_usb_bar():
    if Config.get_down_version() == "V2.0" or Config.get_down_version() == "V3.0":
        return BusinessConstant.SERIAL_USB_DOOR
    else:
        return BusinessConstant.SERIAL_USB_BAR


def get_serial_bps_bar():
    if Config.get_down_version() == "V2.0" or Config.get_down_version() == "V1.0":
        return BusinessConstant.SERIAL_BPS_57600
    else:
        return BusinessConstant.SERIAL_BPS_115200


def get_serial_timeout_bar():
    return BusinessConstant.SERIAL_TIMEOUT_BAR


def get_serial_bytesize_bar():
    return BusinessConstant.SERIAL_BYTE_SIZE_8


def get_serial_parity_bar():
    return BusinessConstant.SERIAL_PARITY_EVEN


def get_serial_stopbits_bar():
    return BusinessConstant.SERIAL_STOP_BITS_1


def get_serial_usb_gps():
    return BusinessConstant.SERIAL_USB_GPS


def get_serial_bps_gps():
    if Config.get_gps_type() == "2":
        return BusinessConstant.SERIAL_BPS_115200
    else:
        return BusinessConstant.SERIAL_BPS_4800


def get_serial_timeout_gps():
    return BusinessConstant.SERIAL_TIMEOUT


def get_serial_usb_alarm_light():
    return BusinessConstant.SERIAL_USB_GPS


def get_serial_bps_alarm_light():
    return BusinessConstant.SERIAL_BPS_115200


def get_serial_timeout_alarm_light():
    return BusinessConstant.SERIAL_TIMEOUT


def get_serial_bytesize_alarm_light():
    return BusinessConstant.SERIAL_BYTE_SIZE_8


def get_serial_parity_alarm_light():
    return BusinessConstant.SERIAL_PARITY_NONE


def get_serial_stopbits_alarm_light():
    return BusinessConstant.SERIAL_STOP_BITS_1


def get_serial_usb_weather():
    return BusinessConstant.SERIAL_USB_WEATHER


def get_serial_bps_weather():
    return BusinessConstant.SERIAL_BPS_9600


def get_serial_timeout_weather():
    return BusinessConstant.SERIAL_TIMEOUT


def get_serial_bytesize_weather():
    return BusinessConstant.SERIAL_BYTE_SIZE_8


def get_serial_parity_weather():
    return BusinessConstant.SERIAL_PARITY_NONE


def get_serial_stopbits_weather():
    return BusinessConstant.SERIAL_STOP_BITS_1


def get_serial_usb_charge():
    return BusinessConstant.SERIAL_USB_CHARGE


def get_serial_bps_charge():
    if Config.get_wlc_version() == "V1.0" and Config.get_is_wlc_double_connect() is True:
        return BusinessConstant.SERIAL_BPS_115200
    else:
        return BusinessConstant.SERIAL_BPS_9600


def get_serial_timeout_charge():
    return BusinessConstant.SERIAL_TIMEOUT_CHARGE


def get_serial_bytesize_charge():
    return BusinessConstant.SERIAL_BYTE_SIZE_8


def get_serial_parity_charge():
    return BusinessConstant.SERIAL_PARITY_NONE


def get_serial_stopbits_charge():
    return BusinessConstant.SERIAL_STOP_BITS_1


def get_serial_usb_aircondition():
    return BusinessConstant.SERIAL_USB_AIRCONITION


def get_serial_bps_aircondition():
    return BusinessConstant.SERIAL_BPS_9600


def get_serial_timeout_aircondition():
    return BusinessConstant.SERIAL_TIMEOUT


def get_serial_parity_aircondition():
    if Config.get_air_condition_computer_version() == "V2.0":
        return BusinessConstant.SERIAL_PARITY_NONE
    else:
        return BusinessConstant.SERIAL_PARITY_EVEN


def get_serial_stopbits_aircondition():
    return BusinessConstant.SERIAL_STOP_BITS_1


def get_serial_bytesize_aircondition():
    return BusinessConstant.SERIAL_BYTE_SIZE_8
