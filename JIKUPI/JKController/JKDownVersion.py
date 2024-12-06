# -*- coding: utf-8 -*- 
# @Time : 2024/2/18 11:41 
# @Author : ZKL 
# @File : JKDownVersion.py
'''
获取下位机版本号
'''
from BASEUtile.Config import Config
from JKController.JKDoorServer import JKDoorServer
from SATA.SATACom import JKSATACOM


class DownVersion:
    def __init__(self, comstate_flag, logger, hangerstate, comconfig):
        self.comstate_flag = comstate_flag
        self.logger = logger
        self.hangerstate = hangerstate
        self.comconfig = comconfig
    def get_dwon_version(self):
        '''
        获取下位机版本号
        '''
        #  常量/参数部分
        recv_text = "03"  # 下发指令
        result="unknown"
        try:
            #  对下位机进行操作
            statCom_door = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(),
                                     self.comconfig.get_bps_door(), self.comconfig.get_timeout_door(),
                                     self.logger,
                                     0)  # 操作的实例
            self.jkdoor = JKDoorServer(statCom_door, self.hangerstate, self.logger)  # 控制对象
            result = self.jkdoor.operator_hanger(recv_text)  # 执行命令
            # self.comstate_flag.set_door_free()  # 串口设置没有在使用
        except Exception as e:
            # self.comstate_flag.set_door_free()  # 串口设置没有在使用
            self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            result = "unknown"
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result