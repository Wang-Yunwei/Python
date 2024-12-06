# 全局常量参数

# door接口
device_info_door = "/dev/ttyUSBDoor"
bps_door = 57600
timeout_door = 30

# bar接口
device_info_bar = "/dev/ttyUSBBar"
bps_bar = 57600
timeout_bar = 30

# GPS接口
device_info_gps = "/dev/ttyUSBGPS"
bps_gps = 4800  #old
#bps_gps = 115200  #new
timeout_gps = 0

# 气象接口
device_info_weather = "/dev/ttyUSBWeather"
bps_weather = 9600
timeout_weather = 3

# 空调接口
device_info_aircondition = "/dev/ttyUSBWeather"
bps_aircondition = 9600
timeout_aircondition = 3

# 充电接口
# 充电的串口信息
device_info_charge = "/dev/ttyUSBCharge"
bps_charge = 115200
charge_bytesize = 8
charge_parity = "N"
charge_stopbits = "1"
charge_threshold = 2

# 触点充电2.0充电接口
# 充电的串口信息
device_info_chargeV2 = "/dev/ttyUSBCharge"
bps_chargeV2 = 9600
charge_bytesizeV2 = 8
charge_parityV2 = "N"
charge_stopbitsV2 = "1"
charge_thresholdV2 = 2


# 作废 [不替换]
# device_info_ups = "/dev/ttyUSBUPS"
# bps_ups = 2400
# timeout_ups = 0

# 作废 [不替换]
# device_info_0 = "/dev/ttyUSB0"
# bps_0 = 115200
# timeout_0 = 20


class USBDeviceConfig(object):
    def __init__(self,configini):
        # 外部传入
        self.configini=configini
        self.init()

    def init(self):
        global device_info_bar
        # 如果想特殊处理，在初始化中追加
        if self.configini.get_down_version()=="V2.0" or self.configini.get_down_version()=="V3.0":
            device_info_bar="/dev/ttyUSBDoor"
        return

    def set_device_info_door(self, value):
        global device_info_door
        device_info_door = value

    def get_device_info_door(self):
        global device_info_door
        return device_info_door

    def set_bps_door(self, value):
        global bps_door
        bps_door = value

    def get_bps_door(self):
        global bps_door
        if self.configini.get_down_version() == "V2.0" or self.configini.get_down_version()=="V1.0":
            bps_door=57600
        else:
            bps_door=115200
        return bps_door

    def set_timeout_door(self, value):
        global timeout_door
        timeout_door = value

    def get_timeout_door(self):
        global timeout_door
        return timeout_door

    def set_device_info_bar(self, value):
        global device_info_bar
        device_info_bar = value

    def get_device_info_bar(self):
        global device_info_bar
        return device_info_bar

    def set_bps_bar(self, value):
        global bps_bar
        bps_bar = value

    def get_bps_bar(self):
        global bps_bar
        if self.configini.get_down_version() == "V2.0" or self.configini.get_down_version() == "V1.0":
            bps_bar = 57600
        else:
            bps_bar = 115200
        return bps_bar

    def set_timeout_bar(self, value):
        global timeout_bar
        timeout_bar = value

    def get_timeout_bar(self):
        global timeout_bar
        return timeout_bar

    def set_device_info_gps(self, value):
        global device_info_gps
        device_info_gps = value

    def get_device_info_gps(self):
        global device_info_gps
        return device_info_gps
    
    def set_bps_gps(self, value):
        global bps_gps
        bps_gps = value

    def get_bps_gps(self):
        global bps_gps
        if self.configini.get_gps_type() == "2":
            bps_gps = 115200
        return bps_gps
    
    def set_timeout_gps(self, value):
        global timeout_gps
        timeout_gps = value

    def get_timeout_gps(self):
        global timeout_gps
        return timeout_gps

    def set_device_info_weather(self, value):
        global device_info_weather
        device_info_weather = value

    def get_device_info_weather(self):
        global device_info_weather
        return device_info_weather

    def set_bps_weather(self, value):
        global bps_weather
        bps_weather = value

    def get_bps_weather(self):
        global bps_weather
        return bps_weather

    def set_timeout_weather(self, value):
        global timeout_weather
        timeout_weather = value

    def get_timeout_weather(self):
        global timeout_weather
        return timeout_weather

    def set_device_info_charge(self, value):
        global device_info_charge
        device_info_charge = value

    def get_device_info_charge(self):
        global device_info_charge
        return device_info_charge

    def set_bps_charge(self, value):
        global bps_charge
        bps_charge = value

    def get_bps_charge(self):
        global bps_charge
        return bps_charge

    def set_bytesize_charge(self, value):
        global charge_bytesize
        charge_bytesize = value

    def get_charge_bytesize_charge(self):
        global charge_bytesize
        return charge_bytesize

    def set_parity_charge(self, value):
        global charge_parity
        charge_parity = value

    def get_charge_parity(self):
        global charge_parity
        return charge_parity

    def set_charge_stopbits(self, value):
        global charge_stopbits
        charge_stopbits = value

    def get_charge_stopbits(self):
        global charge_stopbits
        return charge_stopbits

    def set_charge_threshold(self, value):
        global charge_threshold
        charge_threshold = value

    def get_charge_threshold(self):
        global charge_threshold
        return charge_threshold

    def set_device_info_chargeV2(self, value):
        global device_info_chargeV2
        device_info_chargeV2 = value

    def get_device_info_chargeV2(self):
        global device_info_chargeV2
        return device_info_chargeV2

    def set_bps_chargeV2(self, value):
        global bps_chargeV2
        bps_chargeV2 = value

    def get_bps_chargeV2(self):
        global bps_chargeV2
        return bps_chargeV2

    def set_bytesize_chargeV2(self, value):
        global charge_bytesizeV2
        charge_bytesizeV2 = value

    def get_charge_bytesize_chargeV2(self):
        global charge_bytesizeV2
        return charge_bytesizeV2

    def set_parity_chargeV2(self, value):
        global charge_parityV2
        charge_parityV2 = value

    def get_charge_parityV2(self):
        global charge_parityV2
        return charge_parityV2

    def set_charge_stopbitsV2(self, value):
        global charge_stopbitsV2
        charge_stopbitsV2 = value

    def get_charge_stopbitsV2(self):
        global charge_stopbitsV2
        return charge_stopbitsV2

    def set_charge_thresholdV2(self, value):
        global charge_thresholdV2
        charge_thresholdV2 = value

    def get_charge_thresholdV2(self):
        global charge_thresholdV2
        return charge_thresholdV2
    def get_aircondition_bps(self):
        global bps_aircondition
        return bps_aircondition
    def get_aircondition_usbname(self):
        global device_info_aircondition
        return device_info_aircondition
    def get_aircondition_timeout(self):
        global timeout_aircondition
        return timeout_aircondition

if __name__ == "__main__":
    # usb = USBDeviceConfig()
    # usb2 = USBDeviceConfig()
    # print(usb.get_device_info_door())
    # print(usb2.get_device_info_door())
    # usb.set_device_info_door("222")
    # print(usb.get_device_info_door())
    # print(usb2.get_device_info_door())
    pass
