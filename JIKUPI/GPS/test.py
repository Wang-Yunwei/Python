# -*- coding: utf-8 -*- 
# @Time : 2023/7/21 9:29 
# @Author : ZKL 
# @File : test.py
def dm(x):
    degrees = int(x) // 100
    minutes = x - 100*degrees

    return degrees, minutes

def decimal_degrees(degrees, minutes):
    return degrees + minutes/60

print (decimal_degrees(*dm(3648.5518)))