import time
import serial
import BASEUtile.BusinessConstant as BusinessConstant
import binascii
import datetime
import time
from flask import Response
import json


def execute_command_hex(command, com_serial: serial.Serial, logger, is_hex=True, byte_size=0,is_log_time=False):
    """
    执行命令：返回结果为16进制字符串,没有空格
    """
    try:
        com_serial.flushOutput()
        com_serial.flushInput()
        print(f"[BusinessUtil.execute_command_hex]串口为{com_serial},命令位{command},是否16进制{is_hex},读取字节数{byte_size}")
        # 测试
        test_count = com_serial.inWaiting()
        if test_count == 0:
            logger.get_log().debug(
                f"[BusinessUtil.execute_command_hex]开始写入数据之前，缓存里没有数据")
        else:
            test_data = com_serial.read(test_count)
            logger.get_log().debug(
                f"[BusinessUtil.execute_command_hex]开始写入数据之前，缓存里有数据，数据内容为{test_data}")

        # 判断是否为16进制
        if is_hex is False:
            ret = com_serial.write(command.encode('ascii'))
        else:
            ret = com_serial.write(bytes.fromhex(command))
        logger.get_log().debug(f"[BusinessUtil.execute_command_hex]命令为{command},write返回结果为{ret}")
        # 读取数据
        result = BusinessConstant.ERROR
        if byte_size == 0:
            time.sleep(0.2)
            count = com_serial.inWaiting()
            if count == 0:
                log_info(logger,f"[BusinessUtil.execute_command_hex]执行命令为:{command},写入字节数为:{ret},读取通道返回值字节数为:{count}",is_log_time)
                # logger.get_log().info(
                #     f"[BusinessUtil.execute_command_hex]执行命令为:{command},写入字节数为:{ret},读取通道返回值字节数为:{count}")
                return BusinessConstant.ERROR
            else:
                data = com_serial.read(count)
        else:
            data = com_serial.read(byte_size)
        # 数据的转换
        result = binascii.hexlify(data).decode('ascii')  # 二进制ascii字节串转换为16进制字符串
        # logger.get_log().info(
        #     f"[BusinessUtil.execute_command_hex]执行命令为:{command},写入字节数为:{ret},读取通道返回值字节为:{data},转换字符串后为:{result}")
        log_info(logger, f"[BusinessUtil.execute_command_hex]执行命令为:{command},写入字节数为:{ret},读取通道返回值字节为:{data},转换字符串后为:{result}",
                 is_log_time)
        com_serial.flushOutput()
        com_serial.flushInput()  # 清除缓存区数据,当代码在循环中执行时，不加这句代码会造成count累加
    except Exception as ex:
        # logger.get_log().info(f"[BusinessUtil.execute_command_hex]执行命令为:{command},读取数据异常,异常信息:{str(ex)}")
        log_info(logger, f"[BusinessUtil.execute_command_hex]执行命令为:{command},读取数据异常,异常信息:{str(ex)}", is_log_time)
        return BusinessConstant.ERROR
    return result


def execute_command(command, com_serial: serial.Serial, logger, is_hex=True, byte_size=0,is_log_time=False):
    """
    执行命令：返回结果为2进制字符串ASCII,没有空格
    """
    result = execute_command_hex(command, com_serial, logger, is_hex=is_hex, byte_size=byte_size,is_log_time=is_log_time)
    if result == BusinessConstant.ERROR:
        return BusinessConstant.ERROR
    else:
        return binascii.unhexlify(result).decode('ascii')


def log_info(logger,log_info,is_log_time):
    """
    执行log,log间隔次数
    """
    if is_log_time is True:
        if BusinessConstant.LOG_TIME_INIT % BusinessConstant.LOG_TIME_ALL == 0:
            logger.get_log().info(log_info)
            BusinessConstant.LOG_TIME_INIT = 1
        else:
            BusinessConstant.LOG_TIME_INIT = BusinessConstant.LOG_TIME_INIT + 1
    else:
        logger.get_log().info(log_info)


def open_serial(com_serial: serial.Serial, logger):
    try:
        if com_serial is not None and com_serial.is_open:
            com_serial.close()
            time.sleep(0.1)
        if com_serial is not None:
            com_serial.open()
            time.sleep(0.1)  # 此处等待一下,有的串口打开后直接执行数据不会回来
    except Exception as ex:
        logger.get_log().info(f"[BusinessUtil.open_serial]打开串口异常,异常信息:{str(ex)}")


def close_serial(com_serial: serial.Serial, logger):
    try:
        if com_serial is not None:
            com_serial.close()
            time.sleep(0.1)
    except Exception as ex:
        logger.get_log().info(f"[BusinessUtil.close_serial]关闭串口异常,异常信息:{str(ex)}")


def read_data(com_serial: serial.Serial, logger, byte_size=0):
    """
    读取数据
    """
    result = BusinessConstant.ERROR
    try:
        if byte_size == 0:
            count = com_serial.inWaiting()
            if count == 0:
                logger.get_log().info(f"[BusinessUtil.read_data]读取通道返回值字节数为{count}")
                return BusinessConstant.ERROR
            else:
                data = com_serial.read(count)
        else:
            data = com_serial.read(byte_size)
        # 数据的转换
        result = binascii.b2a_hex(data).decode('ascii')  # 二进制字节串转换为16进制字符串
        logger.get_log().info(f"[BusinessUtil.read_data]读取通道返回值字节为{data},转换字符串后为{result}")
        # time.sleep(0.1)
        # count = com_serial.inWaiting()
        # if count == 0:
        #     result = BusinessConstant.ERROR
        #     logger.get_log().info(f"[BusinessUtil.execute_command]执行命令为{command},读取通道返回值字节数为{count}")
        # if count > 0:
        #     data = com_serial.read(count)
        #     result = binascii.b2a_hex(data).decode('ascii')  # 二进制字节串转换为16进制字符串
        #     logger.get_log().info(f"[BusinessUtil.execute_command]执行命令为{command},读取通道返回值字节为{data},转换字符串后为{result}")
        com_serial.flushOutput()
        com_serial.flushInput()  # 清除缓存区数据,当代码在循环中执行时，不加这句代码会造成count累加
    except Exception as ex:
        logger.get_log().info(f"[BusinessUtil.read_data]读取数据异常,异常信息:{str(ex)}")
    return result


# def execute_command(command, com_serial: serial.Serial, logger):
#     """
#     执行命令
#     """
#     if not com_serial.isOpen():
#         com_serial.open()
#     command = command + "\r\n"
#     ret = com_serial.write(command.encode('ascii'))
#     print(f"[BusinessUtil.execute_command]写返回值{ret}")
#     time.sleep(0.1)
#     com_serial.flushOutput()
#     com_serial.flushInput()  # 清除缓存区数据,当代码在循环中执行时，不加这句代码会造成count累加
#     print(f"[businessUtil.execute_command]----返回值{com_serial.inWaiting()}")
#     data = com_serial.read(4)
#     print(f"[businessUtil.execute_command]----返回值{data}")
#     # count = com_serial.inWaiting()
#     # 数据的接收
#     # 可以根据实际情况做修改，比如：当没有响应传回时，等待+判断
#     print(f"BusinessUtil.execute_command串口为{com_serial}")
#     print(f"BusinessUtil.execute_command执行命令为{command}")
#     print(f"BusinessUtil.execute_command读取通道返回值字节数为{count}")
#     # num = 10
#     # while num > 0:
#     #     data = com_serial.read_all()
#     #     logger.get_log().info(f"[BusinessUtil.execute_command]执行命令为{command},读取通道返回值字节为{data}")
#     #     num = num - 1
#     #     time.sleep(1)
#     if count == 0:
#         result = BusinessConstant.ERROR
#         logger.get_log().info(f"[BusinessUtil.execute_command]执行命令为{command},读取通道返回值字节数为{count}")
#     if count > 0:
#         # data = com_serial.read(count)
#         data = com_serial.read(count)
#         # logger.get_log().info(f"[BusinessUtil.execute_command]read_all:{com_serial.read_all()}")
#         # result = bytes.fromhex(hexShow(data))
#         result = data.decode('ascii')  # 二进制字节串转换为16进制字符串
#         logger.get_log().info(f"[BusinessUtil.execute_command]执行命令为{command},读取通道返回值字节为{data}")
#     # com_serial.flushOutput()
#     # com_serial.flushInput()  # 清除缓存区数据,当代码在循环中执行时，不加这句代码会造成count累加
#     # com_serial.close()
#     return result


def hexString_to_int(string):
    """
    16进制字符窜转10进制
    """
    return int.from_bytes(bytes.fromhex(string), byteorder='big')


def get_hex_data_from_serial(hex_string):
    """
    获取16进制数据从串口结果中
    """
    data_len = hexString_to_int(hex_string[4:6])
    print(f"data_len:{data_len}")
    data = hex_string[6:6 + data_len * 2]
    return data


def get_int_data_from_serial(hex_string):
    """
    获取10进制数据从串口结果中
    """
    data_len = hexString_to_int(hex_string[4:6])
    print(f"data_len:{data_len}")
    data = hex_string[6:6 + data_len * 2]
    return hexString_to_int(data)


def string_remove_blank_lower(string):
    """
    去掉空格，并且字母转换为小写
    """
    return string.replace(" ", "").lower()


def reset_write_result(result, command=""):
    """
    com返回结果判断，重新生成。如果返回为空、error、overtime则统一为error，如果返回为busy(串口被占),则返回busy.
    如果需要比较发送的命令是否成功，则比较发送的命令和返回的结果，如果相同，则成功；如果不需要比较，则直接返回结果，参数command不设置即可
    """
    if result is None or result == "":
        return BusinessConstant.ERROR
    elif result == BusinessConstant.ERROR or result == BusinessConstant.OVERTIME:
        return BusinessConstant.ERROR
    elif result == BusinessConstant.BUSY:
        return BusinessConstant.BUSY
    else:
        if command == "":
            return result
        # 共通方法执行完，返回的结果为小写的16进制字符串，所以把发送命令转为小写10进制进行比较，如果发送和接收一样，证明发送成功
        elif string_remove_blank_lower(command) == result:
            return BusinessConstant.SUCCESS
        else:
            return BusinessConstant.ERROR


def reset_read_result(result):
    """
    com返回结果判断，重新生成。如果返回为空、error、overtime则统一为error，如果返回为busy(串口被占),则返回busy。其他则正常返回
    """
    if result is None or result == "":
        return BusinessConstant.ERROR
    elif result == BusinessConstant.ERROR or result == BusinessConstant.OVERTIME:
        return BusinessConstant.ERROR
    elif result == BusinessConstant.BUSY:
        return BusinessConstant.BUSY
    else:
        return result


def int_to_hexByteString(int_data, byte_size):
    """
    将整数转换为16进制字节字符串:如byte_size=2,标准返回是"02 A0"
    """
    hex_data = hex(int_data)[2:].upper()
    result = ""
    for i in range(byte_size):
        if len(hex_data) - (i * 2) < 0:
            result = "00 " + result
        else:
            if len(hex_data) - 2 - (i * 2) < 0:
                temp_result = hex_data[0:len(hex_data) - (i * 2)]
            else:
                temp_result = hex_data[len(hex_data) - 2 - (i * 2):len(hex_data) - (i * 2)]
            if len(temp_result) == 0:
                result = "00 " + result
            elif len(temp_result) == 1:
                result = "0" + temp_result + " " + result
            else:
                result = temp_result + result
    return result


def hex_str_to_bin_str(hex_str, size=8):
    """
    16进制字符串转为换2进制字符串
    """
    bin_str = bin(int(hex_str, 16))[2:]
    return bin_str.zfill(8)


def hex_to_bin_ascii(hex_ascii):
    """
    16机制ASCII码字符转化为2进制ASCII码
    """
    return binascii.unhexlify(hex_ascii).decode('ascii')


def bin_str_to_int(bin_str):
    """
    2进制字符串转换为10进制
    """
    return int(bin_str, 2)

    #     temp_result = hex_data[len(hex_data) - (i+1)*2:len(hex_data)]
    #     if temp_result
    #     byte_size = byte_size - 1
    #
    # if len(hex_data) > byte_size:
    #
    # if len(str(stop_tem_x)) == 1:
    #     stop_tem_x = "00 0" + stop_tem_x
    # elif len(str(stop_tem_x)) == 2:
    #     stop_tem_x = "00 " + stop_tem_x
    # elif len(str(stop_tem_x)) == 3:
    #     stop_tem_x = "0" + str(stop_tem_x)[:1] + " " + str(stop_tem_x)[1:]
    # elif len(str(stop_tem_x)) == 4:
    #     stop_tem_x = str(stop_tem_x)[:2] + " " + str(stop_tem_x)[2:]


def hexShow(argv):
    """
    十六进制去除特殊字符
    """
    hLen = len(argv)
    out_s = ''
    for i in range(hLen):
        out_s = out_s + '{:02X}'.format(argv[i]) + ' '
    return out_s


def get_now_datetime(date_format='%Y-%m-%d %H:%M:%S'):
    if date_format is None:
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.now().strftime(date_format)


def update_system_time(datetime):
    # linux系统
    import os
    pwd = BusinessConstant.SYSTEM_PWD
    # os.system(f"date -s '{time_value}'")
    os.system(f"echo {pwd} | sudo -S date -s '{datetime}'")


def get_success_response(data=""):
    """
    返回成功信息
    """
    response = {
        "code": BusinessConstant.SUCCESS_CODE,
        "message": BusinessConstant.SUCCESS,
        "data": data
    }
    print(response)
    return Response(json.dumps(response), mimetype='application/json')


def get_error_response(data=""):
    """
    返回异常信息
    """
    response = {
        "code": BusinessConstant.ERROR_CODE,
        "message": BusinessConstant.ERROR,
        "data": data
    }
    return Response(json.dumps(response), mimetype='application/json')


def return_message_json_str(code, message="", data=None):
    return json.dumps({"code": code, "message": message, "data": data}, ensure_ascii=False)


def return_message_dict(code, message="", data=None):
    return {"code": code, "message": message, "data": data}


if __name__ == '__main__':
    # init_device()
    # print(common_serial)

    # DeviceUtil.init_device()
    # print(DeviceConstant.COMMON_COMMAND_LIST)

    print(datetime.datetime.now())
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(int_to_hexByteString(672, 2))
    print(hexString_to_int("6CC6"))
    print(get_hex_data_from_serial("010203030102301231"))
    print(get_int_data_from_serial("010201030102301231"))
    # time.strftime("")

    # print(hexShow([12, 23]))
    # print(bytes.fromhex(hexShow([12, 23])))

    # ccon = Config()

    # common_serial['te1'] = BaseDeviceEnum.DEVICE1
    # # common_serial['te2'] = ccon
    # # common_serial.pop("te1")
    #
    # print(dict(common_serial['te1'].value).get("bps"))
    # print(common_serial['te1'].value.get("port"))
    # print(BaseDeviceEnum.DEVICE1.name)
    #
    # for device in BaseDeviceEnum:
    #     print(device.name)
