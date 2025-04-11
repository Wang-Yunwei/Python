# -*- coding: utf-8 -*- 
# @Time : 2022/2/14 11:11 
# @Author : ZKL 
# @File : test._constantpy
# byte_test=b'/x00/x01/x00/x07/x00/x00'
# restult_str=byte_test.decode(('ascii'))
# windspeed=restult_str[2:4]+restult_str[6:8]
# winddir=restult_str[10:12]+restult_str[14:16]
# rainnum=restult_str[18:20]+restult_str[22:24]
# print(int(winddir,16))#16进制转10进制

# data = []
# msg = ['FF9B']
# for i in range(len(msg)):
#     data.append(msg[i])
#     data[i] = int(data[i], 16)
#     if (data[i] & 0x8000 == 0x8000):
#         data[i] = -((data[i] - 1) ^ 0xFFFF)
#         print(data[i])
#         # 由补码求得原码，一定记得取反得是'^ 0xFFFF'，不能是'^ 0x7FFF'
import asyncio
import datetime
import functools


def get_num_f_h(h_value):
    num=int(h_value,16)
    if (num & 0x8000 == 0x8000):
        num = -((num - 1) ^ 0xFFFF)
    return num

# a="2e12342123"
# print(a[:3] + "0002"+a[7:])
# str_a=f"{3:#^30}"
# print(str_a)
# a=1
# print(f"{'3':#^20}")#.........3..........
# print(f"{'3':.>20}")#...................3
# print(f"{'3':.<20}")#3...................
#python 装饰器的写法
def log(text):
    def decorator(func):
        @functools.wraps(func)
        def app(*args,**kw):
            str1=f"begin execute the method {func.__name__}, the para is {text}"
            print(f"{str1:-^50}")
            return func(*args,**kw)
        return app
    return decorator

@log("Paramters")
def fun_1():
    print(f"The current time is {datetime.datetime.now()}")

class A():
    pass
'''
子协程
'''
def gen():
    for i in range(10):
        if i==5:
            return 'a'
        else:
            yield i
'''
委托
'''
async def test():
    print("abc")

def wrap_gen(gen):
    re=yield from gen # re用来接收生成器gen最后的return返回值a;await后只能跟协程
    print(f"{re}")

# import matplotlib.pyplot as plt
# import numpy as np
# VV=[42,46.7,46.9,47.7,47.8,48.3,48.4,49.5,49.6,50.9,52.4] # 充电电压
# Num=[0,26,27,39,40,48,49,62,63,76,90] # 无人机电量
# a=np.polyfit(VV,Num,5)#用2次多项式拟合x，y数组
# b=np.poly1d(a)#拟合完之后用这个函数来生成多项式对象
# pre_num=b(VV)#生成多项式对象之后，就是获取x在这个多项式处的值
# pre_num2=b(49.7)
# print(f"{pre_num2}")
# plt.scatter(VV,Num,marker='o',label='original datas')#对原始数据画散点图
# plt.plot(VV,pre_num,ls='--',c='red',label='fitting with second-degree polynomial')#对拟合之后的数据，也就是x，c数组画图
# plt.legend()
# plt.show()


from datetime import datetime
import sched
import time

'''
每个 10 秒打印当前时间。
'''

#
# def timedTask():
#     # 初始化 sched 模块的 scheduler 类
#     scheduler = sched.scheduler(time.time, time.sleep)
#     # 增加调度任务
#     scheduler.enter(10, 1, task)
#     # 运行任务
#     scheduler.run()
#
#
# # 定时任务
# def task():
#     print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#
#
# if __name__ == '__main__':
#     timedTask()
import time
now_time = time.strftime("%H:%M:%S", time.localtime())     # 现在的时间
print("现在是北京时间：{}".format(now_time))
# 判断时间
if "06:00:00" < now_time < "11:00:00":
    print("现在是早上")
if "11:00:00" < now_time < "14:00:00":
    print("现在是中午")
if "18:00:00" < now_time < "24:00:00":
    print("现在是晚上")