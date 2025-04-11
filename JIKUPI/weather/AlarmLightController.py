import BASEUtile.BusinessConstant as BusinessConstant
from BASEUtile.BusinessEnum import AlarmLightEnum
import BASEUtile.Config as Config
from functools import wraps
import USBDevice.ComSerial as ComSerial
import BASEUtile.BusinessUtil as BusinessUtil
import WFCharge.WFState as WFState
import time
import threading


def AlarmLight(fun):
    """
    操作通过灯来显示
    红色：异常
    绿色：正常
    黄色：正在执行
    """

    @wraps(fun)
    def wrapper(*args, **kwargs):
        try:
            if Config.get_is_alarm_light() is True:
                # 执行中显示黄闪->绿闪
                # open_yellow_light()
                # BusinessConstant.ALARM_LIGHT = AlarmLightEnum.YELLOW_LIGHT_FLASH
                BusinessConstant.ALARM_LIGHT = AlarmLightEnum.GREEN_LIGHT_FLASH
            print("[AlarmLight.wrapper]开始")
            result = fun(*args, **kwargs)
            if Config.get_is_alarm_light() is True:
                # 执行完正常显示绿色，异常显示红闪
                if result.endswith("0") is True or result == BusinessConstant.SUCCESS:
                    # open_green_light()
                    BusinessConstant.ALARM_LIGHT = AlarmLightEnum.GREEN_LIGHT
                else:
                    # open_red_light()
                    BusinessConstant.ALARM_LIGHT = AlarmLightEnum.RED_LIGHT_FLASH
            print("[AlarmLight.wrapper]结束")
            return result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().error(f"[AlarmLight.wrapper]警灯显示异常,异常信息为:{ex}")

    return wrapper


def open_light_thread():
    """
    灯控制线程 绿灯：正常常亮，绿灯闪：充电中，黄灯闪->绿灯闪：操作过程中，红灯闪：异常
    """
    com_serial = None
    # flash_num = 0  # 闪烁灯显示标识
    while True:
        try:
            # BusinessConstant.LOGGER.get_log().info(f"[AlarmLight.open_light_thread]警示灯打开-开始")
            print(f"[AlarmLight.open_light_thread]警示灯打开-开始,灯颜色为:{BusinessConstant.ALARM_LIGHT}")
            com_serial = ComSerial.get_com_serial(BusinessConstant.USB_ALARM_LIGHT)
            BusinessUtil.open_serial(com_serial, BusinessConstant.LOGGER)
            flash_num = 0  # 闪烁灯显示标识
            while True:
                if BusinessConstant.ALARM_LIGHT == AlarmLightEnum.STOP_LIGHT:
                    time.sleep(60)
                elif BusinessConstant.ALARM_LIGHT == AlarmLightEnum.YELLOW_LIGHT_FLASH:  # 黄闪
                    if flash_num % 2 == 0:
                        yellow_command = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF CC F0 00 AA BB"
                        result = BusinessUtil.execute_command(yellow_command, com_serial, BusinessConstant.LOGGER, is_hex=True,is_log_time=True)
                        flash_num = 1
                    else:
                        close_command = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 00 00 AA BB"
                        result = BusinessUtil.execute_command(close_command, com_serial, BusinessConstant.LOGGER, is_hex=True,is_log_time=True)
                        flash_num = 0
                elif BusinessConstant.ALARM_LIGHT == AlarmLightEnum.RED_LIGHT_FLASH:  # 红闪
                    if flash_num % 2 == 0:
                        red_command = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF F0 10 00 AA BB"
                        result = BusinessUtil.execute_command(red_command, com_serial, BusinessConstant.LOGGER, is_hex=True,is_log_time=True)
                        flash_num = 1
                    else:
                        close_command = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 00 00 AA BB"
                        result = BusinessUtil.execute_command(close_command, com_serial, BusinessConstant.LOGGER, is_hex=True,is_log_time=True)
                        flash_num = 0
                elif BusinessConstant.ALARM_LIGHT == AlarmLightEnum.GREEN_LIGHT_FLASH:  # 绿闪
                    if flash_num % 2 == 0:
                        green_command = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 FF 00 AA BB"
                        result = BusinessUtil.execute_command(green_command, com_serial, BusinessConstant.LOGGER, is_hex=True, is_log_time=True)
                        flash_num = 1
                    else:
                        close_command = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 00 00 AA BB"
                        result = BusinessUtil.execute_command(close_command, com_serial, BusinessConstant.LOGGER, is_hex=True, is_log_time=True)
                        flash_num = 0
                elif BusinessConstant.ALARM_LIGHT == AlarmLightEnum.GREEN_LIGHT:
                    if WFState.get_battery_state() == "charging":  # 绿闪
                        if flash_num % 2 == 0:
                            green_command = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 FF 00 AA BB"
                            result = BusinessUtil.execute_command(green_command, com_serial, BusinessConstant.LOGGER, is_hex=True,is_log_time=True)
                            flash_num = 1
                        else:
                            close_command = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 00 00 AA BB"
                            result = BusinessUtil.execute_command(close_command, com_serial, BusinessConstant.LOGGER, is_hex=True,is_log_time=True)
                            flash_num = 0
                    else:  # 正常颜色
                        green_command = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 FF 00 AA BB"
                        result = BusinessUtil.execute_command(green_command, com_serial, BusinessConstant.LOGGER, is_hex=True,is_log_time=True)
                        flash_num = 0
                # 结果异常，一般为串口没有连接
                if result == BusinessConstant.ERROR:
                    break
                time.sleep(1)
            # BusinessConstant.LOGGER.get_log().info(f"[AlarmLight.open_light_thread]警示灯打开-结束,返回值为:{result}")
            print(f"[AlarmLight.open_light_thread]警示灯打开-结束,,灯颜色为:{BusinessConstant.ALARM_LIGHT},返回值为:{result}")
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[AlarmLight.open_light_thread]警示灯打开-异常，异常信息为:{ex}")
        finally:
            BusinessUtil.close_serial(com_serial, BusinessConstant.LOGGER)
        time.sleep(10)


def open_red_light():
    """
    有异常显示红色
    """
    com_serial = None
    try:
        print(f"[AlarmLight.open_red_light]打开红灯-开始")
        com_serial = ComSerial.get_com_serial(BusinessConstant.USB_ALARM_LIGHT)
        BusinessUtil.open_serial(com_serial, BusinessConstant.LOGGER)
        red_command1 = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF FF 00 00 AA BB"
        result1 = BusinessUtil.execute_command(red_command1, com_serial, BusinessConstant.LOGGER, is_hex=True)
        result1 = result1.replace("\r\n", "")
        # while True:
        #     if BusinessConstant.IS_OPEN_RED_LIGHT:
        #         red_command1 = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF FF 00 00 AA BB"
        #         result1 = BusinessUtil.execute_command(red_command1, com_serial, BusinessConstant.LOGGER, is_hex=True)
        #         result1 = result1.replace("\r\n", "")
        #         time.sleep(1)
        #         close_command2 = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 00 00 AA BB"
        #         result2 = BusinessUtil.execute_command(close_command2, com_serial, BusinessConstant.LOGGER, is_hex=True)
        #         result2 = result2.replace("\r\n", "")
        #         time.sleep(1)
        #     else:
        #         break
        # red_command2 = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF FF 00 00 AA BB"
        # result2 = BusinessUtil.execute_command(red_command2, com_serial, BusinessConstant.LOGGER, is_hex=True)
        # result2 = result2.replace("\r\n", "")
        print(f"[AlarmLight.open_red_light]打开红灯-结束,返回值为:{result1}")
        BusinessConstant.LOGGER.get_log().info(f"[AlarmLight.open_red_light]打开红灯-结束,返回值为:{result1}")
        if result1 is not None and result1 == "RecvEndDisplayEnd":
            result = BusinessConstant.SUCCESS
        else:
            result = BusinessConstant.ERROR
    except Exception as ex:
        print(f"[AlarmLight.open_red_light]打开红灯-异常，异常信息为:{ex}")
        BusinessConstant.LOGGER.get_log().info(f"[AlarmLight.open_red_light]打开红灯-异常，异常信息为:{ex}")
        return BusinessConstant.ERROR
    finally:
        BusinessUtil.close_serial(com_serial, BusinessConstant.LOGGER)


def open_yellow_light():
    """
    正在执行显示黄灯
    """
    com_serial = None
    try:
        print(f"[AlarmLight.open_yellow_light]打开黄灯-开始")
        com_serial = ComSerial.get_com_serial(BusinessConstant.USB_ALARM_LIGHT)
        BusinessUtil.open_serial(com_serial, BusinessConstant.LOGGER)
        yellow_command1 = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF CC F0 00 AA BB"
        result1 = BusinessUtil.execute_command(yellow_command1, com_serial, BusinessConstant.LOGGER, is_hex=True)
        result1 = result1.replace("\r\n", "")
        # while True:
        #     if BusinessConstant.IS_OPEN_YELLOW_LIGHT:
        #         yellow_command1 = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF CC F0 00 AA BB"
        #         result1 = BusinessUtil.execute_command(yellow_command1, com_serial, BusinessConstant.LOGGER, is_hex=True)
        #         result1 = result1.replace("\r\n", "")
        #         time.sleep(1)
        #         close_command2 = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 00 00 AA BB"
        #         result2 = BusinessUtil.execute_command(close_command2, com_serial, BusinessConstant.LOGGER, is_hex=True)
        #         result2 = result2.replace("\r\n", "")
        #         time.sleep(1)
        #     else:
        #         break
        # yellow_command2 = "DD 55 EE 00 02 00 01 00 99 01 00 00 00 03 00 FF CC F0 00 AA BB"
        # result2 = BusinessUtil.execute_command(yellow_command2, com_serial, BusinessConstant.LOGGER, is_hex=True)
        # result2 = result2.replace("\r\n", "")
        print(f"[AlarmLight.open_yellow_light]打开黄灯-结束,返回值为:{result1}")
        BusinessConstant.LOGGER.get_log().info(f"[AlarmLight.open_yellow_light]打开黄灯-结束,返回值为:{result1}")
        if result1 is not None and result1 == "RecvEndDisplayEnd":
            result = BusinessConstant.SUCCESS
        else:
            result = BusinessConstant.ERROR
        return result
    except Exception as ex:
        print(f"[AlarmLight.open_yellow_light]打开黄灯-异常，异常信息为:{ex}")
        BusinessConstant.LOGGER.get_log().info(f"[AlarmLight.open_yellow_light]打开黄灯-异常，异常信息为:{ex}")
        return BusinessConstant.ERROR
    finally:
        BusinessUtil.close_serial(com_serial, BusinessConstant.LOGGER)


def open_green_light():
    """
    正常显示绿灯
    """
    com_serial = None
    try:
        print(f"[AlarmLight.open_green_light]打开绿灯-开始")
        com_serial = ComSerial.get_com_serial(BusinessConstant.USB_ALARM_LIGHT)
        BusinessUtil.open_serial(com_serial, BusinessConstant.LOGGER)
        green_command1 = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 FF 00 AA BB"
        result1 = BusinessUtil.execute_command(green_command1, com_serial, BusinessConstant.LOGGER, is_hex=True)
        result1 = result1.replace("\r\n", "")
        # while True:
        #     if BusinessConstant.IS_OPEN_GREEN_LIGHT:
        #         green_command1 = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 FF 00 AA BB"
        #         result1 = BusinessUtil.execute_command(green_command1, com_serial, BusinessConstant.LOGGER, is_hex=True)
        #         result1 = result1.replace("\r\n", "")
        #         time.sleep(1)
        #         close_command2 = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 00 00 AA BB"
        #         result2 = BusinessUtil.execute_command(close_command2, com_serial, BusinessConstant.LOGGER, is_hex=True)
        #         result2 = result2.replace("\r\n", "")
        #         time.sleep(1)
        #     else:
        #         break

        # green_command2 = "DD 55 EE 00 02 00 01 00 99 01 00 00 00 03 00 FF 00 FF 00 AA BB"
        # result2 = BusinessUtil.execute_command(green_command2, com_serial, BusinessConstant.LOGGER, is_hex=True)
        # result2 = result2.replace("\r\n", "")
        print(f"[AlarmLight.open_green_light]打开绿灯-结束,返回值为:{result1}")
        BusinessConstant.LOGGER.get_log().info(f"[AlarmLight.open_green_light]打开绿灯-结束,返回值为:{result1}")
        if result1 is not None and result1 == "RecvEndDisplayEnd":
            result = BusinessConstant.SUCCESS
        else:
            result = BusinessConstant.ERROR
        return result
    except Exception as ex:
        print(f"[AlarmLight.open_green_light]打开绿灯-异常,常信息为:{ex}")
        BusinessConstant.LOGGER.get_log().info(f"[AlarmLight.open_green_light]打开绿灯-异常,常信息为:{ex}")
        return BusinessConstant.ERROR
    finally:
        BusinessUtil.close_serial(com_serial, BusinessConstant.LOGGER)


def close_light():
    """
    不显示亮灯
    """
    com_serial = None
    try:
        print(f"[AlarmLight.close_light]关闭灯带-开始")
        com_serial = ComSerial.get_com_serial(BusinessConstant.USB_ALARM_LIGHT)
        BusinessUtil.open_serial(com_serial, BusinessConstant.LOGGER)
        close_command1 = "DD 55 EE 00 00 00 01 00 99 01 00 00 00 03 00 FF 00 00 00 AA BB"
        result1 = BusinessUtil.execute_command(close_command1, com_serial, BusinessConstant.LOGGER, is_hex=True)
        result1 = result1.replace("\r\n", "")
        # close_command2 = "DD 55 EE 00 02 00 01 00 99 01 00 00 00 03 00 FF 00 00 00 AA BB"
        # result2 = BusinessUtil.execute_command(close_command2, com_serial, BusinessConstant.LOGGER, is_hex=True)
        # result2 = result2.replace("\r\n", "")
        print(f"[AlarmLight.close_light]关闭灯带-结束,返回值为:{result1}")
        # 关闭灯带线程
        BusinessConstant.ALARM_LIGHT = AlarmLightEnum.STOP_LIGHT
        BusinessConstant.LOGGER.get_log().info(f"[AlarmLight.close_light]关闭灯带-结束,返回值为:{result1}")
        if result1 is not None and result1 == "RecvEndDisplayEnd":
            result = BusinessConstant.SUCCESS
        else:
            result = BusinessConstant.ERROR
        return result
    except Exception as ex:
        print(f"[AlarmLight.close_light]关闭灯带-异常,常信息为:{ex}")
        BusinessConstant.LOGGER.get_log().info(f"[AlarmLight.close_light]关闭灯带-异常,常信息为:{ex}")
        return BusinessConstant.ERROR
    finally:
        BusinessUtil.close_serial(com_serial, BusinessConstant.LOGGER)


if __name__ == '__main__':
    # while True:
    #     open_green_light()
    #     time.sleep(20)
    #     open_yellow_light()
    #     time.sleep(20)
    #     open_red_light()
    #     time.sleep(20)
    #     close_light()
    #     time.sleep(20)
    threading.Thread(target=open_light_thread,args=()).start()
    while True:
        time.sleep(6)
        BusinessConstant.ALARM_LIGHT = AlarmLightEnum.YELLOW_LIGHT_FLASH
        time.sleep(6)
        BusinessConstant.ALARM_LIGHT = AlarmLightEnum.RED_LIGHT_FLASH
        time.sleep(6)
        WFState.set_battery_state("charging")
        BusinessConstant.ALARM_LIGHT = AlarmLightEnum.GREEN_LIGHT
        time.sleep(6)
        WFState.set_battery_state("standby")
        BusinessConstant.ALARM_LIGHT = AlarmLightEnum.GREEN_LIGHT

