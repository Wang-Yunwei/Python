# -*- coding: utf-8 -*-
import BASEUtile.Config as Config
from BASEUtile.logger import Logger
import time

'''
测试新的Config功能时使用的测试类，用于注入logger，调用测试
'''
if __name__ == "__main__":
    print("test run")
    # config = Config()
    out_logger = Logger(__name__)  # 日志记录
    Config.init_logger(out_logger)

    # config.setconfiginfo("127.0.0.1", "8000", "123456789", "testurl")
    print(Config.get_websocket_config_info())
    print(Config.getconfiginfo_db())

    print(Config.get_operation_command_info())
    print(Config.getcommond_db())

    # config.setcommon_sign(closedoor="4444444")
    # config.setcommon_sign(openbar="4444444")
    # config.setDetailConfiginfo("wlc", "V2.0", "1", "0", "0", "1", "1",
    #                            "0", "1", "1", "0", "0", "V2.0", "0",
    #                            "1", "0", "0", "0", "V2.0")

    print(Config.get_config_info())
    print(Config.getdetail_config_db())

    # config.set_minio_config("124.70.41.186:9000", "admin", "1qaz@WSX", "uav-test")

    print(Config.get_minio_config_info())
    print(Config.get_minio_config_db())

    # config = Config()
    night_light = Config.get_is_night_light()  # 是否启动夜灯功能
    night_light_time_begin = int(Config.get_night_light_time_begin())
    night_light_time_end = int(Config.get_night_light_time_end())

    print(night_light)
    print(night_light_time_begin)
    print(night_light_time_end)
    t1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    hour = int(time.strftime("%H", time.localtime()))
    print(type(hour))
    hour = 19
    print(t1)
    print(hour)
    print(night_light and (night_light_time_begin <= hour or night_light_time_end > hour))
