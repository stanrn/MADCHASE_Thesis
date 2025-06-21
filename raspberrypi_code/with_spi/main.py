import paho.mqtt.client as mqtt
from client import set_initiator, set_reflector, set_none
from datetime import datetime
import json


role = 0
number = 1

def take_measurement(client, role,channelnum,broadcast = False):
    if role == 0:
        print("This Raspberry pi will not take part in the measurement.")
        set_none(channel=channelnum)
    elif role == 1:
        print(f"Na stap 6: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
        #print("This Raspberry pi will be the initiator of the measurement.")
        data = set_initiator(channel=channelnum)
        print(f"Na stap 10: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
        payload = json.dumps(data)
        # Publishing measurement result to server
        if broadcast:
            client.publish("results/" + str(number), payload.encode("utf-8"), qos=0)
        else:
            client.publish("measurements/results/" + str(number), payload.encode("utf-8"),qos=0)
            print(f"Na stap 11: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")

        #print(f"Published measurement results to topic 'measurements/results/{number}': {payload}")
    elif role == 2:
        #print("This Raspberry pi will be the reflector of the measurement.")
        set_reflector(channel=channelnum)
    else:
        print("Invalid role")


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe("measurements/start/" + str(number))  # Listen for start
    client.subscribe("measure/" + str(number))  # Listen for start
    client.subscribe("active")  # Listen for active call

def on_message(client, userdata, msg):
    print(f"Na stap 3: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
    global role
    message = msg.payload.decode()
    print(f"Received from {msg.topic}: {message}")
    if msg.topic == "measure/" + str(number):
        role = int(message.split("/")[0])
        channelfreq = int(message.split("/")[1])
        client.publish("measurements/start", f"Raspberry Pi " + str(number) + " started!")
        take_measurement(client, role,channelnum=channelfreq,broadcast = True)
    elif msg.topic == "measurements/start/" + str(number):
        print(f"Na stap 4: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
        role = int(message.split("/")[0])
        channelfreq = int(message.split("/")[1])
        print(f"Role: {role}")
        client.publish("measurements/start",f"Raspberry Pi " + str(number) + " started!")
        print(f"Na stap 5: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
        take_measurement(client, role,channelnum=channelfreq)
    # Listen for active call for broadcast
    elif msg.topic == "active":
        client.publish("active/" + str(number),"true")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("13.61.21.210", 1883, 60)

client.loop_forever()  # Keep listening for messages
