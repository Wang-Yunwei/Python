# -*- coding: utf-8 -*- 
# @Time : 2023/3/22 16:45 
# @Author : ZKL 
# @File : Test.py
#创建监听线程
#创建操作指令
import time

from AirCondition.AirConditionComputer import AirConditionOper
from AirCondition.AirConditionState import AirCondtionState
from AirCondition.CheckAirConState import CheckAirConState
from BASEUtile.HangerState import HangerState
from BASEUtile.logger import Logger
from ConfigIni import ConfigIni
from USBDevice.USBDeviceConfig import USBDeviceConfig
from WFCharge.WFState import WFState

logger = Logger(__name__)  # 日志记录
wfcstate = WFState()
airstate=AirCondtionState()
hangstate = HangerState(wfcstate,airstate)
configini = ConfigIni()
comconfig=USBDeviceConfig(configini)
# checkstate=CheckAirConState(airstate,hangstate,comconfig,logger)#监控类
# airoper=AirConditionOper(airstate,hangstate,comconfig,logger)
# checkstate.checkAirState()
# airoper.openAircondition()
# time.sleep(60)
# airoper.openCodeMode()
# time.sleep(120)
# airoper.closeAircondition()
airoper=AirConditionOper(airstate,hangstate,comconfig,logger)
#制冷停止温度设置
airoper.setColdStopTem(26)

