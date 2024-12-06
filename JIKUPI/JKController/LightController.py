# -*- coding: utf-8 -*- 
# @Time : 2023/1/3 14:54 
# @Author : ZKL 
# @File : LightController.py
# @Des : 夜航灯的打开和关闭
import time

from BASEUtile.Config import Config
from JKController.JKDoorServer import JKDoorServer
from SATA.SATACom import JKSATACOM


class LightController():
    def __init__(self,comstate_flag,logger,hangerstate,comconfig):
        self.comstate_flag=comstate_flag
        self.logger=logger
        self.hangerstate=hangerstate
        self.comconfig=comconfig

    def open_light(self):
        '''
        打开夜航灯
        '''
        #  夜灯流程进入判断
        recv_text = "400000"
        result = ""
        config = Config()
        night_light = config.get_night_light()  # 是否启动夜灯功能
        night_light_time=config.get_night_light_time() #是否判断夜灯时间段
        hour = int(time.strftime("%H", time.localtime()))  # 当前系统时间小时数
        night_light_time_begin = int(config.get_night_light_time_begin())
        night_light_time_end = int(config.get_night_light_time_end())
        #  运行夜灯功能，且当前小时在业务配置的时间段内
        self.logger.get_log().info("------------夜航灯开启判断----------")
        if (night_light and (night_light_time_begin <= hour or night_light_time_end >= hour)) or (night_light and night_light_time==False):
            # 休眠一下
            # time.sleep(2)
            # 打开夜灯判断
            self.logger.get_log().info(f"------------夜航灯开启{night_light_time_begin},{night_light_time_end},{hour}----------")
            self.logger.get_log().info(f"------------夜航灯开启{night_light}{night_light_time}----------")
            result = self.step_scene_night_light_open_400000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[打开夜灯]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            else:
                self.hangerstate.set_night_light_state("open")
        else:
            self.logger.get_log().info(f"执行命令{recv_text}，无需执行[打开夜灯]步骤")
        return result

    def close_light(self):
        '''
        关闭夜航灯
        '''
        '''
               关闭灯操作
               '''
        #  夜灯流程进入判断
        recv_text = "410000"
        result = ""
        config = Config()
        night_light = config.get_night_light()  # 是否启动夜灯功能
        #  运行夜灯功能，且当前小时在业务配置的时间段内
        if night_light:
            # 休眠一下
            self.logger.get_log().info("------------夜航灯关闭判断----------")
            # time.sleep(2)
            # 打开夜灯判断
            result = self.step_scene_night_light_close_410000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[关闭夜灯]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            else:
                self.hangerstate.set_night_light_state("close")
        else:
            self.logger.get_log().info(f"执行命令{recv_text}，无需执行[关闭夜灯]步骤")
        return result

    def step_scene_night_light_open_400000(self):
        #  常量/参数部分
        recv_text = "400000"  # 下发指令
        def_error_result = "9401"  # 默认异常
        command_error_result = "940a"  # 不支持方法异常
        used_error_result = "940d"  # 底层端口或串口被占用异常
        #  业务逻辑部分
        if self.comstate_flag.get_door_isused() is False:  # 串口没有在使用
            #self.comstate_flag.set_door_used()  # 串口设置使用中
            try:
                #  对下位机进行操作
                statCom_door = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(),
                                         self.comconfig.get_bps_door(), self.comconfig.get_timeout_door(),
                                         self.logger,
                                         0)  # 操作的实例
                self.jkdoor = JKDoorServer(statCom_door, self.hangerstate, self.logger)  # 控制对象
                result = self.jkdoor.operator_hanger(recv_text)  # 执行命令
                #self.comstate_flag.set_door_free()  # 串口设置没有在使用
            except Exception as e:
                #self.comstate_flag.set_door_free()  # 串口设置没有在使用
                self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
                result = def_error_result
        else:
            self.logger.get_log().error(f"执行命令{recv_text}，门端口被占用")
            result = used_error_result
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        elif result.endswith("0"):
            self.hangerstate.set_night_light_state("open")
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    def step_scene_night_light_close_410000(self):
        #  常量/参数部分
        recv_text = "410000"  # 下发指令
        def_error_result = "9411"  # 默认异常
        command_error_result = "941a"  # 不支持方法异常
        used_error_result = "941d"  # 底层端口或串口被占用异常
        #  业务逻辑部分
        if self.comstate_flag.get_door_isused() is False:  # 串口没有在使用
            #self.comstate_flag.set_door_used()  # 串口设置使用中
            try:
                #  对下位机进行操作
                statCom_door = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(),
                                         self.comconfig.get_bps_door(), self.comconfig.get_timeout_door(),
                                         self.logger,
                                         0)  # 操作的实例
                self.jkdoor = JKDoorServer(statCom_door, self.hangerstate, self.logger)  # 控制对象
                result = self.jkdoor.operator_hanger(recv_text)  # 执行命令
                #self.comstate_flag.set_door_free()  # 串口设置没有在使用
            except Exception as e:
                #self.comstate_flag.set_door_free()  # 串口设置没有在使用
                self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
                result = def_error_result
        else:
            self.logger.get_log().error(f"执行命令{recv_text}，门端口被占用")
            result = used_error_result
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        elif result.endswith("0"):
            self.hangerstate.set_night_light_state("close")
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result
