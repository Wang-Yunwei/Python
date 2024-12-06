import random

from paho.mqtt import client as mqtt_client

# topic = "python_mqtt"
# topic = "wkzn/JIKUPI/topic/command_feedback/#"
topic = "wkzn/JIKUPI/topic/execute_command/#"
client_id = "subMyselfMqtt"

'''
测试用代码
'''


def connect_mqtt() -> mqtt_client:
    # 连接MQTT服务器
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            subscribe(client)
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    # broker = 'broker.emqx.io'
    # port = 1883
    # client.connect(broker, port)
    client.connect(host='456o607o25.imdo.co', port=38807)

    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        data = msg.payload.decode()
        print('订阅【{}】的消息为：{}'.format(msg.topic, data))

    client.subscribe(topic, qos=2)
    # client.publish(topic, "收到", qos=2)  # TODO 测试
    client.on_message = on_message


def run():
    client = connect_mqtt()

    # subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
