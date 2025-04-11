import USBDevice.USBDeviceConfig as USBDeviceConfig
import BASEUtile.BusinessConstant as BusinessConstant
import serial


def get_com_serial(serial_port) -> serial:
    com_serial = None
    if serial_port == BusinessConstant.USB_WEATHER:
        com_serial = serial.Serial(port=USBDeviceConfig.get_serial_usb_weather(),
                                   baudrate=USBDeviceConfig.get_serial_bps_weather(),
                                   timeout=USBDeviceConfig.get_serial_timeout_weather(),
                                   bytesize=USBDeviceConfig.get_serial_bytesize_weather(),
                                   parity=USBDeviceConfig.get_serial_parity_weather(),
                                   stopbits=USBDeviceConfig.get_serial_stopbits_weather())
    elif serial_port == BusinessConstant.USB_AIRCONITION:
        com_serial = serial.Serial(port=USBDeviceConfig.get_serial_usb_aircondition(),
                                   baudrate=USBDeviceConfig.get_serial_bps_aircondition(),
                                   timeout=USBDeviceConfig.get_serial_timeout_aircondition(),
                                   bytesize=USBDeviceConfig.get_serial_bytesize_aircondition(),
                                   parity=USBDeviceConfig.get_serial_parity_aircondition(),
                                   stopbits=USBDeviceConfig.get_serial_stopbits_aircondition())
    elif serial_port == BusinessConstant.USB_DOOR:
        com_serial = serial.Serial(port=USBDeviceConfig.get_serial_usb_door(),
                                   baudrate=USBDeviceConfig.get_serial_bps_door(),
                                   timeout=USBDeviceConfig.get_serial_timeout_door(),
                                   bytesize=USBDeviceConfig.get_serial_bytesize_door(),
                                   parity=USBDeviceConfig.get_serial_parity_door(),
                                   stopbits=USBDeviceConfig.get_serial_stopbits_door())
    elif serial_port == BusinessConstant.USB_BAR:
        com_serial = serial.Serial(port=USBDeviceConfig.get_serial_usb_bar(),
                                   baudrate=USBDeviceConfig.get_serial_bps_bar(),
                                   timeout=USBDeviceConfig.get_serial_timeout_bar(),
                                   bytesize=USBDeviceConfig.get_serial_bytesize_bar(),
                                   parity=USBDeviceConfig.get_serial_parity_bar(),
                                   stopbits=USBDeviceConfig.get_serial_stopbits_bar())
    elif serial_port == BusinessConstant.USB_CHARGE:
        com_serial = serial.Serial(port=USBDeviceConfig.get_serial_usb_charge(),
                                   baudrate=USBDeviceConfig.get_serial_bps_charge(),
                                   timeout=USBDeviceConfig.get_serial_timeout_charge(),
                                   bytesize=USBDeviceConfig.get_serial_bytesize_charge(),
                                   parity=USBDeviceConfig.get_serial_parity_charge(),
                                   stopbits=USBDeviceConfig.get_serial_stopbits_charge())
    elif serial_port == BusinessConstant.USB_ALARM_LIGHT:
        com_serial = serial.Serial(port=USBDeviceConfig.get_serial_usb_alarm_light(),
                                   baudrate=USBDeviceConfig.get_serial_bps_alarm_light(),
                                   timeout=USBDeviceConfig.get_serial_timeout_alarm_light(),
                                   bytesize=USBDeviceConfig.get_serial_bytesize_alarm_light(),
                                   parity=USBDeviceConfig.get_serial_parity_alarm_light(),
                                   stopbits=USBDeviceConfig.get_serial_stopbits_alarm_light())
    return com_serial
