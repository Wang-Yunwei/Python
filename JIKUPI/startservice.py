# -*- coding: utf-8 -*- 
# @Time : 2021/12/15 14:50 
# @Author : ZKL 
# @File : startservice.py
# 启动机库服务（http服务）
# 启动websocket监听
import os
import threading
import time
import math
import hashlib
import json

from flask import Flask, Response, render_template, redirect
from flask import request

# 创建flask访问接口
import AirCondition
import BASEUtile.InitFileTool
import client
from Activate.ActivateUtils import ActivateUtils
from AirCondition.AirConditionComputer import AirConditionComputer
from AirCondition.CheckAirConState import CheckAirConState
from BASEUtile import MINIO
import BASEUtile.Config as Config
import BASEUtile.HangarState as HangarState
from BASEUtile.logger import Logger
from BASEUtile.loggerColl import LoggerColl
from GPS.GPSCompute import GPSInfo
from JKController.JKDownVersion import DownVersion

from MQTTUtil.python_mqtt import start_mqtt_thread_dx
from MQTTUtil.python_mqtt_jiangsudx import start_mqtt_thread_jiangsudx
from MQTTUtil.python_mqtt_hubeidianli import start_mqtt_thread_hubeidianli
from MQTTUtil.python_mqtt_nanfangdianwang import start_mqtt_thread_nanfangdianwang
from ServerManager.websockets import WebSocketUtil
from WFCharge.ChargeAtTime import ChargeAtTime
from WFCharge.CheckState import CheckState
from WFCharge.JCCListerner import JCCListerner
from WFCharge.JCCServerV2M300Single import JCCServerV2M300Single
from WFCharge.WFCV2Listerner import WFCV2Listerner
import WFCharge.WFState as WFState
from AutoCharge.AutoChargeControl import AutoChargeControl
from weather.AlarmController import AlarmController
from weather.WeatherCompute import WeatherInfo485
from weather.weather import WeatherInfo
from BASEUtile.ResultCodeDict import ResultCodeDict
from Activate.ASHelper import get_aes
import BASEUtile.BusinessConstant as BusinessConstant
from BASEUtile.InitHangarState import InitHangarState
import BASEUtile.OperateUtil as OperateUtil
import weather.AlarmLightController as AlarmLightController
from BASEUtile.BusinessEnum import AlarmLightEnum

# from weather.weather import WeatherInfo

app = Flask(__name__)
logger = Logger(__name__)  # 日志记录
BusinessConstant.LOGGER = logger
# ---------------无线充电操作
# wf_state = WFState()  # 创建对象
# ---------机库状态---包括当前无线充电的状态
# airconstate = AirCondtionState()
# hangstate = HangarState()
auto_charge = None  # 自动充电处理对象(需挂起线程)
webclient = None  # websocket推送线程


# configini = ConfigIni()  # 初始配置信息
# comconfig = USBDeviceConfig()

@app.route('/test', methods=['GET', 'POST'])
def test():
    # threading.Thread(target=AlarmLightController.open_light_thread, args=()).start()
    # while True:
    #     time.sleep(6)
    #     BusinessConstant.ALARM_LIGHT = AlarmLightEnum.YELLOW_LIGHT_FLASH
    #     time.sleep(6)
    #     BusinessConstant.ALARM_LIGHT = AlarmLightEnum.RED_LIGHT_FLASH
    #     time.sleep(6)
    #     WFState.set_battery_state("charging")
    #     BusinessConstant.ALARM_LIGHT = AlarmLightEnum.GREEN_LIGHT
    #     time.sleep(6)
    #     WFState.set_battery_state("standby")
    #     BusinessConstant.ALARM_LIGHT = AlarmLightEnum.GREEN_LIGHT
    pass


@app.route('/', methods=['GET', 'POST'])
def home():
    '''
    机库配置页面，存储信息在配置文件中（或者sqllite中），简单的页面读取和页面信息保存
    :return:
    '''
    # 先读取一个机库配置信息
    # config = Config()
    configinfo_list = Config.get_websocket_config_info()  # 列表元组的形式
    if configinfo_list is None:
        # add table
        Config.createTable()
    if configinfo_list is not None and len(configinfo_list) == 1:
        # ipaddress = configinfo_list[0][1]
        # socket_info = configinfo_list[0][2]
        # station_id = configinfo_list[0][3]
        station_id = configinfo_list[0][1]
        web_socket_url = configinfo_list[0][2]
        web_socket_heart = configinfo_list[0][3]
        username = "wkzn"
        down_version = ""
        try:
            import socket
            username = socket.gethostname()
            downversion = DownVersion(logger=logger)
            down_version = downversion.get_down_version()  # 下位机版本号
        except Exception as ex:
            logger.get_log().info(f"读取上位机用户名或者下位机版本号错误{ex}")
        # if len(configinfo_list[0]) == 5:
        #     web_socket_url = configinfo_list[0][4]
        # else:
        #     web_socket_url = ''
        return render_template('index.html', station_id=station_id, web_socket_url=web_socket_url,
                               web_socket_heart=web_socket_heart, username=username,
                               down_version=down_version)
    return render_template('index.html')


@app.route('/license', methods=['GET', 'POST'])
def license():
    '''
    机库配置页面，存储信息在配置文件中（或者sqllite中），简单的页面读取和页面信息保存
    :return:
    '''
    # config=Config()
    # (1)读取机器码，默认机库的mac地址
    activate = ActivateUtils(logger)
    # maccode=activate.getMacCode()
    maccode = activate.get_unique_identifier()
    activatecode = ""
    try:
        # 读取已经注册的license
        activatecode = Config.get_license_code()
        # 获取剩余天数
        left_days = -1
        if activatecode == "":
            left_days = -1
        else:
            left_days = activate.get_left_days(activate.read_license(activatecode)['time_str'])
        if left_days == -1:
            left_days = "未激活或已过期"
        return render_template('activate.html', left_days=left_days, maccode=maccode, activatecode=activatecode)
    except Exception as e:
        return render_template('activate.html', left_days="unknown", maccode=maccode, activatecode=activatecode)


@app.route('/savelicense', methods=['GET', 'POST'])
def savelicense():
    '''
    保存日志上传路径配置
    :return:
    '''
    try:
        params = request.form if request.method == "POST" else request.args
        activatecode = params['activatecode']
        # 保存信息
        # config = Config()
        Config.set_license_code(activatecode)

        activate = ActivateUtils(logger)
        # maccode = activate.getMacCode()
        maccode = activate.get_unique_identifier()
        # 读取已经注册的license
        activatecode = Config.get_license_code()
        # 获取剩余天数
        left_days = -1
        if activatecode == "":
            left_days = -1
        else:
            left_days = activate.get_left_days(activate.read_license(activatecode)['time_str'])
        if left_days == -1:
            left_days = "未激活或已过期"
        return render_template('activate.html', left_days=left_days, maccode=maccode, activatecode=activatecode)
    except Exception as ex:
        return render_template('activate.html')


# 通过验证拦截器
@app.before_request
def check_license():
    url = request.path  # 当前请求的URL
    passUrl = ["/license", "/savelicense"]
    if url in passUrl:
        pass
    elif "favicon" in url or "static" in url:
        pass
    else:
        res = {}
        try:
            # config=Config()
            activate = ActivateUtils(logger)
            license_dic = activate.read_license(Config.get_license_code())
            date_bool = activate.check_license_date(license_dic['time_str'])
            psw_bool = activate.check_license_psw(license_dic['psw'])
            if psw_bool:
                if date_bool:
                    res['status'] = True
                    res['time'] = license_dic['time_str']
                    res['msg'] = "一切正常"
                else:
                    res['status'] = False
                    res['time'] = license_dic['time_str']
                    res['msg'] = "激活码过期"
                    logger.get_log().info(res)
            else:
                res['status'] = False
                res['time'] = license_dic['time_str']
                res['msg'] = "MAC不匹配, License无效, 请更换License"
                logger.get_log().info(res)
        except Exception as ex:
            res['status'] = False
            res['time'] = ""
            res['msg'] = "激活码无效"
            logger.get_log().info(res)
        if len(res) != 0 and res['status'] == False:
            return "激活码无效或过期，请联系机库厂商"


'''
json格式：获取机库地址配置
'''

# @app.route('/json_get_config', methods=['GET', 'POST'])
# def json_get_config():
#     response = {
#         "ipaddress": "",
#         "socket": "",
#         "station_id": "",
#         "web_socket_url": ""
#     }
#     # 先读取一个机库配置信息
#     # config = Config()
#     configinfo_list = Config.get_websocket_config_info()  # 列表元组的形式
#     if configinfo_list is not None and len(configinfo_list) == 1:
#         # ipaddress = configinfo_list[0][1]
#         # socket = configinfo_list[0][2]
#         # station_id = configinfo_list[0][3]
#         web_socket_url = configinfo_list[0][1]
#         # if len(configinfo_list[0]) == 5:
#         #     web_socket_url = configinfo_list[0][4]
#         # else:
#         #     web_socket_url = ''
#         # response["ipaddress"] = ipaddress
#         # response["socket"] = socket
#         # response["station_id"] = station_id
#         response["web_socket_url"] = web_socket_url
#     logger.get_log().info(f"[json_get_config] response = {response}")
#     return Response(json.dumps(response), mimetype='application/json')


'''
json格式：设置机库地址配置，(包括重启)
'''

# @app.route('/json_set_config', methods=['GET', 'POST'])
# def json_set_config():
#     params = request.json if request.method == "POST" else request.args
#     logger.get_log().info(f"[json_set_config] request = {params}")
#     request_demo = {
#         "ipaddress": "124.71.225.193",
#         "socket": "18088",
#         "station_id": "95091e705eceda57",
#         "web_socket_url": "ws://api.wogrid.com:15005/95091e705eceda57"
#     }
#     response = {
#         "code": "000000",
#         "message": "成功"
#     }
#     try:
#         # config = Config()
#         # ipaddress = params['ipaddress']
#         # socket = params['socket']
#         station_id = params['station_id']
#         web_socket_url = params['web_socket_url']
#         # Config.set_websocket_config_info(ip=ipaddress, socket=socket, station_id=station_id,
#         #                                  web_socket_url=web_socket_url, logger=logger)
#         Config.set_websocket_config_info(station_id=station_id, web_socket_url=web_socket_url, logger=logger)
#         reboot_websocket()
#     except Exception as ex:
#         response["code"] = "000001"
#         response["message"] = "失败"
#         logger.get_log().error(f"[json_set_config] Exception = {ex}")
#         return Response(json.dumps(response), mimetype='application/json')
#
#     logger.get_log().info(f"[json_set_config] response = {response}")
#     return Response(json.dumps(response), mimetype='application/json')


'''
json格式：重启websocket服务(休眠后重启，包括重启异常时也休眠后继续重启)
'''


@app.route('/json_reboot_websocket', methods=['GET', 'POST'])
def json_reboot_websocket():
    response = {
        "code": "000000",
        "message": "成功"
    }
    reboot_websocket()
    logger.get_log().info(f"[json_reboot_websocket] response = {response}")
    return Response(json.dumps(response), mimetype='application/json')


'''
重启websocket服务(休眠后重启，包括重启异常时也休眠后继续重启)
'''


def reboot_websocket():
    # 全局对象，websocket链接对象
    global webclient
    # 重新启动websocket服务
    if webclient is not None and webclient.server_service is True:  # websocket服务在运行中
        logger.get_log().info("[reboot_websocket] websocket重新启动")
        # 启动websocket无限连接和消息接收机制
        webclient.server_service = False  # 让webclient停止运行
        while True:
            time.sleep(15)  # 等待15秒
            try:
                if webclient is None or webclient.server_service is False:
                    webclient = WebSocketUtil(
                        server_addr='', logger=logger, auto_charge=auto_charge)
                    webclient.start_service()
                else:
                    break
            except Exception as ex:
                logger.get_log().info(f"[reboot_websocket] 服务端设置后重新启动websocket异常,{ex}")
                continue
        logger.get_log().info("[reboot_websocket] webclient设置后已启动，启动webservice")


'''
json格式：获取机库挂载配置
'''


@app.route('/json_get_config_info', methods=['GET', 'POST'])
def json_get_config_info():
    response = {}
    response["charge_version"] = Config.get_charge_version()
    response["wfc_version"] = Config.get_wfc_version()
    response["wlc_version"] = Config.get_wlc_version()
    response["down_version"] = Config.get_down_version()
    response["bar_diff_move"] = Config.get_is_bar_diff_move()
    response["GPS"] = boolean_to_10string(Config.get_is_gps())
    response["use_weather"] = boolean_to_10string(Config.get_is_use_weather())
    response["weather_485"] = boolean_to_10string(Config.get_is_weather_485())
    response["rain"] = boolean_to_10string(Config.get_is_rain())
    response["rain_num"] = boolean_to_10string(Config.get_is_rain_num())
    response["wind"] = boolean_to_10string(Config.get_is_wind())
    response["wind_dir"] = boolean_to_10string(Config.get_is_wind_dir())
    response["temp_hum"] = boolean_to_10string(Config.get_is_temp_hum())
    response["is_parking_temp_hum"] = boolean_to_10string(Config.get_is_parking_temp_hum())
    response["smoke"] = boolean_to_10string(Config.get_is_smoke())
    response["wfc_double_connect"] = boolean_to_10string(Config.get_is_wfc_double_connect())  # 无线充电是否使用USB全双工通信，手动配置进去
    response["wlc_double_connect"] = boolean_to_10string(Config.get_is_wlc_double_connect())  # 触点充电，使用全双工通信
    response["need_auto_charge"] = boolean_to_10string(Config.get_is_need_auto_charge())  # 是否需要自动充电功能
    response["need_heartbeat_check"] = boolean_to_10string(Config.get_is_need_heartbeat_check())  # 是否需要心跳检测功能
    logger.get_log().info(f"[json_get_config_info] response = {response}")
    return Response(json.dumps(response), mimetype='application/json')


def boolean_to_10string(flag):
    if flag:
        return "1"
    else:
        return "0"


@app.route('/json_set_config_info', methods=['GET', 'POST'])
def json_set_config_info():
    params = request.json if request.method == "POST" else request.args
    logger.get_log().info(f"[json_set_config_info] request = {params}")
    request_demo = {
        "charge_version": "wlc",
        "wfc_version": "V2.0",
        "wlc_version": "V2.0",
        "down_version": "V1.0",
        "bar_diff_move": "1",
        "GPS": "0",
        "use_weather": "1",
        "weather_485": "0",
        "rain": "1",
        "rain_num": "0",
        "wind": "1",
        "wind_dir": "1",
        "temp_hum": "0",
        "smoke": "0",
        "wfc_double_connect": "0",
        "wlc_double_connect": "1",
        "need_auto_charge": "1",
        "need_heartbeat_check": "1",
        "indoor_temp": "0"
    }
    response = {
        "code": "000000",
        "message": "成功"
    }
    try:
        charge_version = params['charge_version']  # wfc:无线充电  wlc:有线充电
        wfc_version = params['wfc_version']
        wlc_version = params['wlc_version']
        bar_diff_move = params['bar_diff_move']  # 1:是或选中 0:否或未选中
        GPS = params['GPS']  # 1:是或选中 0:否或未选中
        use_weather = params['use_weather']  # 1:是或选中 0:否或未选中
        weather_485 = params['weather_485']  # 1:是或选中 0:否或未选中
        rain = params['rain']  # 1:是或选中 0:否或未选中
        rain_num = params['rain_num']  # 1:是或选中 0:否或未选中
        wind = params['wind']  # 1:是或选中 0:否或未选中
        wind_dir = params['wind_dir']  # 1:是或选中 0:否或未选中
        temp_hum = params['temp_hum']  # 1:是或选中 0:否或未选中
        smoke = params['smoke']  # 1:是或选中 0:否或未选中
        wfc_double_connect = params['wfc_double_connect']  # 无线充电是否使用USB全双工通信，手动配置进去  1:是或选中 0:否或未选中
        wlc_double_connect = params['wlc_double_connect']  # 触点充电，使用全双工通信  1:是或选中 0:否或未选中
        need_auto_charge = params['need_auto_charge']  # 是否需要自动充电功能  1:是或选中 0:否或未选中
        need_heartbeat_check = params['need_heartbeat_check']  # 是否需要心跳检测功能  1:是或选中 0:否或未选中
        down_version = params['down_version']
        indoor_temp = params["indoor_temp"]
        # repeat_bar=params["repeat_bar"]#是否启用充电失败后，推杆夹紧操作

        # config = Config()
        # 存储处理
        Config.set_config_info(charge_version, wfc_version, bar_diff_move, GPS, use_weather, weather_485, rain,
                               rain_num, wind, wind_dir, temp_hum, smoke, down_version, wfc_double_connect,
                               wlc_double_connect, need_auto_charge, need_heartbeat_check, indoor_temp, wlc_version,
                               logger)

        # 是否需要重启websocket接口
        is_reboot = False
        if not need_heartbeat_check == boolean_to_10string(Config.get_is_need_heartbeat_check()):
            is_reboot = True
        # 重新加载数据
        time.sleep(5)
        # configini.ini_config()  # 重新从数据库加载

        #  重启websocket接口
        if is_reboot:
            reboot_websocket()

    except Exception as ex:
        response["code"] = "000001"
        response["message"] = "失败"
        logger.get_log().error(f"[json_set_config] 业务流程发生异常 Exception = {ex}")
        return Response(json.dumps(response), mimetype='application/json')

    logger.get_log().info(f"[json_set_config] response = {response}")
    return Response(json.dumps(response), mimetype='application/json')


'''
json格式：获取机库状态
'''


@app.route('/json_get_state', methods=['GET', 'POST'])
def json_get_state():
    response = HangarState.get_hangar_state_dict()
    logger.get_log().info(f"[json_get_state] response = {response}")
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/logupload', methods=['GET', 'POST'])
def logupload():
    '''
    机库配置页面，存储信息在配置文件中（或者sqllite中），简单的页面读取和页面信息保存
    :return:
    '''
    # 先读取一个机库配置信息
    logger.get_log().info(f"上传本地日志")
    # buck_name = "uav-test"
    # # 获取站点ID编号
    # config = Config()
    # configinfo_list = config.getconfiginfo()
    # station_id = configinfo_list[0][3]
    # utilminio = MINIO.MiniUtils(logger)
    # utilminio.start_uploadfile(buck_name, f"{station_id}.log")
    utilminio = MINIO.MiniUtils(logger)
    utilminio.start_uploadlog()
    return testpage()


@app.route('/logclear', methods=['GET', 'POST'])
def logclear():
    '''
    机库配置页面，存储信息在配置文件中（或者sqllite中），简单的页面读取和页面信息保存
    :return:
    '''
    # 先读取一个机库配置信息
    logger.get_log().info(f"清空本地日志")
    logger.delete_log()
    return testpage()


@app.route('/logconfig', methods=['GET', 'POST'])
def logconfig():
    '''
    加载日志上传路径配置
    :return:
    '''
    # 读取数据库当前配置信息状态
    # config_db = Config()
    log_conf = Config.get_minio_config_info()
    return render_template('logconfig.html', minio_ip=log_conf[0][1], minio_username=log_conf[0][2],
                           minio_password=log_conf[0][3], minio_dir=log_conf[0][4],
                           upload_log_url=Config.get_upload_log_url())


@app.route('/savelogconfig', methods=['GET', 'POST'])
def savelogconfig():
    '''
    保存日志上传路径配置
    :return:
    '''
    try:
        logger.get_log().info(f"[http.savelogconfig]日志配置信息保存-开始")
        params = request.form if request.method == "POST" else request.args
        logger.get_log().info(f"[http.savelogconfig]日志配置信息保存-参数:{params}")
        minio_ip = params['minio_ip']
        minio_username = params['minio_username']
        minio_password = params['minio_password']
        minio_dir = params['minio_dir']
        upload_log_url = params['upload_log_url']
        # minio_suffix = params['minio_suffix']
        # 保存信息
        # minio_config = Config()
        Config.set_minio_config_info(minio_ip, minio_username, minio_password, minio_dir, logger)
        Config.set_upload_log_url(upload_log_url)
        logger.get_log().info(f"[http.savelogconfig]日志配置信息保存-结束,保存成功")
        return logconfig()
    except Exception as ex:
        logger.get_log().info(f"[http.savelogconfig]日志配置信息保存-异常,异常信息为:{ex}")
        return logconfig()


@app.route('/reboot', methods=['GET', 'POST'])
def reboot():
    print('Client restart.')
    # reboot system
    import subprocess
    # subprocess.call(["echo 'wkzn123' | bash /home/wkzn/jkstart.sh"])
    # subprocess.call(["echo","wkzn123","|", "bash", "/home/wkzn/jkstart.sh"],shell=True)
    # subprocess.call(["bash","/home/wkzn/jkreboot.sh"])
    # status = subprocess.call('/home/wkzn/jkreboot.sh')
    try:
        logger.get_log().info(f"[http.reboot]重启上位机-开始")
        script_path = '/home/wkzn/JIKUPI/jkreboot.sh'
        result = subprocess.run([script_path], check=True, stdout=subprocess.PIPE)
        # subprocess.call(["echo", "wkzn123", "|", "systemctl", "restart","jkstart.service"], stdout=subprocess.PIPE,shell=True)
        # 执行shell脚本
        # result = subprocess.run([script_path], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # # 打印输出和错误信息
        # print(result.stdout)  # 脚本的输出
        # print(result.stderr)  # 脚本的错误信息
        # os.popen(script_path)
        time.sleep(6)
        logger.get_log().info(f"[http.reboot]重启上位机-结束")
    except Exception as ex:
        logger.get_log().info(f"[http.reboot]重启上位机异常,异常信息为:{ex}")


@app.route('/testpage', methods=['GET', 'POST'])
def testpage():
    '''
    测试页面，通过点击页面就可以操作机库
    :return:
    '''
    # 读取机库当前状态
    # result = f"\"hanger_door\": \"{self.hanger_door}\",\"hanger_td_bar\": \"{self.hanger_td_bar}\",\"air_condition\": \"{self.air_condition}\",\"STAT_connet_state\": \"{self.STAT_connet_state}\",\"hanger_lr_bar\": \"{self.hanger_lr_bar}\"," \
    #          f"\"charge_state\": \"{self.wfcstate.get_state()}\",\"hanger_bar\": \"{self.hanger_bar}\",\"uav_controller\": \"{self.uav_controller}\",\"windspeed\": \"{self.windspeed}\",\"winddirction\": \"{self.winddirection}\",\"rain\": \"{self.rain}\""
    # return "{" + result + "}"
    hanger_door = HangarState.get_hangar_door_state()
    hanger_bar = HangarState.get_hangar_bar_state()
    hanger_air = HangarState.get_air_condition_state()
    hanger_uav = HangarState.get_uav_controller_state()
    hanger_updown_lift = HangarState.get_updown_lift_state()
    hanger_turn_lift = HangarState.get_turn_lift_state()
    # 读取操控指令，门开，门关；推杆开，推杆关；空调开，空调关；手柄开，手柄关；
    # config = Config()
    commond_list = Config.get_operation_command_info()  # 列表元组的形式
    coldstoptem = Config.get_coldstoptem()
    coldsenstem = Config.get_coldsenstem()
    hotstoptem = Config.get_hotstoptem()
    hotsenstem = Config.get_hotsenstem()
    hihum = Config.get_hihum()
    lowhum = Config.get_lowhum()
    if commond_list is None:
        # add table
        Config.createTable()
    if commond_list is not None and len(commond_list) == 1:
        opendoor = commond_list[0][1]
        closedoor = commond_list[0][2]
        openbar = commond_list[0][3]
        closebar = commond_list[0][4]
        openair = commond_list[0][5]
        closeair = commond_list[0][6]
        openuav = commond_list[0][7]
        closeuav = commond_list[0][8]
        uplift = commond_list[0][9]
        downlift = commond_list[0][10]
        turnlift = commond_list[0][11]
        backlift = commond_list[0][12]
        return render_template('testpage.html', hanger_door=hanger_door, hanger_bar=hanger_bar, hanger_air=hanger_air,
                               hanger_uav=hanger_uav, hanger_updown_lift=hanger_updown_lift,
                               hanger_turn_lift=hanger_turn_lift,
                               opendoor=opendoor, closedoor=closedoor, openbar=openbar, closebar=closebar,
                               openair=openair, closeair=closeair, openuav=openuav,
                               closeuav=closeuav, coldstoptem=coldstoptem, coldsenstem=coldsenstem,
                               hotsenstem=hotsenstem, hotstoptem=hotstoptem,
                               hihum=hihum, lowhum=lowhum, turn_lift=turnlift, back_lift=backlift)
    return render_template('testpage.html')


@app.route('/getCommand', methods=['GET', 'POST'])
def getCommand():
    response = {
        "code": "9000",
        "message": "成功"
    }
    logger.get_log().info(f"[getCommand]开始执行")
    try:
        # 读取操控指令，门开，门关；推杆开，推杆关；空调开，空调关；手柄开，手柄关；
        # config = Config()
        commond_list = Config.get_operation_command_info()  # 列表元组的形式
        if commond_list is not None and len(commond_list) == 1:
            opendoor = commond_list[0][1]
            closedoor = commond_list[0][2]
            openbar = commond_list[0][3]
            closebar = commond_list[0][4]
            openair = commond_list[0][5]
            closeair = commond_list[0][6]
            openuav = commond_list[0][7]
            closeuav = commond_list[0][8]
            response["opendoor"] = opendoor
            response["closedoor"] = closedoor
            response["openbar"] = openbar
            response["closebar"] = closebar
            response["openair"] = openair
            response["closeair"] = closeair
            response["openuav"] = openuav
            response["closeuav"] = closeuav
        else:
            response["code"] = "9001"
            response["message"]: "未查询到数据"
    except Exception as ex:
        logger.get_log().error(f"[getCommand]执行过程中发生异常:{ex}")
        response["code"] = "9001"
        response["message"]: "执行发生异常"
    logger.get_log().info(f"[getCommand]得到结果{response}")
    return Response(json.dumps(response), mimetype='application/json')


'''
设置命令(更新DB，并进行执行)
'''


@app.route('/setCommand/<string:command>', methods=['GET', 'POST'])
def setCommand(command):
    params = request.json if request.method == "POST" else request.args
    logger.get_log().info(f"[setCommand] command = {command} request = {params}")
    request_demo = {
        "command_code": "140120"
    }
    response = {
        "code": "error_command",
        "message": "不支持的命令"
    }
    command_code = params["command_code"]
    global webclient

    result = "error_command"
    # config = Config()
    if command == "140000":
        Config.set_operation_command_info_sign(logger=logger, opendoor=command_code)
        time.sleep(2)  # 操作一下数据库
        result = OperateUtil.operate_hangar("140000")
    elif command == "150000":
        Config.set_operation_command_info_sign(logger=logger, closedoor=command_code)
        time.sleep(2)  # 操作一下数据库
        result = OperateUtil.operate_hangar("150000")
    elif command == "2e10002000":
        Config.set_operation_command_info_sign(logger=logger, closebar=command_code)
        time.sleep(2)  # 操作一下数据库
        result = OperateUtil.operate_hangar("2e10002000")
    elif command == "2f10002000":
        Config.set_operation_command_info_sign(logger=logger, openbar=command_code)
        time.sleep(2)  # 操作一下数据库
        result = OperateUtil.operate_hangar("2f10002000")
    elif command == "500000":
        logger.get_log().info(f"[setCommand] command = {command} 不支持DB设置参数，直接调用方法")
        result = OperateUtil.operate_hangar("500000")
    elif command == "300000":
        Config.set_operation_command_info_sign(logger=logger, openair=command_code)
        time.sleep(2)  # 操作一下数据库
        result = OperateUtil.operate_hangar("300000")
    elif command == "310000":
        Config.set_operation_command_info_sign(logger=logger, closeair=command_code)
        time.sleep(2)  # 操作一下数据库
        result = OperateUtil.operate_hangar("310000")
    elif command == "400000":
        Config.set_operation_command_info_sign(logger=logger, openuav=command_code)
        time.sleep(2)  # 操作一下数据库
        result = OperateUtil.operate_hangar("400000")
    elif command == "410000":
        Config.set_operation_command_info_sign(logger=logger, closeuav=command_code)
        time.sleep(2)  # 操作一下数据库
        result = OperateUtil.operate_hangar("410000")
    else:
        logger.get_log().info(f"暂不支持命令{command}")
    if not result == "error_command":
        resultCodeDict = ResultCodeDict()
        response["code"] = result
        response["message"] = resultCodeDict.get_msg(result)
    logger.get_log().info(f"[setCommand] 返回结果{response}")
    return Response(json.dumps(response), mimetype='application/json')


@app.route('/doCommand/<string:command>', methods=['GET', 'POST'])
def doCommand(command):
    """
    手柄调用
    """
    response = {
        "code": "error_command",
        "message": "不支持的命令"
    }
    logger.get_log().info(f"[http.doCommand]手柄调用-开始,执行{command}命令")
    result = OperateUtil.operate_hangar(command)
    logger.get_log().info(f"[http.doCommand]手柄调用-结束,执行{command}命令,返回结果{result}")
    if not result == "error_command":
        resultCodeDict = ResultCodeDict()
        response["code"] = result
        response["message"] = resultCodeDict.get_msg(result)
    return Response(json.dumps(response), mimetype='application/json')


# ===============================手柄操控===============================start
@app.route('/operhanger', methods=['GET', 'POST'])
def operhanger():
    """
    手柄调用
    """
    params = request.json if request.method == "POST" else request.args
    # 解析传递过来的参数
    try:
        if params is not None:  #
            commond = params['commond']
            logger.get_log().info(f"[http.operhanger]手柄调用-开始,执行{commond}命令")
            result = OperateUtil.operate_hangar(commond)
            logger.get_log().info(f"[http.operhanger]手柄调用-结束,执行{commond}命令,返回结果为:{result}")
            return result
        else:
            logger.get_log().info(f"[http.operhanger]手柄调用-异常,参数为空")
            return "参数是空"
    except Exception as ex:
        logger.get_log().info(f"[http.operhanger]手柄调用-异常,异常信息为:{ex}")
        return BusinessConstant.ERROR


@app.route('/opercharge', methods=['GET', 'POST'])
def oper_charge():
    """
    手柄调用,无人机充电
    :return:
    """
    params = request.json if request.method == "POST" else request.args
    # 解析传递过来的参数
    try:
        if params is not None:  #
            commond = params['commond']
            logger.get_log().info(f"[http.opercharge]手柄调用-开始,执行{commond}命令")
            if commond in ["Charge", "TakeOff", "Standby", "DroneOff", "Check", "DisplayOn", "DisplayOff", "Connect"]:
                return OperateUtil.operate_hangar(commond)
            else:
                return "充电操作命令错误"
        else:
            logger.get_log().info(f"[http.operhanger]手柄调用-异常,参数为空")
            return "充电操作命令为空"
    except Exception as e:
        logger.get_log().info(f'工控机调用充电异常，异常{e}')
        return "error"


# ===============================手柄操控===============================end


@app.route('/config', methods=['GET', 'POST'])
def configpage():
    '''
    挂载配置页面
    :return:
    '''
    # 读取当前配置信息状态
    # print(f"night_light={type(configini.get_night_light())}")
    # print(f"repeat={type(configini.get_repeat_bar())}")
    return render_template('config.html', charge_version=Config.get_charge_version(),
                           wlc_version=Config.get_wlc_version(),
                           wfc_version=Config.get_wfc_version(), down_version=Config.get_down_version(),
                           bar_diff_move=Config.get_is_bar_diff_move(),
                           GPS=Config.get_is_gps(), use_weather=Config.get_is_use_weather(),
                           weather_485=Config.get_is_weather_485(),
                           rain=Config.get_is_rain(), rain_num=Config.get_is_rain_num(), wind=Config.get_is_wind(),
                           wind_dir=Config.get_is_wind_dir(), temp_hum=Config.get_is_temp_hum(),
                           is_parking_temp_hum=Config.get_is_parking_temp_hum(),
                           smoke=Config.get_is_smoke(), wfc_double_connect=Config.get_is_wfc_double_connect(),
                           wlc_double_connect=Config.get_is_wlc_double_connect(),
                           need_auto_charge=Config.get_is_need_auto_charge(),
                           need_heartbeat_check=Config.get_is_need_heartbeat_check(),
                           indoor_temp=Config.get_is_indoor_temp(),
                           night_light=Config.get_is_night_light(),
                           night_light_time_begin=Config.get_night_light_time_begin(),
                           night_light_time_end=Config.get_night_light_time_end(),
                           repeat_bar=Config.get_is_repeat_bar(),
                           night_charge=Config.get_is_night_charge(),
                           night_light_time=Config.get_is_night_light_time(),
                           signal_battery_charge=Config.get_is_signal_battery_charge(),
                           weather_wait_time=Config.get_weather_wait_time(),
                           aircon485=Config.get_is_aircon485(),
                           meanopen=Config.get_is_meanopen(),
                           alarm=Config.get_is_alarm(),
                           alarm_light=Config.get_is_alarm_light(),
                           bar_move_style=Config.get_bar_move_style(),
                           air_condition_computer_version=Config.get_air_condition_computer_version(),
                           hangar_version=Config.get_hangar_version(),
                           controller_ip=Config.get_controller_ip(),
                           con_server_ip_port=Config.get_con_server_ip_port(),
                           td_bar=Config.get_is_td_bar(),
                           blance_charge=Config.get_is_blance_charge())


@app.route('/mqtt', methods=['GET', 'POST'])
def mqtt_page():
    '''
    直接读取INI文件
    '''
    return render_template('mqtt.html',
                           is_run_mqtt=BASEUtile.InitFileTool.get_boolean_value("mqtt_info", "is_run_mqtt"),
                           mqtt_type=BASEUtile.InitFileTool.get_str_value("mqtt_info", "mqtt_type"),
                           host_str=BASEUtile.InitFileTool.get_str_value("mqtt_info", "host_str"),
                           port_int=BASEUtile.InitFileTool.get_str_value("mqtt_info", "port_int"),
                           username_str=BASEUtile.InitFileTool.get_str_value("mqtt_info", "username_str"),
                           password_str=BASEUtile.InitFileTool.get_str_value("mqtt_info", "password_str"),
                           client_id=BASEUtile.InitFileTool.get_str_value("mqtt_info", "client_id")
                           )


@app.route('/save_mqtt_config', methods=['GET', 'POST'])
def save_mqtt_config():
    params = request.form if request.method == "POST" else request.args
    print(params)
    is_run_mqtt = params['is_run_mqtt']
    mqtt_type = params['mqtt_type']
    host_str = params['host_str']
    port_int = params['port_int']
    username_str = params['username_str']
    password_str = params['password_str']
    client_id = params['client_id']

    BASEUtile.InitFileTool.set_value("mqtt_info", "is_run_mqtt", is_run_mqtt)
    BASEUtile.InitFileTool.set_value("mqtt_info", "mqtt_type", mqtt_type)
    BASEUtile.InitFileTool.set_value("mqtt_info", "host_str", host_str)
    BASEUtile.InitFileTool.set_value("mqtt_info", "port_int", port_int)
    BASEUtile.InitFileTool.set_value("mqtt_info", "username_str", username_str)
    BASEUtile.InitFileTool.set_value("mqtt_info", "password_str", password_str)
    BASEUtile.InitFileTool.set_value("mqtt_info", "client_id", client_id)
    return mqtt_page()


@app.route('/saveconfig', methods=['GET', 'POST'])
def saveconfigpage():
    '''
        挂载保存页面，保存数据库，并且重新启动服务
        :return:
        '''
    # 读取当前配置信息状态
    try:
        # config = Config()
        params = request.form if request.method == "POST" else request.args
        logger.get_log().info(f"[saveconfigpage]参数设置{params}")
        charge_version = params['charge_version']
        if charge_version == "无线充电":
            charge_version = "wfc"
        else:
            charge_version = "wlc"
        wfc_version = params['wfc_version']
        wlc_version = params['wlc_version']
        bar_diff_move = 'False'
        GPS = 'False'
        use_weather = 'False'
        weather_485 = 'False'
        rain = 'False'
        rain_num = 'False'
        wind = 'False'
        wind_dir = 'False'
        temp_hum = 'False'
        is_parking_temp_hum = 'False'
        smoke = 'False'
        wfc_double_connect = 'False'  # 无线充电是否使用USB全双工通信，手动配置进去
        wlc_double_connect = 'False'  # 触点充电，使用全双工通信
        need_auto_charge = 'False'  # 是否需要自动充电功能
        need_heartbeat_check = 'False'  # 是否需要心跳检测功能
        down_version = params['down_version']
        indoor_temp = 'False'  # 是否读取室内温湿度
        night_light = 'False'  # 是否需要夜间灯功能
        repeat_bar = 'False'
        night_charge = 'False'
        night_light_time = 'False'
        signal_battery_charge = 'False'
        weather_wait_time = '10'
        aircon485 = 'False'
        meanopen = 'False'
        alarm = 'False'
        alarm_light = 'False'
        bar_move_style = params['bar_move_style']
        air_condition_computer_version = params['air_condition_computer_version']
        hangar_version = params['hangar_version']
        controller_ip = ""
        td_bar = 'False'
        blance_charge = 'False'

        if 'bar_diff_move' in params.keys():
            bar_diff_move = 'True'
        if "GPS" in params.keys():
            GPS = 'True'
        if "use_weather" in params.keys():
            use_weather = 'True'
        if "weather_485" in params.keys():
            weather_485 = 'True'
        if "rain" in params.keys():
            rain = 'True'
        if "rain_num" in params.keys():
            rain_num = 'True'
        if "wind" in params.keys():
            wind = 'True'
        if "wind_dir" in params.keys():
            wind_dir = 'True'
        if "temp_hum" in params.keys():
            temp_hum = 'True'
        if "is_parking_temp_hum" in params.keys():
            is_parking_temp_hum = 'True'
        if "smoke" in params.keys():
            smoke = 'True'
        if "wfc_double_connect" in params.keys():
            wfc_double_connect = 'True'
        if "wlc_double_connect" in params.keys():
            wlc_double_connect = 'True'
        if "need_auto_charge" in params.keys():
            need_auto_charge = 'True'
        if "need_heartbeat_check" in params.keys():
            need_heartbeat_check = 'True'
        if "indoor_temp" in params.keys():
            indoor_temp = 'True'
        if "night_light" in params.keys():
            night_light = 'True'
        if "repeat_bar" in params.keys():
            repeat_bar = 'True'
        if "night_charge" in params.keys():
            night_charge = 'True'
        if "night_light_time" in params.keys():
            night_light_time = 'True'
        if "signal_battery_charge" in params.keys():
            signal_battery_charge = "True"
        if "aircon485" in params.keys():
            aircon485 = 'True'
        if "meanopen" in params.keys():
            meanopen = 'True'
        if "alarm" in params.keys():
            alarm = 'True'
        if "alarm_light" in params.keys():
            alarm_light = 'True'
        if "td_bar" in params.keys():
            td_bar = 'True'
        if "blance_charge" in params.keys():
            blance_charge = 'True'

        print(
            f"{charge_version},{wfc_version},{bar_diff_move},{GPS},{use_weather},{weather_485},{rain},{rain_num},{wind},{wind_dir},{temp_hum},{smoke},{down_version},{wfc_double_connect},{wlc_double_connect},{need_auto_charge},{need_heartbeat_check},{indoor_temp},{wlc_version},{repeat_bar},{night_charge}")
        # 存储处理
        # 老版本存储方法
        Config.set_config_info(charge_version, wfc_version, bar_diff_move, GPS, use_weather, weather_485, rain,
                               rain_num, wind, wind_dir, temp_hum, smoke, down_version, wfc_double_connect,
                               wlc_double_connect, need_auto_charge, need_heartbeat_check, indoor_temp, wlc_version,
                               logger)
        # 新追加处理字段
        Config.set_is_night_light(night_light)
        Config.set_night_light_time_begin(params["night_light_time_begin"])
        Config.set_night_light_time_end(params["night_light_time_end"])
        Config.set_is_repeat_bar(repeat_bar)
        Config.set_is_night_charge(night_charge)
        Config.set_is_night_light_time(night_light_time)
        Config.set_is_signal_battery_charge(signal_battery_charge)
        Config.set_weather_wait_time(params["weather_wait_time"])
        Config.set_is_aircon485(aircon485)
        Config.set_is_meanopen(meanopen)
        Config.set_is_alarm(alarm)
        Config.set_is_alarm_light(alarm_light)
        Config.set_bar_move_style(params["bar_move_style"])
        Config.set_controller_ip(params["controller_ip"])
        Config.set_con_server_ip_port(params["con_server_ip_port"])
        Config.set_is_td_bar(td_bar)
        Config.set_is_blance_charge(blance_charge)
        Config.set_air_condition_computer_version(air_condition_computer_version)
        Config.set_hangar_version(hangar_version)
        Config.set_is_parking_temp_hum(is_parking_temp_hum)
        time.sleep(5)
        # 重新启动系统
        # try:
        #     configini.ini_config()  # 重新从数据库加载
        # except Exception as ex:
        #     print(f"{ex}")
        return "请重新启动服务程序"
    except Exception as ex:
        return render_template('config.html')


# def bar_use_check(commond):
#     if commond.startswith("2f") or commond.startswith("50"):  # 推杆打开操作或者复位操作
#         exe_charge_commond("standby")  # 充电先做一次复位操作
#     result = ""
#     # 2023-4-4 如果是空调操作指令，并且启用了空调485通信
#     if Config.get_is_aircon485() == True and commond.startswith('3'):
#         airManager = AirConditionOper(logger)
#         if commond.startswith('30'):  # 开空调
#             airManager.openAircondition()
#             HangarState.set_air_condition_state('open')
#             result = '9300'
#         else:
#             airManager.closeAircondition()
#             HangarState.set_air_condition_state('close')
#             result = '9310'
#     else:
#         # 如果使用485读取天气，则不作waiting处理
#         if Config.get_is_weather_485() is True:
#             if SerialUsedStateFlag.get_is_used_serial_bar() == False:
#                 logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}http推杆调用，收到命令{commond}")
#                 SerialUsedStateFlag.set_used_serial_bar()
#                 try:
#                     statCom_bar = JKSATACOM(USBDeviceConfig.get_serial_usb_bar(), USBDeviceConfig.get_serial_bps_bar(),
#                                             USBDeviceConfig.get_serial_timeout_bar(), logger, 0)
#                     jkbar = JKBarServer(statCom_bar, logger)
#                     result = jkbar.operator_hanger(commond)
#                     SerialUsedStateFlag.set_used_serial_free_bar()
#                     logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} http推杆调用，返回{result}")
#                 except Exception as barex:
#                     SerialUsedStateFlag.set_used_serial_free_bar()
#             else:
#                 logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} http推杆调用，推杆端口被占用，返回busy")
#                 result = "busy"
#
#     return result


# def commonfun(commond):
#     result = ''
#     if commond.startswith("1") or commond.startswith("4"):  # 门的操作
#         if commond.startswith("14"):  # 开门
#             result = OperateUtil.step_scene_door_open_140000(logger)  # 开门、开灯
#         elif commond.startswith("15"):  # 关门
#             result = OperateUtil.step_scene_door_close_150000(logger)  # 关门、关灯
#         elif commond.startswith("40"):  # 开灯
#             result = OperateUtil.step_scene_night_light_open_400000(logger)
#         elif commond.startswith("41"):  # 关灯
#             result = OperateUtil.step_scene_night_light_close_410000(logger)
#         # if SerialUsedStateFlag.get_is_used_serial_door() == False:  # 串口没有在使用
#         #     SerialUsedStateFlag.set_used_serial_door()
#         #     try:
#         #         logger.get_log().info(f'页面调用,机库门操作,{commond}')
#         #         statCom_door = JKSATACOM(USBDeviceConfig.get_serial_usb_door(), USBDeviceConfig.get_serial_bps_door(),
#         #                                  USBDeviceConfig.get_serial_timeout_door(), logger, 0)
#         #         jkdoor = JKDoorServer(statCom_door, logger)
#         #         result = jkdoor.operator_hanger(commond)
#         #         SerialUsedStateFlag.set_used_serial_free_door()
#         #     except Exception as doorex:
#         #         SerialUsedStateFlag.set_used_serial_free_door()
#         # else:
#         #     result = "busy"
#     else:  # 推杆的操作
#         result = webclient.bar_use_check(commond)
#     # try:
#     #     # 如果有门的操作，则做一下灯光操作
#     #     lightcontroller = LightController(logger=logger)
#     #
#     #     if commond.startswith("14"):
#     #         lightcontroller.open_light()
#     #     elif commond.startswith("15"):
#     #         lightcontroller.close_light()
#     # except Exception as excpte:
#     #     print(f"-----------灯光异常{excpte}------------")
#     hanger_door = HangarState.get_hangar_door_state()
#     hanger_bar = HangarState.get_hangar_bar_state()
#     hanger_air = HangarState.get_air_condition_state()
#     hanger_uav = HangarState.get_uav_controller_state()
#     # 读取操控指令，门开，门关；推杆开，推杆关；空调开，空调关；手柄开，手柄关；
#     # config = Config()
#     commond_list = Config.get_operation_command_info()  # 列表元组的形式
#     if commond_list is None:
#         # add table
#         Config.createTable()
#     if commond_list is not None and len(commond_list) == 1:
#         opendoor = commond_list[0][1]
#         closedoor = commond_list[0][2]
#         openbar = commond_list[0][3]
#         closebar = commond_list[0][4]
#         openair = commond_list[0][5]
#         closeair = commond_list[0][6]
#         openuav = commond_list[0][7]
#         closeuav = commond_list[0][8]
#         return render_template('testpage.html', hanger_door=hanger_door, hanger_bar=hanger_bar,
#                                hanger_air=hanger_air, hanger_uav=hanger_uav, opendoor=opendoor, closedoor=closedoor,
#                                openbar=openbar, closebar=closebar, openair=openair, closeair=closeair,
#                                openuav=openuav, closeuav=closeuav)


@app.route('/opendoor', methods=['GET', 'POST'])
def opendoor():
    try:
        params = request.form if request.method == "POST" else request.args
        # config = Config()
        commond = params['opendoorcomm']
        Config.set_operation_command_info_sign(logger=logger, opendoor=commond)
        # time.sleep(2)  # 操作一下数据库
        logger.get_log().info(f"[http.opendoor]页面调用开门")
        return OperateUtil.operate_hangar("140000")
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/closedoor', methods=['GET', 'POST'])
def closedoor():
    try:
        params = request.form if request.method == "POST" else request.args
        # config = Config()
        commond = params['closedoorcomm']
        Config.set_operation_command_info_sign(logger=logger, closedoor=commond)
        # time.sleep(2)  # 操作一下数据库
        logger.get_log().info(f"[http.closedoor]页面调用关门")
        return OperateUtil.operate_hangar("150000")
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/openbar', methods=['GET', 'POST'])
def openbar():
    try:
        params = request.form if request.method == "POST" else request.args
        # config = Config()
        commond = params['openbarcomm']
        Config.set_operation_command_info_sign(logger=logger, openbar=commond)
        # time.sleep(2)  # 操作一下数据库
        # return commonfun(commond)
        logger.get_log().info(f"[http.openbar]页面调用推杆打开")
        return OperateUtil.operate_hangar("2f10002000")
    except Exception as ex:
        return render_template('testpage.html')

# 前后推杆打开
@app.route('/opentdbar', methods=['GET', 'POST'])
def opentdbar():
    try:
        params = request.form if request.method == "POST" else request.args
        # config = Config()
        commond = "2f2000"
        # Config.set_operation_command_info_sign(logger=logger, openbar=commond)
        # time.sleep(2)  # 操作一下数据库
        # return commonfun(commond)
        logger.get_log().info(f"[http.opentdbar]页面调用前后推杆打开")
        return OperateUtil.operate_hangar(commond)
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/closebar', methods=['GET', 'POST'])
def closebar():
    try:
        params = request.form if request.method == "POST" else request.args
        # config = Config()
        commond = params['closebarcomm']
        Config.set_operation_command_info_sign(logger=logger, closebar=commond)
        # time.sleep(2)  # 操作一下数据库
        # return commonfun(commond)
        logger.get_log().info(f"[http.closebar]页面调用推杆夹紧")
        return OperateUtil.operate_hangar("2e10002000")
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/turnLift', methods=['GET', 'POST'])
def turnLift():
    try:
        params = request.form if request.method == "POST" else request.args
        # config = Config()
        commond = params['turnliftcomm']
        Config.set_operation_command_info_sign(logger=logger, turnlift=commond)
        result = OperateUtil.operate_hangar("800000")
        return result
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/backLift', methods=['GET', 'POST'])
def backLift():
    try:
        params = request.form if request.method == "POST" else request.args
        # config = Config()
        commond = params['backliftcomm']
        Config.set_operation_command_info_sign(logger=logger, backlift=commond)
        result = OperateUtil.operate_hangar("810000")
        return result
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/openair', methods=['GET', 'POST'])
def openair():
    try:
        params = request.form if request.method == "POST" else request.args
        # config = Config()
        commond = params['openaircomm']
        if Config.get_is_aircon485():
            aircontroller = AirCondition.AirConditionComputer.AirConditionComputer(logger)
            result = OperateUtil.operate_hangar("300000")
            if result == BusinessConstant.SUCCESS:
                HangarState.set_air_condition_state(BusinessConstant.OPEN_STATE)
                result = OperateUtil.operate_hangar("940000")
            return result
        Config.set_operation_command_info_sign(logger=logger, openair=commond)
        # time.sleep(2)  # 操作一下数据库
        # return commonfun(commond)
        logger.get_log().info(f"[http.openair]页面调用空调打开")
        return OperateUtil.operate_hangar("300000")
    except Exception as ex:
        logger.get_log().info(f"exception is {ex}")
        return render_template('testpage.html')


@app.route('/closeair', methods=['GET', 'POST'])
def closeair():
    try:
        params = request.form if request.method == "POST" else request.args
        # config = Config()
        commond = params['closeaircomm']
        if Config.get_is_aircon485():
            aircontroller = AirCondition.AirConditionComputer.AirConditionComputer(logger)
            result = OperateUtil.operate_hangar("310000")
            if result == BusinessConstant.SUCCESS:
                HangarState.set_air_condition_state(BusinessConstant.CLOSE_STATE)
                result = OperateUtil.operate_hangar("950000")
            return result
        Config.set_operation_command_info_sign(logger=logger, closeair=commond)
        # time.sleep(2)  # 操作一下数据库
        # return commonfun(commond)
        logger.get_log().info(f"[http.closeair]页面调用空调关闭")
        return OperateUtil.operate_hangar("310000")
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/setair', methods=['GET', 'POST'])
def setair():
    try:
        params = request.form if request.method == "POST" else request.args
        # config = Config()
        coldstoptem = params['coldstoptem']
        coldsenstem = params['coldsenstem']
        hotstoptem = params['hotstoptem']
        hotsenstem = params['hotsenstem']
        hihum = params['hihum']
        lowhum = params['lowhum']
        aircontroller = AirCondition.AirConditionComputer.AirConditionComputer(logger)
        aircontroller.setColdStopTem(coldstoptem)
        aircontroller.setColdSensitivityTem(coldsenstem)
        aircontroller.setHotStopTem(int(hotstoptem))
        aircontroller.setHotSensitivityTem(hotsenstem)
        aircontroller.setHiHumidityAlarm(hihum)
        aircontroller.setLowHumidityAlarm(lowhum)
        # 存储参数
        Config.set_coldstoptem(coldstoptem)
        Config.set_coldsenstem(coldsenstem)
        Config.set_hotstoptem(hotstoptem)
        Config.set_hotsenstem(hotsenstem)
        Config.set_hihum(hihum)
        Config.set_lowhum(lowhum)
        time.sleep(2)  # 操作一下数据库
        return redirect('/testpage')
    except Exception as ex:
        logger.get_log().info(f"exception is {ex}")
        return redirect('/testpage')


@app.route('/uavcontroller', methods=['GET', 'POST'])
def uavcontro():
    """
    夜灯控制
    """
    try:
        params = request.form if request.method == "POST" else request.args
        commond = params['controller']
        # config = Config()
        if commond == "open":
            commond = "400000"
            logger.get_log().info(f"[http.uavcontroller]页面调用夜灯打开")
            return OperateUtil.operate_hangar("400000")
            # config.setcommon_sign(openuav=commond)  # 夜灯操作不在更新INI配置
        else:
            commond = "410000"
            logger.get_log().info(f"[http.uavcontroller]页面调用夜灯关闭")
            return OperateUtil.operate_hangar("410000")
            # config.setcommon_sign(closeuav=commond)  # 夜灯操作不在更新INI配置
        # print(f"{commond:=<100}")
        # time.sleep(2)  # 操作一下数据库
        # return commonfun(commond)
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/resetbar', methods=['GET', 'POST'])
def resetbar():
    try:
        # config = Config()
        commond = "500000"
        # return commonfun(commond)
        logger.get_log().info(f"[http.resetbar]页面调用推杆复位")
        return OperateUtil.operate_hangar("500000")
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/ABCharge', methods=['GET', 'POST'])
def ABCharge():
    try:
        params = request.form if request.method == "POST" else request.args
        commond = params['wfcommond']
        if commond in ["AStartCharge", "BStartCharge", "AStopCharge", "BStopCharge"]:
            result = ""
            WFC = JCCServerV2M300Single(logger)
            if commond == "AStartCharge":
                WFC.charge_A()
                return "A充电"
            elif commond == "BStartCharge":
                WFC.charge_B()
                return "B充电"
            elif commond == "AStopCharge":
                WFC.standby_A()
                return "A停止充电"
            elif commond == "BStopCharge":
                WFC.standby_B()
                return "B停止充电"
        else:
            return "充电操作命令错误"
    except Exception as e:
        logger.get_log().info(f'工控机调用AB充电异常，异常{e}')
        return f"AB充电操作异常，{e}"


@app.route('/wfccontroller', methods=['GET', 'POST'])
def wfccontroller():
    """
    页面http操作
    """
    try:
        params = request.form if request.method == "POST" else request.args
        commond = params['wfcommond']
        logger.get_log().info(f"[http页面.wfccontroller]电池操作-开始,接收命令为:{commond}")
        if commond in ["Charge", "TakeOff", "Standby", "DroneOff", "Check", "DisplayOn", "DisplayOff", "Connect"]:
            result = ""
            # if Config.get_is_need_auto_charge():  # 启动自动充电
            if commond == "Charge":  # 充电操作
                result = OperateUtil.operate_hangar("cp0000")
                if WFState.get_battery_value() == "100":
                    # 满电
                    result = "full"
                elif WFState.get_battery_state() == "cool":
                    # 降温
                    result = "cool"
            elif commond == "TakeOff":
                result = OperateUtil.operate_hangar("dt0000")
            elif commond == "DroneOff":
                result = OperateUtil.operate_hangar("dd0000")
            elif commond == "Standby":
                result = OperateUtil.operate_hangar("sb0000")
            else:
                result = OperateUtil.exe_charge_command(commond)
            logger.get_log().info(f"[http页面.wfccontroller]电池操作-结束,接收命令为:{commond},返回结果为:{result}")
            return result
        else:
            logger.get_log().info(f"[http页面.wfccontroller]电池操作-结束,接收命令为:{commond},充电命令错误")
            return "充电操作命令错误"
    except Exception as ex:
        logger.get_log().info(f"[http页面.wfccontroller]电池操作-异常,接收命令为:{commond},异常信息为:{ex}")
        return f"充电异常，{e}"


@app.route('/shutterDoor', methods=['GET', 'POST'])
def shutterDoor():
    try:
        params = request.form if request.method == "POST" else request.args
        commond = params['shutterDoor']
        # config = Config()
        if commond == "open":
            # commond = "400000"
            # config.setcommon_sign(openuav=commond)  # 夜灯操作不在更新INI配置
            result = OperateUtil.operate_hangar("920000")
        else:
            # commond = "410000"
            # config.setcommon_sign(closeuav=commond)  # 夜灯操作不在更新INI配置
            result = OperateUtil.operate_hangar("930000")
        # print(f"{commond:=<100}")
        # time.sleep(2)  # 操作一下数据库
        return result
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/shandeWindow', methods=['GET', 'POST'])
def shandeWindow():
    try:
        params = request.form if request.method == "POST" else request.args
        commond = params['shadeWindow']
        # config = Config()
        if commond == "open":
            # commond = "400000"
            # config.setcommon_sign(openuav=commond)  # 夜灯操作不在更新INI配置
            result = OperateUtil.operate_hangar("940000")
        else:
            # commond = "410000"
            # config.setcommon_sign(closeuav=commond)  # 夜灯操作不在更新INI配置
            result = OperateUtil.operate_hangar("950000")
        # print(f"{commond:=<100}")
        # time.sleep(2)  # 操作一下数据库
        return result
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/updownLift', methods=['GET', 'POST'])
def updownLift():
    try:
        params = request.form if request.method == "POST" else request.args
        commond = params['updownLift']
        # config = Config()
        if commond == "upLift":
            # commond = "400000"
            # config.setcommon_sign(openuav=commond)  # 夜灯操作不在更新INI配置
            result = OperateUtil.operate_hangar("700000")
        else:
            # commond = "410000"
            # config.setcommon_sign(closeuav=commond)  # 夜灯操作不在更新INI配置
            result = OperateUtil.operate_hangar("710000")
        # print(f"{commond:=<100}")
        # time.sleep(2)  # 操作一下数据库
        return result
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/testdoortimes', methods=['GET', 'POST'])
def test_door_times():
    try:
        test_log = LoggerColl(__name__)
        params = request.form if request.method == "POST" else request.args
        times = params['doortesttimes']  # 测试次数
        distance = params['doorpara']  # 开关门的参数
        openwait = params['openwait']  # 开门等待时间
        closewait = params['closewait']  # 关门等待时间
        error_times = 0
        # error_times_song=0
        current_time = 1
        for i in range(int(times)):
            strinfo = f"第{current_time}次开门操作"
            test_log.get_log().info(f"{strinfo:*^50}")
            result = ""
            # if not SerialUsedStateFlag.get_is_used_serial_door():  # 串口没有在使用
            #     SerialUsedStateFlag.set_used_serial_door()
            #     try:
            #         logger.get_log().info(f'页面调用,机库门操作,{distance}')
            #         OperateUtil.step_scene_door_open_140000(logger)
            #         SerialUsedStateFlag.set_used_serial_free_door()
            #     except Exception as doorex:
            #         SerialUsedStateFlag.set_used_serial_free_door()
            # else:
            #     result = "busy"
            result = OperateUtil.operate_hangar("140000")

            if result != "9140":
                error_times += 1
                # logger.get_log().info(f",返回结果{result}，共计失败次数{error_times_jia},{statCom_bar.engine.main_engine.is_open}")
                strinfo = f"第{current_time}次开门操作失败,下位机返回结果为：{result},停止开门操作"
                test_log.get_log().info(f"{strinfo:=^50}")
                break
            # 松开
            time.sleep(int(openwait))
            strinfo = f"第{current_time}次关门操作"
            test_log.get_log().info(f"{strinfo:-^50}")
            # if SerialUsedStateFlag.get_is_used_serial_door() == False:  # 串口没有在使用
            #     SerialUsedStateFlag.set_used_serial_door()
            #     try:
            #         logger.get_log().info(f'页面调用,机库门操作,150000')
            #         OperateUtil.step_scene_door_close_150000(logger)
            #         SerialUsedStateFlag.set_used_serial_free_door()
            #     except Exception as doorex:
            #         SerialUsedStateFlag.set_used_serial_free_door()
            # else:
            #     result = "busy"
            result = OperateUtil.operate_hangar("150000")

            if result != "9150":
                strinfo = f"第{current_time}次关门操作失败,下位机返回结果为：{result},停止关门操作"
                test_log.get_log().info(f"{strinfo:+^50}")
                break
            if i == int(times) - 1:
                break
            time.sleep(int(closewait))
            current_time = current_time + 1
        strinfo = f"总共需要进行{times}次开门、关门操作，成功了{current_time}次"
        test_log.get_log().info(f"{strinfo:!^50}")
        return testpage()
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/testbartimes', methods=['GET', 'POST'])
def test_bar_times():
    test_log = LoggerColl(__name__)
    try:
        params = request.form if request.method == "POST" else request.args
        times = params['testtimes']  # 测试次数
        distance = params['tuigandis']  # 移动的参数
        jiajinwait = params['jiajinwait']  # 夹紧等待时间
        originwait = params['originwait']  # 原点等待时间
        current_time = 1
        for i in range(int(times)):
            strinfo = f"第{current_time}次夹紧操作"
            test_log.get_log().info(f"{strinfo:*^50}")
            # 夹紧
            result = OperateUtil.operate_hangar("2e10002000")
            if result != "92e0":
                strinfo = f"第{current_time}次夹紧操作失败,下位机返回结果为：{result},停止夹紧操作"
                test_log.get_log().info(f"{strinfo:=^50}")
                break  # 有串口资源被占用，则不再做测试操作
            time.sleep(int(jiajinwait))
            # 松开
            commond = "2f10002000"
            result = OperateUtil.operate_hangar(commond)
            strinfo = f"第{current_time}次松开推杆操作"
            test_log.get_log().info(f"{strinfo:-^50}")
            if result != "92f0":
                strinfo = f"第{current_time}次松开操作失败,下位机返回结果为：{result},停止松开操作"
                test_log.get_log().info(f"{strinfo:+^50}")
                break
            if i == int(times) - 1:
                break
            time.sleep(int(originwait))
            current_time = current_time + 1
        strinfo = f"总共需要进行{times}次推杆夹紧和松开操作，成功了{current_time}次"
        test_log.get_log().info(f"{strinfo:%^50}")
        return testpage()
    except Exception as ex:
        return render_template('testpage.html')


@app.route('/testbarresettimes', methods=['GET', 'POST'])
def test_barreset_times():
    try:
        test_log = LoggerColl(__name__)
        params = request.form if request.method == "POST" else request.args
        times = params['testresettimes']  # 测试次数
        distance = params['tuiganresetdis']  # 移动的参数
        resetjiajinwait = params['resetjiajinwait']  # 夹紧等待时间
        resetwait = params['resetwait']  # 复位原点等待时间
        error_times_jia = 0
        error_times_song = 0
        current_time = 1
        for i in range(int(times)):
            strinfo = f"第{current_time}次夹紧操作"
            test_log.get_log().info(f"{strinfo:*^50}")
            commond = distance
            # result = webclient.bar_use_check(commond)
            result = OperateUtil.operate_hangar("2e10002000")
            if result != "92e0":
                strinfo = f"第{current_time}次夹紧操作失败,下位机返回结果为：{result},停止夹紧操作"
                test_log.get_log().info(f"{strinfo:=^50}")
                break
            time.sleep(int(resetjiajinwait))
            # 松开
            commond = "500000"
            # result = webclient.bar_use_check(commond)
            result = OperateUtil.operate_hangar("500000")
            strinfo = f"第{current_time}次复位推杆操作"
            test_log.get_log().info(f"{strinfo:-^50}")
            if result != "9500":
                strinfo = f"第{current_time}次复位推杆操作失败,下位机返回结果为：{result},停止复位操作"
                test_log.get_log().info(f"{strinfo:+^50}")
                break
            if i == int(times) - 1:
                break
            time.sleep(int(resetwait))
            current_time = current_time + 1
        strinfo = f"总共需要进行{times}次推杆夹紧和复位操作，成功了{current_time}次"
        test_log.get_log().info(f"{strinfo:%^50}")
        return testpage()


    except Exception as ex:
        return render_template('testpage.html')


@app.route('/save', methods=['GET', 'POST'])
def saveWebsocket():
    '''
    页面信息保存
    :return:
    '''
    global webclient
    try:
        params = request.form if request.method == "POST" else request.args
        # config = Config()
        # ipaddress = params['server_ip']
        # socket = params['socket']
        station_id = params['station_id']
        web_socket_url = params['web_socket_url']
        web_socket_heart = params['web_socket_heart']
        Config.set_websocket_config_info(station_id=station_id, web_socket_url=web_socket_url,
                                         web_socket_heart=web_socket_heart, logger=logger)
        configinfo_list = Config.get_websocket_config_info()  # 列表元组的形式
        station_id = configinfo_list[0][1]
        web_socket_url = configinfo_list[0][2]
        web_socket_heart = configinfo_list[0][3]
        # if configinfo_list is not None and len(configinfo_list) == 1:  # 页面显示信息
        #     ipaddress = configinfo_list[0][1]
        #     socket = configinfo_list[0][2]
        #     station_id = configinfo_list[0][3]
        #     if len(configinfo_list[0]) == 5:
        #         web_socket_url = configinfo_list[0][4]
        #     else:
        #         web_socket_url = ''
        # 重新启动websocket服务
        if webclient is not None and webclient.server_service == True:  # websocket服务在运行中
            logger.get_log().info("websocket重新启动")
            # 启动websocket无限连接和消息接收机制
            webclient.server_service = False  # 让webclient停止运行
            time.sleep(15)  # 等待15秒
            while True:
                try:
                    if webclient is None or webclient.server_service == False:
                        webclient = WebSocketUtil(server_addr='', logger=logger,
                                                  auto_charge=auto_charge)
                        webclient.start_service()
                    else:
                        break
                except Exception as e:
                    logger.get_log().info(f"服务端设置后重新启动websocket异常,{e}")
                    continue
            logger.get_log().info("webclient设置后已启动，启动webservice")

        # if webclient == None or webclient.server_service == False:
        # return render_template('index.html', station_id=station_id, web_socket_url=web_socket_url,web_socket_heart=web_socket_heart)
        return BusinessConstant.SUCCESS
    except Exception as ex:
        # return render_template('index.html')
        return BusinessConstant.ERROR


#
#
# def open_close_light(commond):
#     '''
#     打开或关闭灯光线程
#     '''
#     # 打开或关闭灯光线程
#     if commond.startswith("14"):
#         # 如果是开门操作，则做开灯操作
#         lightcontroller = LightController(logger=logger)
#         lightcontroller.open_light()
#     elif commond.startswith("15"):
#         # 如果是关门操作，则做关灯操作
#         lightcontroller = LightController(logger=logger)
#         lightcontroller.close_light()


@app.route('/gethangerstate', methods=['GET', 'POST'])
def gethangerstate():
    '''
    获取机库参数
    :return:
    '''
    try:
        # print(f"{hangstate.getHangerState()}")
        return HangarState.get_hangar_state()
    except Exception as e:
        logger.get_log().info(f'工控机调用机库，异常{e}')
        return "error"


@app.route('/gechargestate', methods=['GET', 'POST'])
def getchargestate():
    '''
    获取机库参数
    :return:
    '''
    try:
        return WFState.get_charge_info()
    except Exception as e:
        logger.get_log().info(f'触点充电状态调用异常{e}')
        return "error"


@app.route('/getWFCstate', methods=['GET', 'POST'])
def getWFCstate():
    '''
    获取充电参数
    :return:
    '''
    try:
        return WFState.get_battery_state()
    except Exception as e:
        logger.get_log().info(f'充电状态获取异常，{e}')
        return "error"


@app.route('/alarmcontroller', methods=['GET', 'POST'])
def alarmController():
    '''
   警报设置
    :return:
    '''
    try:
        params = request.form if request.method == "POST" else request.args
        commond = params['controller']
        print(f"{commond}")
        alarmControl = AlarmController(logger)
        if commond == "open":
            alarmControl.start_alarm()
        else:
            alarmControl.stop_alarm()
        return "success"
    except Exception as e:
        return "success"


@app.route('/opencontroller', methods=['GET', 'POST'])
def remoteController():
    '''
   遥控器开关机设置
    :return:
    '''
    try:
        params = request.form if request.method == "POST" else request.args
        commond = params['controller']
        print(f"{commond}")
        result = "error"
        if commond == "open":
            result = OperateUtil.operate_hangar("h00000")
        else:
            result = OperateUtil.operate_hangar("h10000")
        return result
    except Exception as e:
        return "excepiton"


# def exe_charge_commond(commond):
#     '''
#     执行充电相关命令
#     :param commond:
#     :return:
#     '''
#     try:
#         result = ""
#         if SerialUsedStateFlag.get_is_used_serial_charge() == False:
#             SerialUsedStateFlag.set_used_serial_charge()
#             try:
#                 if Config.get_charge_version() == "wfc":  # 无线充电
#                     if Config.get_wfc_version() == 'V1.0':  # V1.0版本
#                         WFC = WFCServer(logger)
#                         result = WFC.operator_charge(commond)
#                     elif Config.get_wfc_version() == 'V2.0':  # V2.0版本
#                         if Config.get_is_wfc_double_connect() == False:
#                             WFC = WFCServerV2(logger)
#                         else:
#                             WFC = WFCServerV2Sender(logger)
#                         result = WFC.operator_charge(commond)
#                 else:  # 触点充电
#                     if Config.get_wlc_version() == "V1.0":
#                         if Config.get_is_wlc_double_connect() == True:  # 全双工通信
#                             WFC = JCCServerM300Sender(logger)
#                         else:
#                             WFC = JCCServerM300(logger)
#                         result = WFC.operator_charge(commond)
#                     elif Config.get_wlc_version() == "V2.0":  # V2.0
#                         WFC = JCCServerV2M300Single(logger)
#                         result = WFC.operator_charge(commond)
#                     elif Config.get_wlc_version() == "V3.0":  # V3.0
#                         WFC = JCCServerV3M300(logger)
#                         result = WFC.operator_charge(commond)
#                     elif Config.get_wlc_version() == "V4.0":  # V4.0
#                         WFC = JCCServerV4M350(logger)
#                         result = WFC.operator_charge(commond)
#                     elif Config.get_wlc_version() == "V5.0":  # V5.0
#                         WFC = JCCServerV5(logger)
#                         result = WFC.operator_charge(commond)
#                 SerialUsedStateFlag.set_used_serial_free_charge()
#             except Exception as charex:
#                 SerialUsedStateFlag.set_used_serial_free_charge()
#         else:
#             logger.get_log().info(f"http 充电指令{commond}无法执行，因为充电串口被占用")
#             result = "chargeerror"
#         return result
#     except Exception as ex:
#         logger.get_log().info(f"http 充电指令{commond}执行异常")
#         return "chargeerror"


# def open_autocharge():
#     '''
#     调用自动充电
#     设置自动充电(auto_charge,fly_back)+电量为0+充电
#     :return:
#     '''
#     # 充电操作
#     WFState.set_battery_value("0")  # 电池状态未知
#     result = "chargeerror"
#     # result = exe_charge_commond("Charge")
#     result = OperateUtil.step_scene_drone_charge_cp0000(logger)
#     global auto_charge
#     auto_charge.set_run_auto_charge(1)
#     auto_charge.set_fly_back(1)
#     return result
#
#
# def close_autocharge():
#     '''
#     结束自动充电
#     设置自动充电关闭+standby
#     :return:
#     '''
#     global auto_charge
#     auto_charge.set_run_auto_charge(0)
#     auto_charge.set_fly_back(-1)
#     # 复位操作
#     result = "chargeerror"
#     # result = exe_charge_commond("Standby")
#     result = OperateUtil.step_scene_drone_standby_sb0000(logger)
#     return result
#
#
# def takeoff():
#     '''
#     设置开机
#     close_autocharge()
#     takeoff命令
#     :return:
#     '''
#     close_autocharge()
#     result = "chargeerror"
#     result = exe_charge_commond("TakeOff")
#     return result
#
#
# def droneoff():
#     '''
#     设置关机
#     关机+自动充电
#     :return:
#     '''
#     result = "chargeerror"
#     close_autocharge()
#     # exe_charge_commond("Standby")
#     result = exe_charge_commond("DroneOff")
#     # global auto_charge
#     # wf_state.set_battery_value("0")  # 电池状态未知
#     # auto_charge.set_run_auto_charge(1)
#     auto_charge.set_fly_back(1)
#     return result
#
#
# def standby():
#     '''
#     设置复位操作
#     结束自动充电+复位
#     :return:
#     '''
#     result = close_autocharge()
#     return result


def reset_machine():
    '''
    重启服务后复位操作
    :return:
    '''
    # 上电后做一次复位操作
    logger.get_log().info(f'重启做一次复位操作')
    commmond = "500000"
    result = OperateUtil.operate_hangar("500000")
    logger.get_log().info(f'推杆复位执行结果为：{result}')
    # # 升降台初始化下降
    # result = webclient.step_scene_down_lift_710000()
    logger.get_log().info(f'升降台初始化下降结果为：{result}')


def start_Aircondition():
    '''
    重启空调
    '''
    if Config.get_is_aircon485():
        aircontroller = AirCondition.AirConditionComputer.AirConditionComputer(logger)
        result = OperateUtil.operate_hangar("300000")
        if result == BusinessConstant.SUCCESS:
            HangarState.set_air_condition_state('open')
        logger.get_log().info(f"重启上位机操作，重启空调485操作,返回结果为:{result}")
    else:
        commond_air = "300000"
        result = OperateUtil.operate_hangar("300000")
        logger.get_log().info(f"重启上位机操作，重启空调{result}")
    time.sleep(5)


@app.route('/updatesoftware', methods=['GET', 'POST'])
def updatesoftware():
    '''
    升级上位机程序
    :return:
    '''
    logger.get_log().info("升级上位机程序")
    client.updatesoftware()
    return "success"


'''
[江苏电信定制版]江苏电信接口-获取token
'''


@app.route('/api/v1/getToken', methods=['POST'])
def jsdx_get_token():
    params = request.json if request.method == "POST" else request.args
    request_demo = {
        "timestamp": "1703573281",
        "userinfo": "cfa11343be27bf9805de69873c461cf7"
    }
    response = {
        "code": "1",
        "msg": "成功",
        "token": ""
    }
    logger.get_log().info(f"[jsdx_get_token][in][{params['timestamp']}][{params['userinfo']}]")
    username = BASEUtile.InitFileTool.get_str_value("jsdx_info", "username")
    password = BASEUtile.InitFileTool.get_str_value("jsdx_info", "password")
    time_abs = BASEUtile.InitFileTool.get_int_value("jsdx_info", "time_abs")
    # print(f"config==={username}")
    # print(f"config==={password}")
    # print(f"config==={time_abs}")
    in_timestamp = str(params['timestamp'])
    in_userinfo = str(params['userinfo'])

    # 时间戳验证
    int_in_timestamp = int(in_timestamp)
    logger.get_log().info(f"[jsdx_get_token][in_time][{int_in_timestamp}]")
    int_now_timestamp = int(time.time()) * 1000
    logger.get_log().info(f"[jsdx_get_token][now_time][{int_now_timestamp}]")
    if math.fabs(int_now_timestamp - int_in_timestamp) > time_abs:
        response['code'] = '0'
        response['msg'] = '时间戳错误'
        logger.get_log().info(f"[jsdx_get_token][msg][时间戳错误]")
        return Response(json.dumps(response), mimetype='application/json')
    # MD5验证
    logger.get_log().info(f"[jsdx_get_token][domd5]")
    logger.get_log().info(f"[jsdx_get_token][username][{username}]")
    logger.get_log().info(f"[jsdx_get_token][password][{password}]")
    logger.get_log().info(f"[jsdx_get_token][in_timestamp][{in_timestamp}]")
    test_str = username + "_" + password + "_" + in_timestamp
    logger.get_log().info(f"[jsdx_get_token][test_str][{test_str}]")
    md5 = hashlib.md5()
    md5.update(test_str.encode('utf-8'))
    check_hash = md5.hexdigest()
    # print("MD5算法的hash值:", check_hash)
    logger.get_log().info(f"[jsdx_get_token][check_hash][{check_hash}]")
    if in_userinfo != check_hash:
        response['code'] = '0'
        response['msg'] = '验证失败'
        return Response(json.dumps(response), mimetype='application/json')

    # 验证成功，给token
    str_now_timestamp = str(int_now_timestamp)
    token = get_aes().encrypt(str_now_timestamp)
    response['token'] = token
    logger.get_log().info(f"[jsdx_get_token][token][{token}]")
    return Response(json.dumps(response), mimetype='application/json')


'''
[江苏电信定制版]江苏电信接口-手动控制机库
'''


@app.route('/api/v1/shelter/control', methods=['POST'])
def jsdx_shelter_control():
    params = request.json if request.method == "POST" else request.args
    request_demo = {
        "token": "xxx",
        "sheltercode": "xxx",
        "opertyp": "xxx"
    }
    response = {
        "code": "1",
        "msg": "成功"
    }
    time_abs = BASEUtile.InitFileTool.get_int_value("jsdx_info", "time_abs")
    #  配置中的方舱编码
    sheltercode = BASEUtile.InitFileTool.get_str_value("jsdx_info", "sheltercode")
    # 验证token
    token = params['token']
    if token == '':
        response['code'] = '0'
        response['msg'] = '缺失token'
        logger.get_log().info(f"[jsdx_shelter_control][msg][缺失token]")
        return Response(json.dumps(response), mimetype='application/json')
    try:
        token_time = int(get_aes().decrypt(token))
        int_now_timestamp = int(time.time()) * 1000
        if math.fabs(int_now_timestamp - token_time) > time_abs:
            response['code'] = '0'
            response['msg'] = 'token过期'
            logger.get_log().info(f"[jsdx_shelter_control][msg][token过期]")
            return Response(json.dumps(response), mimetype='application/json')
    except Exception as e:
        response['code'] = '0'
        response['msg'] = 'token非法'
        logger.get_log().info(f"[jsdx_shelter_control][msg][token非法]")
        return Response(json.dumps(response), mimetype='application/json')
    # 验证 方舱编号
    if sheltercode != params['sheltercode']:
        response['code'] = '0'
        response['msg'] = '方舱编号非法'
        logger.get_log().info(f"[jsdx_shelter_control][msg][方舱编号非法]")
        return Response(json.dumps(response), mimetype='application/json')

    # 执行机库动作
    global webclient
    if params['opertyp'] == 'open':
        print("open")
        result = OperateUtil.operate_hangar("A000")
        logger.get_log().info(f"[jsdx_shelter_control][open][big_scene_A000][{result}]")
        if result != 'A00090000':
            response['code'] = '0'
            response['msg'] = f'预备起飞过程发生异常'
            logger.get_log().info(f"[jsdx_shelter_control][msg][预备起飞过程发生异常][{result}]")
            return Response(json.dumps(response), mimetype='application/json')
    elif params['opertyp'] == 'close':
        print("close")
        result = OperateUtil.operate_hangar("B100")
        logger.get_log().info(f"[jsdx_shelter_control][close][big_scene_B100][{result}]")
        if result != 'B1009000':
            response['code'] = '0'
            response['msg'] = f'降落后续过程发生异常'
            logger.get_log().info(f"[jsdx_shelter_control][msg][降落后续过程发生异常][{result}]")
            return Response(json.dumps(response), mimetype='application/json')
    elif params['opertyp'] == 'reset':
        print("reset")
        result = OperateUtil.operate_hangar("500000")
        logger.get_log().info(f"[jsdx_shelter_control][reset][step_scene_bar_reset_500000][{result}]")
        if result != '9500':
            response['code'] = '0'
            response['msg'] = f'重置后续过程发生异常'
            logger.get_log().info(f"[jsdx_shelter_control][msg][重置后续过程发生异常][{result}]")
            return Response(json.dumps(response), mimetype='application/json')


    else:
        response['code'] = '0'
        response['msg'] = '操作类型非法'
        logger.get_log().info(f"[jsdx_shelter_control][msg][操作类型非法]")
        return Response(json.dumps(response), mimetype='application/json')

    # 返回应答
    logger.get_log().info(f"[jsdx_shelter_control][ok]")
    return Response(json.dumps(response), mimetype='application/json')


if __name__ == "__main__":
    # time.sleep(10)  # wait the system until it  is running
    #  自动充电线程处理对象必然实例化，线程改为必定执行，但内部逻辑改为判断标识决定是否执行
    logger.get_log().info(f"[AutoChargeControl]===启动自动化充电功能线程===")
    # config = Config()
    # 传入日志对象，按照主任务日志打印
    # Config.init_logger(logger)
    configinfo_list = Config.get_websocket_config_info()  # 列表元组的形式
    # if configinfo_list is not None and len(configinfo_list) == 1:
    #     if len(configinfo_list[0]) == 5 and configinfo_list[0][4] != "":  # 天宇的版本,根据是否填写最后一个websocket地址来判定，是不是第三方平台
    #         logger.get_log().info(f"[AutoChargeControl][模式0]启动")
    #         auto_charge = AutoChargeControl(logger)
    #     else:
    #         logger.get_log().info(f"[AutoChargeControl][模式1-1]启动")
    #         auto_charge = AutoChargeControlV1(logger)
    # else:
    #     logger.get_log().info(f"[AutoChargeControl][模式1-2]启动")
    #     auto_charge = AutoChargeControlV1(logger)
    auto_charge = AutoChargeControl(logger)
    thead_auto = threading.Thread(target=auto_charge.start_auto_charge, args=())
    thead_auto.start()

    # 启动flask服务
    # 启动websocket无限连接和消息接收机制
    while True:
        try:
            if webclient is None or webclient.server_service is False:
                webclient = WebSocketUtil(server_addr='ws://124.71.225.193:18088/uav/hangarServer/95091e705eceda57',
                                          logger=logger, auto_charge=auto_charge)

                webclient.start_service()

            else:
                break
        except Exception as e:
            logger.get_log().info(f"服务端启动websocket异常,{e}")
            continue
    logger.get_log().info("webclient已启动，启动webservice")

    # --------------推杆复位---------------------

    # logger.get_log().info("启动推杆复位")
    # reset_machine()

    # 如果启用了空调485通信，则使用监听获取空调状态2023-04-04
    if Config.get_is_aircon485() is True:
        checkAirConState = CheckAirConState(logger)
        checkAirConState.checkAirState()
    if Config.get_is_use_weather() is True:
        if Config.get_is_weather_485() is True:  # 485读取数据
            # 启动一个线程获取天气情况
            logger.get_log().info(f"启动485天气")
            weather_info = WeatherInfo485(logger)
            thead_weather = threading.Thread(target=weather_info.start_get_weather, args=())
            thead_weather.start()
        else:
            # 启动一个线程获取天气情况
            weather_info = WeatherInfo(logger)
            thead_weather = threading.Thread(target=weather_info.startgetinfo, args=())
            thead_weather.start()

    if Config.get_is_gps():
        # 添加PGS信息
        gps_client = None
        # 启动一个线程获取天气情况
        gps_client = GPSInfo(logger)
        if Config.get_gps_type() == "1":
            thead_gps = threading.Thread(target=gps_client.start_get_gps, args=())
            thead_gps.start()
        elif Config.get_gps_type() == "2":
            thead_gps = threading.Thread(target=gps_client.start_get_gps_RTK, args=())
            thead_gps.start()
    # 如果触点充电，启用一个线程,不停的check电池状态
    if Config.get_charge_version() == "wlc":
        if Config.get_wlc_version() == "V1.0":
            charge_client = None
            charge_client = CheckState(logger)
            thead_charge = threading.Thread(target=charge_client.start_check, args=())
            thead_charge.start()
            if Config.get_is_wlc_double_connect():
                charge_listern = None
                charge_listern = JCCListerner(logger)
                thead_charge_listern = threading.Thread(target=charge_listern.start_Listern, args=())
                thead_charge_listern.start()
        else:  # V2.0 or V3.0
            charge_client = None
            charge_client = CheckState(logger)
            thead_charge = threading.Thread(target=charge_client.start_check, args=())
            thead_charge.start()
        # 如果无线充电，启用一个线程,不停的check电池状态，如果是无线充电1.0版本则不进行操作（保持现在的状态），如果是无线充电2.0版本则进行充电操作(默认开启2.0版本)
    elif Config.get_charge_version() == "wfc" and Config.get_wfc_version() == "V2.0" and Config.get_is_wfc_double_connect() is True:
        # 启动监听
        charge_wfc_listerner = None
        charge_wfc_listerner = WFCV2Listerner(logger)
        thead_wfc_charge_listerner = threading.Thread(target=charge_wfc_listerner.start_Listern, args=())
        thead_wfc_charge_listerner.start()

    # 启动MQTT接口对接（为兼容旧版本，一般注释掉）
    if BASEUtile.InitFileTool.get_boolean_value("mqtt_info", "is_run_mqtt"):
        mqtt_type = BASEUtile.InitFileTool.get_str_value("mqtt_info", "mqtt_type")
        if mqtt_type == "dianxin":
            logger.get_log().info("[MQTT]启用MQTT服务，启动MQTT服务[电信定制版]")
            start_mqtt_thread_dx(webclient, logger)
        elif mqtt_type == "jiangsudx":
            logger.get_log().info("[MQTT]启用MQTT服务，启动MQTT服务[江苏电信定制版]")
            start_mqtt_thread_jiangsudx(webclient, logger)
        elif mqtt_type == "hubeidianli":
            logger.get_log().info("[MQTT]启用MQTT服务，启动MQTT服务[湖北电力定制版]")
            start_mqtt_thread_hubeidianli(webclient, logger)
        elif mqtt_type == "nanfangdianwang":
            logger.get_log().info("[MQTT]启用MQTT服务，启动MQTT服务[南方电网定制版]")
            start_mqtt_thread_nanfangdianwang(webclient, logger)
        else:
            logger.get_log().info("[MQTT]启用MQTT服务，启动MQTT服务[自有协议]")
            # TODO 自有MQTT功能入口
    else:
        logger.get_log().info("[MQTT]禁用MQTT服务，无需启动")

    # logger.get_log().info("-----服务启动，空调打开------")
    # start_Aircondition()

    # 初始化配件状态,需要从配置文件中读取
    initHangar = InitHangarState(logger)
    initHangar.init_hangar()

    # #启动夜间自动充电配置
    chargeAtTime = ChargeAtTime(logger)
    # 启动一个线程执行夜间充电
    nigth_charge_thread = threading.Thread(target=chargeAtTime.start_task_thread, args=())
    nigth_charge_thread.start()
    # 警示灯打开线程
    if Config.get_is_alarm_light() is True:
        logger.get_log().info(f"[机库启动]警示灯配置文件alarm:{Config.get_is_alarm_light()},警示绿灯线程开启")
        threading.Thread(target=AlarmLightController.open_light_thread, args=()).start()
    else:
        logger.get_log().info(f"[机库启动]警示灯配置文件alarm:{Config.get_is_alarm_light()},警示绿灯线程无需开启")

    logger.get_log().info("服务开启，完成")
    app.run(host='0.0.0.0', port=8000)
