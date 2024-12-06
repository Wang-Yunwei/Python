# -*- coding: utf-8 -*- 
# @Time : 2023/2/9 19:06 
# @Author : ZKL 
# @File : M300VolFit.py
'''
M300电量拟合
根据预测模型，对于每个输入值，计算输出电量值
当前模型只针对M300触点充电V2版本
'''
import numpy as np
class M300VolFit():
    def __init__(self):
        self.vol=[42,46.7,46.9,47.7,47.8,48.3,48.4,49.5,49.6,50.9,52.4] # 充电电压
        self.Num=[0,26,27,39,40,48,49,62,63,76,90] # 无人机电量
        self.model=None
        self.__ini_model()
    def __ini_model(self):
        '''
        初始化模型
        '''
        a = np.polyfit(self.vol, self.Num, 5)  # 用5次多项式拟合x，y数组
        self.model= np.poly1d(a)  # 拟合完之后用这个函数来生成多项式对象

    def pre_vol(self,vol,ec):
        '''
        预测电量值
        根据电压、电流预测无人机电量
        '''
        if ec>0 and vol*ec<150:#充电功率不够，电池故障
            return -1
        if vol<42:
            return 0
        if vol<52.4 and ec>0:#在充电
            return int(self.model(vol))
        if vol>=52.3 and ec>3.0:#在充电
            return 92
        if vol>=52.3 and ec>0:#在充电
            return 97
        if vol>=51.0 and ec==0:#不在充电，电压为无人机电池电压;满电情况下电压为51.8;此时判断为满电
            return 100
        return 99