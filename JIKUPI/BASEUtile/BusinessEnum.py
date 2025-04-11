from enum import Enum


class AlarmLightEnum(Enum):
    """
    绿灯：正常常亮，绿灯闪：充电中，黄灯闪->绿灯闪：操作过程中，红灯闪：异常
    """
    GREEN_LIGHT = "green_light"
    GREEN_LIGHT_FLASH = "green_light_flash"
    YELLOW_LIGHT_FLASH = "yellow_light_flash"
    RED_LIGHT_FLASH = "red_light_flash"
    STOP_LIGHT = "stop_light"
