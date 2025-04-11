# -*- coding: utf-8 -*- 
# @Time : 2023/8/16 10:11 
# @Author : ZKL 
# @File : StartAppClient.py
'''
启动APP远程开启的客户端
'''
import time
from websocket import create_connection
import BASEUtile.Config as Config
import BASEUtile.BusinessConstant as BusinessConstant


class StartAppClient:
    def __init__(self):
        # self.configini=configini
        pass

    def check_startup(self):
        web_socket = create_connection("ws://" + Config.get_con_server_ip_port(), timeout=3)  # 如果30秒没有收到消息则结束等待
        if web_socket != None:
            try:
                web_socket.send("startcontroller")
                wait_time = 20.0  # 等待60秒
                begin_time = time.time()
                while float(time.time() - begin_time) < wait_time:
                    print(str(time.time() - begin_time))
                    try:
                        rec_text = web_socket.recv()
                        if "start_success" in rec_text:
                            print("start success")
                            return BusinessConstant.SUCCESS
                        elif "start_failed" in rec_text:
                            print("start failed")
                            return BusinessConstant.ERROR
                    except Exception as rec_ex:
                        print(f"rec_ex exception is {rec_ex}")
                        continue
                return BusinessConstant.ERROR
            except Exception as ex:
                print(f"client {ex}")


if __name__ == "__main__":
    # check_startup()
    pass
