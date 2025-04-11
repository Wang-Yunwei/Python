import random
import time
import json
import threading

from paho.mqtt import client as mqtt_client

# topic = 'python_mqtt'  # 发布的主题，订阅时需要使用这个主题才能订阅此消息

# 发布的主题，订阅时需要使用这个主题才能订阅此消息
topic = "wkzn/JIKUPI/topic/execute_command/test"  # 机巢协议对接
# topic = "wkzn/JIKUPI/topic/execute_command/"  #

# 随机生成一个客户端id
client_id = "pubMyselfMqtt"

'''
测试用代码
'''

topic_subscribe_list = [
    (f"wkzn/JIKUPI/topic/execute_command/test", 2)
]


def connect_mqtt():
    # 连接mqtt服务器
    def on_connect(client, userdata, flags, rc, props):  # mqtt2.0以上版本
        # def on_connect(client, userdata, flags, rc):  # mqtt2.0以下版本
        if rc == 0:
            print(
                f"[connect_mqtt.on_connect]Connected to MQTT Broker!userdata:{userdata},flags:{flags},rc:{rc},props:{props}")
            # print(
            #     f"[connect_mqtt.on_connect]Connected to MQTT Broker!userdata:{userdata},flags:{flags},rc:{rc}")
            subscribe(client)  # 必须放此处，因为重连走此步骤
        else:
            print("[connect_mqtt.on_connect]Failed to connect, return code %d\n", rc)

    def on_connect_fail(client, userdata, msg):
        print(f"[on_connect_fail]已经断开连接:{msg}")

    def on_disconnect(client, userdata, rc):
        print(f"[on_disconnect]已经断开连接:{rc}")
        if rc != 0:
            client.reconnect_delay_set(min_delay=10, max_delay=120)
            client.reconnect()

    is_run = False
    while not is_run:
        try:
            print("[循环打开mqtt连接]打开连接-开始")
            client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id)  # mqtt2.0以上版本
            # client = mqtt_client.Client(client_id)  # mqtt2.0以下版本
            client.on_connect = on_connect
            client.on_connect_fail = on_connect_fail
            client.on_disconnect = on_disconnect
            client.reconnect_delay_set(min_delay=10, max_delay=120)
            # client.username_pw_set("pilot", "pilot123")
            # client.connect(host='123.249.125.73', port=18383)
            client.username_pw_set("admin", "admin")
            client.connect(host='127.0.0.1', port=1883)
            client.on_message = on_message
            is_run = True
            print("[循环打开mqtt连接]打开连接-结束")
        except Exception as e:
            print(f"[connect_mqtt]]异常:{e}")
            time.sleep(2)  # 休眠10秒之后重新创建链接
    return client


def subscribe(client: mqtt_client):
    print("[subscribe]")
    client.subscribe(topic_subscribe_list, qos=2)

    # def on_message(client, userdata, msg):
    #     print(f"[subscribe.on_message]userdata:{userdata},msg:{msg},{msg.topic},{msg.payload.decode()}")
    #
    # client.on_message = on_message


def on_message(client, userdata, msg):
    print(f"[on_message]userdata:{userdata},msg:{msg},{msg.topic},{msg.payload.decode()}")


def publish(client):
    while True:
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
        time.sleep(10)


def run():
    # 第一种方法,client.loop_start()这样就是订阅消息单启个线程，发布消息放到主线程里
    client = connect_mqtt()
    client.loop_start()  # 启动一个线程，处理消息的接收和处理
    publish(client)
    client.loop_forever()

    # 第二种方法,发布消息单启一个线程，订阅消息在主线程中
    # client = connect_mqtt()
    # threading.Thread(target=publish, args=(client,), daemon=True).start()
    # client.loop_forever()


if __name__ == '__main__':
    # test = [1, 2, 3, 4, 5, 6, 7]
    # print(test[-2])
    # threading.Thread(target=run, args=(), daemon=True).start()
    run()
    time.sleep(200)
    # time.sleep(60)
