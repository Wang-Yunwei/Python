from BASEUtile.BusinessEnum import AlarmLightEnum

# 串口配置信息
SERIAL_TIMEOUT = 1
SERIAL_WAIT_TIMEOUT = 2
SERIAL_BPS_4800 = 4800
SERIAL_BPS_9600 = 9600
SERIAL_BPS_57600 = 57600
SERIAL_BPS_115200 = 115200
SERIAL_BYTE_SIZE_8 = 8
SERIAL_STOP_BITS_1 = 1
SERIAL_PARITY_NONE = 'N'
SERIAL_PARITY_EVEN = 'E'
SERIAL_PARITY_ODD = 'O'
SERIAL_USB_WEATHER = "/dev/ttyUSBWeather"
# SERIAL_USB_WEATHER = "COM3"
# SERIAL_USB_CHARGE = "COM7"
SERIAL_USB_CHARGE = "/dev/ttyUSBCharge"
SERIAL_USB_AIRCONITION = "/dev/ttyUSBWeather"
SERIAL_TIMEOUT_CHARGE = 10
SERIAL_USB_DOOR = "/dev/ttyUSBDoor"
SERIAL_TIMEOUT_DOOR = 30
SERIAL_USB_BAR = "/dev/ttyUSBBar"
SERIAL_TIMEOUT_BAR = 30
SERIAL_USB_GPS = "/dev/ttyUSBGPS"
# SERIAL_USB_GPS = "COM3"
# 串口区分
USB_WEATHER = "USBWeather"
USB_AIRCONITION = "USBAircondition"
USB_CHARGE = "USBCharge"
USB_DOOR = "USBDoor"
USB_BAR = "USBBar"
USB_GPS = "USBGps"
USB_ALARM_LIGHT = "USBAlarmLight"
# 串口是否占用标识
IS_USED_SERIAL_WEATHER = False  # 气象USB口是否被占用
IS_USED_SERIAL_BAR = False  # 夹杆USB口是否被占用
IS_USED_SERIAL_DOOR = False  # 门USB口是否被占用
IS_USED_SERIAL_CHARGE = False  # 充电USB口是否被占用
IS_USED_SERIAL_AIR = False  # 空调USB口是否被占用
IS_USED_SERIAL_GPS = False  # GPS口是否被占用
# 返回值
SUCCESS = "success"
ERROR = "error"
BUSY = "busy"
OVERTIME = "overtime"
# 状态
UP_STATE = "up"
UPING_STATE = "uping"
DOWN_STATE = "down"
DOWNING_STATE = "downing"
OPEN_STATE = "open"
OPENING_STATE = "opening"
CLOSE_STATE = "close"
CLOSING_STATE = "closing"
TURN_STATE = "turn"
TURNING_STATE = "turning"
BACK_STATE = "back"
BACKING_STATE = "backing"
# 电池状态
CHARGE_STATE_TAKEOFF = "takeoff"  # 开机
CHARGE_STATE_STANDBY = "standby"  # 待机
CHARGE_STATE_CLOSE = "close"  # 关机
CHARGE_STATE_CHARGING = "charging"  # 充电中
# 电池满电判断
CHARGE_FULL_VALUE = 98
# 灯颜色显示标识
ALARM_LIGHT = AlarmLightEnum.GREEN_LIGHT
# log打印间隔数量累计,防止log过多,例如：每隔20次打印一个log信息
LOG_TIME_INIT = 0
LOG_TIME_ALL = 20
LOGGER = None  # 全局log对象
