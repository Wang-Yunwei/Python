# -*- coding: utf-8 -*- 
# @Time : 2021/12/13 12:04 
# @Author : ZKL 
# @File : SATACom.py
# 机库串口通讯，并将机库状态反馈到当前机库内，串口、管理端和控制端应共用一个状态对象实例
# 串口操作类
'''
机库的一些基本操作，包括机库门的开、关；上下、左右推杆的开、关；空调的开、关；及机库的连接状态;
所有机库的命令都是在最后才转化为ascii码，其他均类操作均是字符串处理
结果是获取到的是ascii，然后均转换为字符串，其他类操作都是字符串操作
'''
import time

from BASEUtile.HangerState import HangerState
from BASEUtile.logger import Logger
import serial
import serial.tools.list_ports


class Communication():
    # 初始化
    def __init__(self, com, bps, timeout, logger, parity):
        self.port = com  # 串口类型 ser=serial.Serial("/dev/ttyUSB0",9600,timeout=0.5) #使用USB连接串行口，比特率，连接超时时间（单位为秒）
        self.bps = bps
        self.timeout = timeout
        self.logger = logger
        if parity == None:
            self.parity = serial.PARITY_NONE  # 无校验
        elif parity == 0:
            self.parity = serial.PARITY_ODD  # 偶校验
        elif parity == 1:
            self.parity = serial.PARITY_EVEN  # 奇数校验
        self.parity = serial.PARITY_NONE
        global Ret
        try:
            # 打开串口，并得到串口对象
            # self.main_engine = serial.Serial(self.port, self.bps, timeout=self.timeout, bytesize=8,
            #                                  parity=serial.PARITY_ODD, stopbits=1)
            self.main_engine = serial.Serial(self.port, self.bps, timeout=self.timeout, bytesize=8,
                                             parity=self.parity, stopbits=1)
            # 判断是否打开成功
            if self.main_engine != None and self.main_engine.is_open:
                Ret = True
        except Exception as e:
            self.logger.get_log().info(f"{__name__},串口连接异常")
            self.main_engine = None

    # 打印设备基本信息
    def Print_Name(self):
        print(f"设备名字{self.main_engine.name}")  # 设备名字
        print(f"读或者写端口{self.main_engine.port}")  # 读或者写端口
        print(f"波特率{self.main_engine.baudrate}")  # 波特率
        print(f"字节大小{self.main_engine.bytesize}")  # 字节大小
        print(f"校验位{self.main_engine.parity}")  # 校验位
        print(f"停止位{self.main_engine.stopbits}")  # 停止位
        print(f"读超时设置{self.main_engine.timeout}")  # 读超时设置
        print(f"写超时{self.main_engine.writeTimeout}")  # 写超时
        print(f"软件流控{self.main_engine.xonxoff}")  # 软件流控
        print(f"软件流控{self.main_engine.rtscts}")  # 软件流控
        print(f"硬件流控{self.main_engine.dsrdtr}")  # 硬件流控
        print(f"字符间隔超时{self.main_engine.interCharTimeout}")  # 字符间隔超时

    # 打开串口
    def Open_Engine(self):
        try:
            if self.main_engine != None and self.main_engine.is_open:
                self.main_engine.close()
            if self.main_engine != None:
                self.main_engine.open()
        except Exception as e:
            # self.logger.get_log().info(f"SATACOM--打开串口异常,{e}")
            pass

    # 关闭串口
    def Close_Engine(self):
        try:
            if self.main_engine != None:
                self.main_engine.close()
            # self.logger.get_log().info(self.main_engine.is_open)  # 检验串口是否打开
        except Exception as e:
            # print(f"SATACOM--关闭串口异常,{e}")
            self.logger.get_log().info(f"SATACOM--关闭串口异常,{e}")

    # 打印可用串口列表
    # @staticmethod
    # def Print_Used_Com():
    #     port_list = list(serial.tools.list_ports.comports())
    #     print(port_list)

    # 接收指定大小的数据
    # 从串口读size个字节。如果指定超时，则可能在超时后返回较少的字节；如果没有指定超时，则会一直等到收完指定的字节数。
    def Read_Size(self, size):
        try:
            if self.main_engine != None and self.main_engine.is_open:
                self.main_engine.flushOutput()
                self.main_engine.flushInput()
                # time.sleep(0.1)
                result = self.main_engine.read(size=size)
                # self.main_engine.reset_input_buffer()
                return result
            else:
                return b""
        except Exception as e:
            self.logger.get_log().info(f"SATACOM--读取串口返回固定长度数据异常,{e}")
            return b''

    # 发数据
    def Send_data(self, data):
        try:
            if self.main_engine != None and self.main_engine.is_open:
                self.main_engine.flushInput()
                self.main_engine.flushOutput()
                result = self.main_engine.write(data)
                return result
            else:
                return 0
        except Exception as e:
            self.logger.get_log().info(f"SATACOM--发送串口数据异常,{e}")
            return 0

    # read all data
    def read_all_data(self):
        try:
            if self.main_engine != None and self.main_engine.is_open:
                # time.sleep(0.2)#等待
                return self.main_engine.read_all()
            else:
                return b''
        except Exception as e:
            self.logger.get_log().info(f"SATACOM--读取串口返回所有数据异常,{e}")
            return b''

    # 读取每行数据
    def read_lines(self, lines_num=100):
        try:
            if self.main_engine != None and self.main_engine.is_open:
                return self.main_engine.readlines(lines_num)
            else:
                return b""
        except Exception as e:
            self.logger.get_log().info(f"SATACOM--读取串口所有行数据异常,{e}")
            return b''


class JKSATACOM():
    def __init__(self, hanger_state, device_info, bps, timeout, logger, parity):
        '''
        :param hanger_state: 机库的状态对象实例
        '''
        self.logger = logger
        self.hanger_state = hanger_state
        self.engine = Communication(device_info, bps, timeout, self.logger, parity)  # 5秒超时

    def operator_hanger(self, commond):
        '''
        根据设置的命令格式进行机库的操作
        并将操作后的机库状态进行记录
        :param commond:
        :return:
        '''
        # 发送命令，必须是ascii码
        self.logger.get_log().info(f"上位机发送给串口的命令为{commond}")
        self.engine.Open_Engine()  # 打开串口
        send_back = self.engine.Send_data(commond.encode('ascii'))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        result = ''  # 返回结果
        # 空调特殊处理
        if commond.startswith("30"):
            result = "9300"
            self.engine.Close_Engine()  # 关闭当前连接
            # return result
        elif commond.startswith("31"):
            result = "9310"
            self.engine.Close_Engine()  # 关闭当前连接
            # return result
        else:
            try:
                read_all_date_con = self.engine.Read_Size(4).decode('ascii')
                self.engine.Close_Engine()  # 关闭当前连接
                if read_all_date_con != "" and len(read_all_date_con) >= 4:
                    result = read_all_date_con[:4]  # 读取四个字节
                else:
                    result = ""
                self.logger.get_log().info(f"第一次操作，命令{commond}下位机返回值为：{read_all_date_con},处理后的结果result is {result}")
            except Exception as ex:
                print(f"{ex}")
                return 'error'
        # result = self.engine.Read_Size(4).decode('GB2312')  # 读取四个字节
        return_number = ''
        success_result = ['9000', '9001', '9010', '900a', '900b', '900c', '9011', '9100', '9101', '9110', '9111',
                          '9120', '9121', '9130',
                          '9131', '9140', '9141', '9150', '9151', '914a', '914b', '914c', '915a', '915b', '915c',
                          '92a0', '92a1', '92b0', '92b1', '92c0', '92c1', '92d0', '92d1', '92e0', '92e1', '92f0',
                          '92f1', '92fa', '92fb', '92fc', '92ea', '92eb', '92ec', '9300', '9301', '9310', '9311',
                          '930a', '930b', '930c', '931a', '931b', '931c', '9400', '9401', '940a', '940b', '940c',
                          '9410', '9411', '941a', '941b', '941c', '9500',
                          '9501', '950a', '950b', '950c']
        if result == '' or result not in success_result or result == "9001":  # 超时，没有返回值,当前设备故障；或者别的问题返回错误结果;或者发送命令错误
            # 最多两次失败操作
            time_fail = 0
            while time_fail > 0:
                try:
                    # 发送命令，必须是ascii码
                    if result == "":
                        self.logger.get_log().info(f"下位机返回为空")
                    elif result == "9001":
                        self.logger.get_log().info(f"下位机返回{result}，下位机收到命令错误")
                    else:
                        self.logger.get_log().info(f"下位机结果不在列表，返回结果为：{result}")
                        break
                    self.logger.get_log().info(f"返回为空 or 结果不在列表 or 9001，失败后重新发送给串口的命令为{commond},第{3 - time_fail}次操作")
                    self.engine.Open_Engine()  # 打开串口
                    send_back = self.engine.Send_data(commond.encode('ascii'))
                    read_all_date_con = ""
                    read_all_date_con = self.engine.Read_Size(4).decode('ascii')
                    self.engine.Close_Engine()  # 关闭当前连接
                    self.logger.get_log().info(f"第{3 - time_fail}次操作,下位机返回值为：{read_all_date_con}")
                    if read_all_date_con == "9001":
                        result = read_all_date_con
                        time_fail = time_fail - 1
                        continue
                    if read_all_date_con != "" and len(read_all_date_con) >= 4:
                        result = read_all_date_con[:4]  # 读取四个字节
                        break
                    else:
                        result = read_all_date_con
                        time_fail = time_fail - 1
                except Exception as ex:
                    print(f"{ex}")
                    return 'error'
            if result == "":
                self.hanger_state.set_STAT_connet_state('error')
                self.engine.Close_Engine()  # 关闭当前连接
                self.logger.get_log().error(f"控制板返回参数为空，串口连接超时")
                return '90119021'  # 第一块板子和第二块板子异常’
            else:
                self.hanger_state.set_STAT_connet_state('open')  # 串口连接正常
        else:
            self.hanger_state.set_STAT_connet_state('open')  # 串口连接正常
        if commond.startswith("03"):#下位机版本号
            return result
        if not result[0] == '9':  # 下位机返回结果不正确
            self.logger.get_log().error(f"下位机返回参数不正确，不是以9 or V开头，当前返回值为{result}")
            self.engine.Close_Engine()  # 关闭当前连接
            return 'error'
        else:
            if result == "9001" or result == '9011':
                self.logger.get_log().info(f"最终返回9001或者9002,下位机接收到的命令不识别")
                return "error"
            # 提取后三位数字
            type_num = result[1]
            type_state_num = result[2]
            result_num = result[3]
            print(f"{type_num},{type_state_num},{result_num}")
            if type_num == '0':  # 连接状态
                if type_state_num == '0':  # 第一块板子
                    if result_num == '0':
                        self.hanger_state.set_STAT_connet_state('open')  # 第一块板子串口连接正常
                        return_number = '9000'
                    else:
                        self.hanger_state.set_STAT_connet_state('error')  # 第一块板子串口连接异常
                        return_number = '9001'

                else:  # 第二块板子
                    if result_num == '0':
                        self.hanger_state.set_STAT_connet_state('open')  # 第二块板子串口连接正常
                        return_number = '9010'
                    else:
                        self.hanger_state.set_STAT_connet_state('error')  # 第二块板子串口连接异常
                        return_number = '9011'
            elif type_num == '1':  # 机库门操作
                if type_state_num == '0':  # #左机库门开操作
                    if result_num == '0':  # 机库门打开操作正常
                        self.hanger_state.set_hanger_door('open')  # 打开机库门操作正常
                        return_number = '9100'
                    else:  # 机库门打开操作异常
                        self.hanger_state.set_hanger_door('error')  # 打开机库门操作异常
                        return_number = '9101'
                elif type_state_num == '1':  # #左机库门关闭库门操作
                    if result_num == '0':
                        self.hanger_state.set_hanger_door('close')  # 关闭机库门操作正常
                        return_number = '9110'
                    else:
                        self.hanger_state.set_hanger_door('error')  # 关闭机库门操作异常
                        return_number = '9111'
                elif type_state_num == '2':  # 右机库门开操作
                    if result_num == '0':
                        self.hanger_state.set_hanger_door('open')  # 关闭机库门操作正常
                        return_number = '9120'
                    else:
                        self.hanger_state.set_hanger_door('error')  # 关闭机库门操作异常
                        return_number = '9121'
                elif type_state_num == '3':  # #右机库门关闭库门操作
                    if result_num == '0':
                        self.hanger_state.set_hanger_door('close')  # 关闭机库门操作正常
                        return_number = '9130'
                    else:
                        self.hanger_state.set_hanger_door('error')  # 关闭机库门操作异常
                        return_number = '9131'
                # ---------------同时操作----------------------------------
                elif type_state_num == '4':  # #机库门同时打开操作
                    if result_num == '0':
                        self.hanger_state.set_hanger_door('open')  # 打开机库门操作正常
                        return_number = '9140'
                    else:
                        self.hanger_state.set_hanger_door('error')  # 打开机库门操作异常
                        return_number = '9141'
                elif type_state_num == '5':  # #机库门同时关闭操作
                    if result_num == '0':
                        self.hanger_state.set_hanger_door('close')  # 关闭机库门操作正常
                        return_number = '9150'
                    else:
                        self.hanger_state.set_hanger_door('error')  # 关闭机库门操作异常
                        return_number = '9151'
            elif type_num == '2':  # 操作推拉杠
                if type_state_num == 'a':  # 操作上下推拉杠--打开
                    if result_num == '0':
                        self.hanger_state.set_hanger_td_bar('open')  # 上下推杆打开正常
                        return_number = '92a0'
                    else:
                        self.hanger_state.set_hanger_td_bar('error')  # 上下推杆打开异常
                        return_number = '92a1'
                elif type_state_num == 'b':  # # 操作上下推拉杠--关闭
                    if result_num == '0':
                        self.hanger_state.set_hanger_td_bar('close')  # 上下推杆关闭正常
                        return_number = '92b0'
                    else:
                        self.hanger_state.set_hanger_td_bar('error')  # 上下推杆关闭异常
                        return_number = '92b1'
                elif type_state_num == 'c':  # # 操作左右推拉杠--打开
                    if result_num == '0':
                        self.hanger_state.set_hanger_lr_bar('open')  # 左右推杆关闭正常
                        return_number = '92c0'
                    else:
                        self.hanger_state.set_hanger_lr_bar('error')  # 左右推杆关闭异常
                        return_number = '92c1'
                elif type_state_num == 'd':  # # 操作左右推拉杠--关闭
                    if result_num == '0':
                        self.hanger_state.set_hanger_lr_bar('close')  # 左右推杆关闭正常
                        return_number = '92d0'
                    else:
                        self.hanger_state.set_hanger_lr_bar('error')  # 左右推杆关闭异常
                        return_number = '92d1'
                elif type_state_num == 'e':  # # 操作四个推拉杠--夹紧
                    if result_num == '0':
                        print(f"-----------------set bar close----")
                        self.hanger_state.set_hanger_lr_bar('close')  # 左右推杆关闭正常
                        self.hanger_state.set_hanger_td_bar('close')  # 上下推杆关闭正常
                        self.hanger_state.set_hanger_bar('close')
                        return_number = '92e0'
                    else:
                        self.hanger_state.set_hanger_lr_bar('error')  # 左右推杆关闭异常
                        self.hanger_state.set_hanger_td_bar('error')  # 上下推杆关闭异常
                        self.hanger_state.set_hanger_bar('error')
                        return_number = '92e1'
                elif type_state_num == 'f':  # # 操作左右推拉杠--打开
                    if result_num == '0':
                        print(f"-----------------set bar open----")
                        self.hanger_state.set_hanger_lr_bar('open')  # 左右推杆打开正常
                        self.hanger_state.set_hanger_td_bar('open')  # 上下推杆打开正常
                        self.hanger_state.set_hanger_bar('open')
                        return_number = '92f0'
                    else:
                        self.hanger_state.set_hanger_lr_bar('error')  # 左右推杆打开异常
                        self.hanger_state.set_hanger_td_bar('error')  # 上下推杆打开异常
                        self.hanger_state.set_hanger_bar('error')
                        return_number = '92f1'
            elif type_num == '3':  # 操作空调
                if type_state_num == '0':  # 空调打开
                    if result_num == '0':
                        self.hanger_state.set_air_condition('open')  # 空调打开正常
                        return_number = '9300'
                    else:
                        self.hanger_state.set_air_condition('error')  # 空调打开异常
                        return_number = '9301'
                elif type_state_num == '1':  # 空调关闭
                    if result_num == '0':
                        self.hanger_state.set_air_condition('close')  # 空调关闭正常
                        return_number = '9310'
                    else:
                        self.hanger_state.set_air_condition('error')  # 空调关闭异常
                        return_number = '9311'
            elif type_num == '4':  # 操作无人机手柄（20221203改为操作夜灯）
                if self.hanger_state.get_night_light_state() == "close" or self.hanger_state.get_night_light_state() == "error":
                    self.hanger_state.set_night_light_state("open")  # 20221203改为设置夜灯
                else:
                    self.hanger_state.set_night_light_state("close")  # 20221203改为设置夜灯
                return_number = result
            elif type_num == '5':  # 推杆复位操作
                self.hanger_state.set_hanger_lr_bar('open')  # 左右推杆打开正常
                self.hanger_state.set_hanger_td_bar('open')  # 上下推杆打开正常
                self.hanger_state.set_hanger_bar('open')
                return_number = result

        self.engine.Close_Engine()
        return return_number


if __name__ == "__main__":
    # hangstate = HangerState()
    # device_info = "/dev/ttyUSB0"
    # bps = 115200
    # timeout = 20
    # statCom = JKSATACOM(hangstate, device_info, bps, timeout,0)
    # result=statCom.operator_hanger(commond='2b0000\r\n')
    # print(f"OK , the result is {result}")
    device_info = "/dev//dev/ttyUSBCharge"
    bps = 9600
    timeout = 20
    logger = Logger(__name__)  # 日志记录
    comm = Communication(device_info, bps, timeout, logger, None)
    comm.Open_Engine()  # 打开串口
    command_read = "01 04 00 00 00 06 70 08"
    comm.Send_data(bytes.fromhex(command_read))
    print(comm.read_lines(1))

    # statCom = Communication(com="/dev/ttyUSB0", bps=115200, timeout=5)
    # comm=Communication(com="/dev/ttyUSB0", bps=115200, timeout=5)
    # comm.Print_Name()
    # comm.Print_Used_Com()
    # while True:
    #     #comm.Send_data('00'.encode('ascii'))
    #     #success_bytes = comm.Send_data('00'.encode('ascii'))
    #     success_bytes = comm.Send_data('010000\r\n'.encode("ascii"))
    #     print (success_bytes)
    #     #print(f"send data is 00")
    #
    #     time.sleep(1)
