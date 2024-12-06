from BASEUtile.DeviceEnum import BaseDeviceEnum, DeviceEnum
import serial
import BASEUtile.DeviceConstant as DeviceConstant
import BASEUtile.BusinessUtil as BusinessUtil
import threading
import time
import BASEUtile.BusinessConstant as BusinessConstant
import binascii
from BASEUtile.logger import Logger

logger = Logger(__name__)


def _monitor_serial():
    """
    监控串口连接情况，如果断联，重新连接
    """
    while True:
        time.sleep(DeviceConstant.DEVICE_RECONNECTION_TIME)
        for v in BaseDeviceEnum:
            try:
                if DeviceConstant.COMMON_SERIAL_MAP.get(v.name) is None:
                    serial_device = serial.Serial(
                        port=dict(v.value).get(DeviceConstant.PORT),
                        timeout=dict(v.value).get(DeviceConstant.TIMEOUT),
                        baudrate=dict(v.value).get(DeviceConstant.BPS),
                        parity=dict(v.value).get(DeviceConstant.PARITY),
                        stopbits=dict(v.value).get(DeviceConstant.STOPBITS),
                        bytesize=dict(v.value).get(DeviceConstant.BYTESIZE))
                    if not serial_device.isOpen():
                        serial_device.open()
                    # 串口对象字典表
                    DeviceConstant.COMMON_SERIAL_MAP[v.name] = serial_device
                    # 命令字典表
                    DeviceConstant.COMMON_COMMAND_LIST_MAP[v.name] = []
                    threading.Thread(target=_deal_command, args=(v.name,)).start()
                    # 命令返回值字典表
                    DeviceConstant.COMMON_COMMAND_RETURN_MAP[v.name] = []
                    # 建立该串口命令处理线程
                    threading.Thread(target=_deal_command, args=(v.name,)).start()
                    # 业务驱动被占用字典表{KEY,{IS_USED:True,IS_WAITING:False}}
                    DeviceConstant.COMMON_SERIAL_USED_MAP[v.name] = {DeviceConstant.IS_USED: False,
                                                                     DeviceConstant.IS_WAITING: False}
                    logger.get_log().info(f"串口{dict(v.value).get(DeviceConstant.PORT)}，重新连接成功")
                else:
                    print(f"重新打开串口{v.name}，{DeviceConstant.COMMON_SERIAL_MAP[v.name].isOpen()}")
                    if not DeviceConstant.COMMON_SERIAL_MAP[v.name].isOpen():
                        print(f"重新打开串口{v.name}成功")
                        DeviceConstant.COMMON_SERIAL_MAP[v.name].open()
            except Exception as e:
                logger.get_log().info(f"串口{dict(v.value).get(DeviceConstant.PORT)}重新连接失败，{str(e)}")


def _deal_command_thread():
    """
    每个串口命令启动一个线程进行命令的处理
    """
    # DeviceConstant.COMMON_COMMAND_LIST = {"1": "dd", "2": "dd2", "3": "dd3"}
    for key in DeviceConstant.COMMON_COMMAND_LIST_MAP.keys():
        print("循环驱动开启线程，驱动关键字：" + key)
        threading.Thread(target=_deal_command, args=(key,)).start()


def _insert_command_priority(device_enum: DeviceEnum, command, command_priority: int):
    """
    命令放入消息列表中{DEVICE1:[{device_map:驱动分类,command:消息,priority:优先级]},}
    """
    # 获取驱动key
    device_name = dict(device_enum.value).get(DeviceConstant.DEVICE_NAME)
    common_serial_used_map = DeviceConstant.COMMON_SERIAL_USED_MAP.get(device_name)
    if common_serial_used_map is None:
        logger.get_log().info(f"_insert_command_priority操控命令:{command}，无法下发到{device_name}串口中，该串口没有初始化打开！")
        return BusinessConstant.ERROR
    else:
        # 根据业务判断是否有需要占用串口
        is_used = common_serial_used_map[DeviceConstant.IS_USED]
        is_waiting = common_serial_used_map[DeviceConstant.IS_WAITING]
        if is_used is True or is_waiting is True:
            logger.get_log().info(f"_insert_command_priority操控命令:{command}，无法下发到{device_name}串口中，该串口被占用！")
            return BusinessConstant.BUSY
    # 向消息列表中放入消息,包括驱动信息和处理命令
    common_command_list = DeviceConstant.COMMON_COMMAND_LIST_MAP.get(device_name)
    print(f"_insert_command_priority操控指令{command},当前命令列表{common_command_list}")
    # 判断命令优先级-如果列表中有1个一级命令，则不能在加一级命令，如果有二级命令，把二级命令清除，换成一级命令
    if len(common_command_list) == 0:
        common_command_list.append({DeviceConstant.DEVICE_MAP: device_enum.value,
                                    DeviceConstant.COMMAND: command,
                                    DeviceConstant.COMMAND_PRIORITY: command_priority})
        return BusinessConstant.SUCCESS
    else:
        for common_command in common_command_list:
            temp_command_priority = common_command.get(DeviceConstant.COMMAND_PRIORITY)
            # 如果列表中当前有一级命令，则不能添加一级命令
            if temp_command_priority == DeviceConstant.COMMAND_PRIORITY_FIRST:
                return BusinessConstant.BUSY
            else:  # 如果列表中当前有二级命令，则判断当前命令为一级命令则添加进去，二级清除，如果当前二级命令，请返回
                if command_priority == DeviceConstant.COMMAND_PRIORITY_FIRST:
                    # 删除二级命令
                    common_command_list.remove(common_command)
                    # 并设置二级命令返回值为BUSY
                    DeviceConstant.COMMON_COMMAND_RETURN_MAP[device_name].append(
                        common_command.get(DeviceConstant.COMMAND) + BusinessConstant.BUSY)
                    common_command_list.append({DeviceConstant.DEVICE_MAP: device_enum.value,
                                                DeviceConstant.COMMAND: command,
                                                DeviceConstant.COMMAND_PRIORITY: command_priority})
                    return BusinessConstant.SUCCESS
                else:
                    return BusinessConstant.BUSY

    # # 判断命令的优先级-允许有多个命令排队
    # row_num = 0
    # if command_priority == DeviceConstant.COMMAND_PRIORITY_FIRST:
    #     if len(common_command_list) == 0:
    #         common_command_list.append({DeviceConstant.DEVICE_MAP: device_enum.value,
    #                                     DeviceConstant.COMMAND: command,
    #                                     DeviceConstant.COMMAND_PRIORITY: command_priority})
    #     else:
    #         for common_command in common_command_list:
    #             # 如果列表中有二级，则一级插入到二级之前
    #             temp_command_priority = common_command.get(DeviceConstant.COMMAND_PRIORITY)
    #             if temp_command_priority == DeviceConstant.COMMAND_PRIORITY_SECOND:
    #                 common_command_list.insert(row_num, {DeviceConstant.DEVICE_MAP: device_enum.value,
    #                                                      DeviceConstant.COMMAND: command,
    #                                                      DeviceConstant.COMMAND_PRIORITY: command_priority})
    #                 break
    #             row_num = row_num + 1
    #             # 没有二级则添加到最后
    #             if row_num == len(common_command_list):
    #                 common_command_list.append(
    #                     {DeviceConstant.DEVICE_MAP: device_enum.value, DeviceConstant.COMMAND: command,
    #                      DeviceConstant.COMMAND_PRIORITY: command_priority})
    #                 break
    # else:
    #     common_command_list.append(
    #         {DeviceConstant.DEVICE_MAP: device_enum.value, DeviceConstant.COMMAND: command,
    #          DeviceConstant.COMMAND_PRIORITY: command_priority})


def _deal_command(key):
    """
    串口命令处理
    """
    while True:
        try:
            print(
                f"_deal_command开始时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())},当前线程{threading.currentThread().name}")
            # 待处理命令
            common_command_list = DeviceConstant.COMMON_COMMAND_LIST_MAP.get(key)
            print(f"_deal_command待处理所有命令{key}：{common_command_list}")
            if len(common_command_list) == 0:
                time.sleep(DeviceConstant.COMMAND_INTERVAL_TIME)
                continue
            # 获取对应的串口对象
            common_serial = DeviceConstant.COMMON_SERIAL_MAP.get(key)
            if not common_serial.isOpen():
                common_serial.open()
            # 处理消息队列
            while len(common_command_list) > 0:
                common_command = common_command_list[0]
                # 串口属性对比更新
                device_map = dict(dict(common_command).get(DeviceConstant.DEVICE_MAP))
                if common_serial.timeout != device_map.get(DeviceConstant.TIMEOUT):
                    common_serial.timeout = device_map.get(DeviceConstant.TIMEOUT)
                if common_serial.baudrate != device_map.get(DeviceConstant.BPS):
                    common_serial.baudrate = device_map.get(DeviceConstant.BPS)
                if common_serial.parity != device_map.get(DeviceConstant.PARITY):
                    common_serial.parity = device_map.get(DeviceConstant.PARITY)
                if common_serial.stopbits != device_map.get(DeviceConstant.STOPBITS):
                    common_serial.stopbits = device_map.get(DeviceConstant.STOPBITS)
                if common_serial.bytesize != device_map.get(DeviceConstant.BYTESIZE):
                    common_serial.bytesize = device_map.get(DeviceConstant.BYTESIZE)
                # 执行命令
                command = dict(common_command).get(DeviceConstant.COMMAND)
                logger.get_log().info(f"_deal_command执行命令,命令:{command}")
                result = BusinessUtil.execute_command(command, common_serial, logger)
                # 执行结果放入结果字典表中
                # print(f"deal_command返回值拼接前缀后结果：{DEVICE1:[command + result,]}")
                DeviceConstant.COMMON_COMMAND_RETURN_MAP[key].append(command + result)
                # 处理完成后进行删除
                common_command_list.remove(common_command)
            print(f"_deal_command结束时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        except Exception as e:
            logger.get_log().info(f"执行命令异常_deal_command,异常信息,{str(e)}")
            # 执行结果放入结果字典表中
            DeviceConstant.COMMON_COMMAND_RETURN_MAP[key].append(command + BusinessConstant.ERROR)
            # 清空信息列表
            common_command_list.clear()
            # 关闭串口，重新插入才能好用
            common_serial.close()


def init_device():
    """
    初始化驱动信息
    """
    # com口驱动
    for v in BaseDeviceEnum:
        try:
            serial_device = serial.Serial(
                port=dict(v.value).get(DeviceConstant.PORT),
                timeout=dict(v.value).get(DeviceConstant.TIMEOUT),
                baudrate=dict(v.value).get(DeviceConstant.BPS),
                parity=dict(v.value).get(DeviceConstant.PARITY),
                stopbits=dict(v.value).get(DeviceConstant.STOPBITS),
                bytesize=dict(v.value).get(DeviceConstant.BYTESIZE))
            if not serial_device.isOpen():
                serial_device.open()
            # 串口对象字典表
            DeviceConstant.COMMON_SERIAL_MAP[v.name] = serial_device
            # 命令字典表
            DeviceConstant.COMMON_COMMAND_LIST_MAP[v.name] = []
            # 命令返回值字典表
            DeviceConstant.COMMON_COMMAND_RETURN_MAP[v.name] = []
        except Exception as e:
            logger.get_log().info(f"串口{dict(v.value).get(DeviceConstant.PORT)}初始化失败，{str(e)}")
    # 开启处理消息线程,一个串口一个线程
    _deal_command_thread()
    # 开启出口监控线程，如果有串口重连，需要初始化该串口
    threading.Thread(target=_monitor_serial, args=()).start()


# def execute_command(device_enum: DeviceEnum, command, command_priority: int = DeviceConstant.COMMAND_PRIORITY_FIRST):
#     """
#     执行命令
#     """
#     # 将命令插入到消息列表中
#     result = _insert_command_priority(device_enum, command, command_priority)
#     if result != BusinessConstant.SUCCESS:
#         return result
#     # 获取返回值,返回列表中根据规则获取返回值,返回值是自定义以command开头的
#     device_name = dict(device_enum.value).get(DeviceConstant.DEVICE_NAME)
#     command_return_overtime = 0
#     while True:
#         common_command_return_list = DeviceConstant.COMMON_COMMAND_RETURN_MAP.get(device_name)
#         # print(f"execute_command结果列表：{common_command_return_list}")
#         for common_command_return in common_command_return_list:
#             is_exist = common_command_return.startswith(command, 0, len(command))
#             if is_exist:
#                 common_command_return_list.remove(common_command_return)
#                 # print(f"execute_command返回结果值：{common_command_return.replace(command, '', 1)}")
#                 return common_command_return.replace(command, "", 1)
#         time.sleep(0.1)
#         command_return_overtime = command_return_overtime + 0.1
#         if command_return_overtime > DeviceConstant.COMMAND_RETURN_OVERTIME:
#             return BusinessConstant.OVERTIME


def execute_command_hex(device_enum: DeviceEnum, command,
                        command_priority: int = DeviceConstant.COMMAND_PRIORITY_FIRST):
    """
    执行命令,返回值为十六进制
    """
    # 获取返回值,返回列表中根据规则获取返回值,返回值是自定义以command开头的
    device_name = dict(device_enum.value).get(DeviceConstant.DEVICE_NAME)
    # 将命令插入到消息列表中
    result = _insert_command_priority(device_enum, command, command_priority)
    if result != BusinessConstant.SUCCESS:
        return result
    # 返回值超时
    command_return_overtime = 0
    while True:
        common_command_return_list = DeviceConstant.COMMON_COMMAND_RETURN_MAP.get(device_name)
        # print(f"execute_command结果列表：{common_command_return_list}")
        for common_command_return in common_command_return_list:
            is_exist = common_command_return.startswith(command, 0, len(command))
            if is_exist:
                common_command_return_list.remove(common_command_return)
                # print(f"execute_command返回结果值：{common_command_return.replace(command, '', 1)}")
                return common_command_return.replace(command, "", 1)
        time.sleep(0.1)
        command_return_overtime = command_return_overtime + 0.1
        if command_return_overtime > DeviceConstant.COMMAND_RETURN_OVERTIME:
            return BusinessConstant.OVERTIME


def execute_command(device_enum: DeviceEnum, command, command_priority: int = DeviceConstant.COMMAND_PRIORITY_FIRST):
    """
    执行命令,返回值为二进制
    """
    result = execute_command_hex(device_enum, command, command_priority)
    if result == BusinessConstant.ERROR or result == BusinessConstant.BUSY or result == BusinessConstant.OVERTIME:
        return result
    else:
        # 十六进制字符串转换为二进制字符串，还原返回值
        result = binascii.a2b_hex(result.encode('ascii')).decode('ascii')
        return result


def test_job():
    while True:
        ret = execute_command(DeviceEnum.DEVICE_AIR_CONDITION, "0D 02 00 07 00 01 08 C7",
                              DeviceConstant.COMMAND_PRIORITY_SECOND)
        # ret = execute_command(DeviceEnum.DEVICE_AIR_CONDITION, "ttttt",
        #                       DeviceConstant.COMMAND_PRIORITY_FIRST)

        print(f"test_job返回值：{ret}")
        time.sleep(1)


if __name__ == '__main__':
    logger = Logger(__name__)  # 日志记录
    init_device(logger)
    print("main开启空调")
    ret = execute_command(DeviceEnum.DEVICE_AIR_CONDITION, "0D 06 00 2f 00 01 79 0F",
                          DeviceConstant.COMMAND_PRIORITY_FIRST)
    print(f"main返回值1：{ret}")
    # ret = execute_command(DeviceEnum.DEVICE_AIR_CONDITION, "ttttt",
    #                       DeviceConstant.COMMAND_PRIORITY_FIRST)
    th = threading.Thread(target=test_job, args=())
    th.start()

    print(f"main返回值2：{ret}")

    # time.sleep(6)
    print("main关闭空调")

    ret = execute_command(DeviceEnum.DEVICE_AIR_CONDITION, "0D 06 00 2f 00 00 B8 CF",
                          DeviceConstant.COMMAND_PRIORITY_FIRST)
    print(f"main返回值：{ret}")

    # list = [{"a1": "b1"}, {"a2": "b2"}, {"a3": "b3"}, {"a4": "b4"}]
    # list.append({"a5": "b5"})
    #
    # print(len(list))
    #
    # while len(list) > 0:
    #     a = list[0]
    #     print(a)
    #     list.remove(a)
    #
    # print(list)

    # common_command_list = [{"device_map": "d", "command": "c", "priority": 1},
    #                        {"device_map": "d1", "command": "c1", "priority": 1},
    #                        {"device_map": "d2", "command": "c2", "priority": 1}]
    # row_num = 0
    # for common_command in common_command_list:
    #     # 如果列表中有二级，则一级插入到二级之前
    #     temp_command_priority = common_command.get(DeviceConstant.COMMAND_PRIORITY)
    #     print(f"----{temp_command_priority},{common_command}")
    #     if temp_command_priority == DeviceConstant.COMMAND_PRIORITY_SECOND:
    #         common_command_list.insert(row_num, {DeviceConstant.DEVICE_MAP: "dd",
    #                                              DeviceConstant.COMMAND: "cc",
    #                                              DeviceConstant.COMMAND_PRIORITY: 1})
    #         break
    #     row_num = row_num + 1
    #     # 没有二级则添加到最后
    #     if row_num == len(common_command_list):
    #         common_command_list.append(
    #             {DeviceConstant.DEVICE_MAP: "d3", DeviceConstant.COMMAND: "c3",
    #              DeviceConstant.COMMAND_PRIORITY: 1})
    #         break
    #
    # print(common_command_list)

    # command = "123456"
    # common_command_return = "12345678912345678"
    # print(common_command_return.replace(command))
    # i = common_command_return.find(command, 0, len(common_command_return))
    # print(i)
    pass
