import random
import time
import json

from paho.mqtt import client as mqtt_client

# topic = 'python_mqtt'  # 发布的主题，订阅时需要使用这个主题才能订阅此消息

# 发布的主题，订阅时需要使用这个主题才能订阅此消息
topic = "wkzn/JIKUPI/topic/execute_command/HEISHAD1352023010500001"  # 机巢协议对接
# topic = "wkzn/JIKUPI/topic/execute_command/"  #

# 随机生成一个客户端id
client_id = "pubMyselfMqtt"

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
    client.connect(host='456o607o25.imdo.co', port=38807)
    return client


def publish(client):
    # 发布消息
    msg_count = 0
    msg_str = "140000"
    print(f"主题【{topic}】发送报文【{msg_str}】")
    # print(type(json.dumps(msg_obj)))
    result = client.publish(topic, msg_str, qos=0)
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
    # client.loop_forever()


if __name__ == '__main__':
    test = [1, 2, 3, 4, 5, 6, 7]
    print(test[-2])

    run()
    # time.sleep(60)
