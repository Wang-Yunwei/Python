import random
import time
import json

from paho.mqtt import client as mqtt_client

# topic = 'python_mqtt'  # 发布的主题，订阅时需要使用这个主题才能订阅此消息

# 发布的主题，订阅时需要使用这个主题才能订阅此消息
topic = "uavshelter/devicecontral/FC-LIANYUNGANG-010/shelterdoor"  # 4.1. 方舱舱门控制
# topic = "uavshelter/devicecontral/FC-LIANYUNGANG-010/centerdevice"  # 4.2. 归中装置控制
# topic = "uavshelter/devicecontral/FC-LIANYUNGANG-010/airconditioner"  # 4.3. 空调控制
# topic = "uavshelter/devicecontral/FC-LIANYUNGANG-010/chargingdevice"  # 4.5. 充电控制
# topic = "uavshelter/devicecontral/FC-LIANYUNGANG-010/uavcontral"  # 4.6. 无人机控制
# topic = "uavshelter/devicecontral/FC-LIANYUNGANG-010/edit"  # 4.7.2. 修改方舱信息（操控系统_发布） # 4.7.1. 查询方舱信息 能做多少做多少 4.7.4. 查询方舱状态 能做多少做多少
# topic = "uavshelter/devicecontral/FC-LIANYUNGANG-010/readyforflight"  # 4.8. 起降控制 # 4.8.4. 查询预备起飞状态不实现  4.8.7. 查询预备降落状态不实现 4.8.11.查询降落关舱状态不实现
# topic = "uavshelter/devicecontral/FC-LIANYUNGANG-010/security"  # 4.9. 安全控制 # 机场复位支持(推杆复位 空调开机)，机场急停不支持
# topic = "uavshelter/devicecontral/FC-LIANYUNGANG-010/rccontral"  # 4.10.遥控器控制  # 暂不支持该功能
# topic = "uavshelter/devicecontral/FC-LIANYUNGANG-010/nightlanding"  # 4.11.夜间降落控制 # 暂不支持该功能，目前只有一款支持
# 随机生成一个客户端id
client_id = "pub"

'''
测试用代码
'''


def connect_mqtt():
    # 连接mqtt服务器
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    # broker = 'broker.emqx.io'
    # port = 1883
    # client.connect(broker, port)
    client.connect(host='127.0.0.1', port=1883)
    return client


def publish(client):
    # 发布消息
    msg_count = 0
    # while True:
    #
    #     time.sleep(1)
    #     msg = '这是客户端发送的第{}条消息'.format(msg_count)
    #     result = client.publish(topic, msg, qos=2)
    #     status = result[0]
    #     if status == 0:
    #         print('第{}条消息发送成功'.format(msg_count))
    #     else:
    #         print('第{}条消息发送失败'.format(msg_count))
    #         print(f"status={status}")
    #     msg_count += 1

    msg_obj = {
        "msgType": "0",
        "msgCode": "1001",
        "msgExplain": "xxxx",
        "data": {}
    }

    # 7002 edit接口特有报文
    # msg_obj = {
    #     "msgType": "0",
    #     "msgCode": "7002",
    #     "msgExplain": "xxxx",
    #     "data": {
    #         "serialNumber": "SQDX-FC-2022111701",
    #         "type": "SQDX-FCV1.0",
    #         "adapter": "大疆 M300",
    #         "adress": "电信大楼",
    #         "alternatePoint": "118.232,54.154",
    #         "doorSpeed": "50", "centerSpeed": "50",
    #         "mqttHost": "0.0.0.0",
    #         "mqttPort": "1883",
    #         "mqttUserName": "",
    #         "mqttPassWord": ""}
    # }
    # print(msg_obj)
    print(f"主题【{topic}】发送报文【{json.dumps(msg_obj)}】")
    # print(type(json.dumps(msg_obj)))
    result = client.publish(topic, json.dumps(msg_obj), qos=2)
    status = result[0]
    if status == 0:
        print('第{}条消息发送成功'.format(msg_count))
    else:
        print('第{}条消息发送失败'.format(msg_count))
        print(f"status={status}")


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    test = [1, 2, 3, 4, 5, 6, 7]
    print(test[-2])

    run()
    # time.sleep(60)
