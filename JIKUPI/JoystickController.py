# -*- coding: utf-8 -*- 
# @Time : 2021/12/31 16:58 
# @Author : ZKL 
# @File : JoystickController.py
'''
手柄控制
通过GPIO引脚进行手柄电压控制
'''
import RPi.GPIO as GPIO         ## 导入GPIO库
import time                     ## 导入time库

pin_input = 11                  ## 使用11号引脚
pin_output=12                   ## 使用11号引脚
GPIO.setmode(GPIO.BOARD)        ## 使用BOARD引脚编号

GPIO.setup(pin_input, GPIO.IN)       ## 设置11号引脚为输入通道
GPIO.setup(pin_output, GPIO.OUT)       ## 设置12号引脚为输入通道

#执行操作过程

def start_Joystick():
    try:
        GPIO.output(pin_input, GPIO.LOW)## 打开GPIO引脚（LOW）
        GPIO.output(pin_output,GPIO.LOW)## 打开GPIO引脚（LOW）
        time.sleep(0.5)#等待0.5秒
        GPIO.cleanup()#断开
        GPIO.output(pin_input, GPIO.LOW)  ## 打开GPIO引脚（LOW）
        GPIO.output(pin_output, GPIO.LOW)  ## 打开GPIO引脚（LOW）
        time.sleep(2)
        GPIO.cleanup()#断开
    except Exception as e:
        print(f"手柄启动异常{e}")

if __name__=="__main__":
    start_Joystick()#启动手柄


