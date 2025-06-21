import paho.mqtt.client as mqtt
from client import set_initiator, set_reflector, set_none
import json

# Role definitions:
# 0 = None (no participation)
# 1 = Initiator (starts measurement)
# 2 = Reflector (responds in measurement)
role = 0 # Initial role is None

number = 1 # <device id> --> needs to be changed manually for each node

# Perform measurement based on role and channel number
def take_measurement(client, role,channelnum,broadcast = False):
    if role == 0:
        print("This Raspberry pi will not take part in the measurement.")
        set_none(channel=channelnum)
    elif role == 1:
        print("This Raspberry pi will be the initiator of the measurement.")
        data = set_initiator(channel=channelnum)
        payload = json.dumps(data)
        # Publishing measurement result to server (broadcast variable decides if this is a single measurement or part of a continuous measurement)
        if broadcast:
            client.publish("results/" + str(number), payload.encode("utf-8"), qos=1)
        else:
            client.publish("measurements/results/" + str(number), payload.encode("utf-8"),qos=1)
        print(f"Published measurement results to topic 'measurements/results/{number}': {payload}")
    elif role == 2:
        print("This Raspberry pi will be the reflector of the measurement.")
        set_reflector(channel=channelnum)
    else:
        print("Invalid role")

# Callback function on connection to the MQTT broker, subscribes to the correct topics
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe("measurements/start/" + str(number))  # Listen for start
    client.subscribe("measure/" + str(number))  # Listen for start
    client.subscribe("active")  # Listen for active call

# Callback function activated on incoming message
def on_message(client, userdata, msg):
    global role
    message = msg.payload.decode()
    print(f"Received from {msg.topic}: {message}")
    # Depending on topic, a measurement is executed either as a single measurement or as part of a continuous measurement
    if msg.topic == "measure/" + str(number):
        role = int(message.split("/")[0])
        channelfreq = int(message.split("/")[1])
        client.publish("measurements/start", f"Raspberry Pi " + str(number) + " started!")
        take_measurement(client, role,channelnum=channelfreq,broadcast = True)
    elif msg.topic == "measurements/start/" + str(number):
        role = int(message.split("/")[0])
        channelfreq = int(message.split("/")[1])
        print(f"Role: {role}")
        client.publish("measurements/start",f"Raspberry Pi " + str(number) + " started!")
        take_measurement(client, role,channelnum=channelfreq)
    # Listen for active call for broadcast
    elif msg.topic == "active":
        client.publish("active/" + str(number),"true")
        #print(f"Confirming active status of node {number} to server!")

# MQTT setup code, connecting to the public!! IP adress of the server
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("13.53.200.83", 1883, 60)

client.loop_forever()  # Keep listening for messages 
