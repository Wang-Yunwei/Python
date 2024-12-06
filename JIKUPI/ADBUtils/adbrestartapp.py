# -*- coding: utf-8 -*- 
# @Time : 2023/3/6 18:40 
# @Author : ZKL 
# @File : adbrestartapp.py
#shell am start com.zyhk.uav.android/.Controller.FlyDetailActivity
import os
#os.popen("adb shell tcpip  6000")
import time

# result1=os.popen("adb connect 172.16.21.70:6000")
# time.sleep(5)
displayPowerState=os.popen("adb shell am start com.zyhk.uav.android/.Controller.FlyDetailActivity").read().strip('\n')
print(f"displayPowerState is {displayPowerState}")
try:
    displayPowerState = os.popen("adb shell dumpsys power | grep 'Display Power: state=' | awk -F '=' '{print $2}'").read().strip('\n')
    print(displayPowerState)
    if displayPowerState == 'OFF':
        print("唤醒屏幕")
        os.system('adb shell input keyevent 26')
    else:
        print("屏幕已开启不需要唤醒")
except Exception as ex:
    print(f"{ex}")

# 熄灭屏幕223，点亮屏幕224
# os.system('adb shell input keyevent 223')