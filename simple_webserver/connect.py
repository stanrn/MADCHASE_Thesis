import time
import json
from threading import Event
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import paho.mqtt.client as mqtt

from filehandler import handle_files, convert_svg_png
from dataprocessing import DataPlotter
from dataextraction import extract_cfr_from_json
from flask_socketio import SocketIO, emit
from shared import expected_measurements, received_measurements, batch_done

"""
This module handles MQTT communication, message processing, and frontend data transmission
for the distributed channel sounding system. It processes incoming measurement results,
tracks active Raspberry Pi nodes, and transmits parsed data to the frontend via Socket.IO.

Key functionalities:
- Subscribing to MQTT topics for measurement results and active node detection.
- Parsing and storing incoming measurement results.
- Coordinating individual measurement requests.
- Periodically checking active nodes and updating the frontend.
- Sending parsed measurement data to the frontend in real time.
"""

# Global variables
title = "" # Title set by user for current measurement session
last_seen = {} # Tracks last-seen timestamps of Raspberry Pis
last_measurements = [] # Stores latest measurements to be sent to frontend

# Creating a dictionary for the roles
roles = {
    "None": 0,
    "Initiator": 1,
    "Reflector": 2
}

# function to connect the server to the MQTT broker on the private IP adress and port 1883
def connect_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("172.31.34.18", 1883, 60)
    return client # Client instance is passed back

# Process to disconnect from the MQTT broker
def disconnect_mqtt(client):
    client.loop_stop()

# Process executed on connection with MQTT broker
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe("measurements/results/#")  # Listen for results
    client.subscribe("measurements/start") # Listen for raspberry pi's starting
    client.subscribe("active/#") # Listen for active Raspberry Pi's
    client.subscribe("results/#") # Listen for all broadcast results

# Callback function for incoming MQTT messages
def on_message(client, userdata, msg):
    # Specify usage of the global variables for title and the expected measurements set by the activate_nodes function
    global title
    global expected_measurements

    # Decoding payload
    message = msg.payload.decode("utf-8")
    message_topic = msg.topic

    # When incoming measurements from continuous measuring
    if message_topic.startswith("results/"):
        # Parsing devide id from sent node
        device_id = message_topic.split("/")[-1]
        print(f"End of measurement: {datetime.now(ZoneInfo("Europe/Brussels")).strftime("%d-%m-%Y %H:%M:%S.%f")}")

        # Trying to parse JSON, exception when no valid JSON is received
        try:
            # Parsing JSON and extracting data
            message_json = json.loads(message)
            result = extract_cfr_from_json(data=message_json,tx_id=int(device_id),rx_id = int(next(rx for (tx, rx) in expected_measurements if tx == device_id))) # Extracts transmitter and receiver
        
            # Further processing of result
            last_measurements.append(result) # Adding result to shared list to be sent to fromtend
            received_measurements.append(device_id) # Updating received measurements list
            print("Received measurements: " + str(set(received_measurements)))
            print("Expected measurements: " + str((expected_measurements)))

            # Check if all expected results are received
            transmitting_nodes = {tx for (tx, _) in expected_measurements}
            if transmitting_nodes == set(received_measurements):
                batch_done.set() # This triggers starting measurements of next batch
            
        except Exception as e:
            result = None
            print("Error handling MQTT message:", e)

    # When incoming single measurements
    elif message_topic.startswith("measurements/results/"):
        print(f"End of measurement: {datetime.now(ZoneInfo("Europe/Brussels")).strftime("%d-%m-%Y %H:%M:%S.%f")}")

        # Getting file path from user title (Making folders)
        data_file_path, timestamped_folder = handle_files(title)

        # Trying to open the file to write measurement data, exception when this fails
        try:
            #Open the file for writing data
            with open(data_file_path, "w") as file:
                file.write(message)
            
            # Plotting data in graphs with class DataPlotter
            print(f"Plotting data for {data_file_path}")
            plotter = DataPlotter(data_file_path, timestamped_folder)
            plotter.plot_data()

            # Converting svg files to png to show to user later
            convert_svg_png(timestamped_folder)

        except IOError as e:
            print(f"Error writing to file {data_file_path}: {e}")

    # Keeping track of active RPIs
    elif message_topic[:-1] == "active/":
        last_seen[message_topic[-1]] = datetime.now()
        #print(f"Active node {message_topic[-1]} detected!\n")

# Checking every 5 seconds which RPIs are still active
def detect_active_rpis(client,socketio:SocketIO):
    while True:
        #print(f"Active nodes: {list(last_seen.keys())}\n")
        now = datetime.now()
        for rpi, timestamp in list(last_seen.items()):
            # RPi's inactive for more then 6 seconds get deleted
            if now - timestamp > timedelta(seconds = 6):
                del last_seen[rpi]
        client.publish("active",1)
        time.sleep(5)
        socketio.emit('rpi_list', list(last_seen.keys()), broadcast=True)

# Function that returns the set of active RPis
def get_active_rpis():
    return last_seen

# Function to start a single measurement with function being initiator or reflector or None
def setup_rpi(client,channel,function,freq_channel = 40):
    message = f"{function}/{freq_channel}"

    # Publishing start command to MQTT topic
    client.publish("measurements/start/" + str(channel),message,qos=0)
    #print(f"After step 1...: {datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")}")

# Function to all involved nodes of a singe measurement
def setup_rpis(client,order):
    print(f"Start measuring: {datetime.now(ZoneInfo("Europe/Brussels")).strftime("%d-%m-%Y %H:%M:%S.%f")}")
    setup_rpi(client, order[0], roles["Reflector"])
    setup_rpi(client, order[1], roles["Initiator"])
    setup_rpi(client, 3, roles["None"]) 
    #print(f"After step 2: {datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")}")

# Function activated when user chooses to do a single channel measurement
def server_loop(client,title_sent,initiator,reflector):
    # Title and node roles are extracted
    global title 
    title=title_sent
    init_index = initiator
    reflect_index = reflector
    order = [reflect_index,init_index]
    #print(f"Measurement started between Initiator: (node {init_index}) and Reflector (node {reflect_index})!")
    setup_rpis(client,order) # Setup all involved nodes

# Function to send the last measurement results to the frontend, is constantly running in the background
def send_measurements(socketio):
    while True:        
        if(last_measurements):
            try:
                time.sleep(0.1)
                new_measurement = last_measurements.pop(0)
                measurement = {
                    'transmitter': "Node " + str(new_measurement['tx_id']),
                    'receiver': "Node " + str(new_measurement['rx_id']),
                    'timestamp': new_measurement['timestamp'],
                    'link_loss': new_measurement['link_loss_dB'],
                    'delay': new_measurement['delay_spread_ns'],
                    'distance': new_measurement['estimated_distance_mm'],
                    'quality' : new_measurement['quality']
                }
                socketio.emit('new_data', measurement)
            except TypeError as e:
                print(f"Error formatting measurement: {e} | Value: {new_measurement}")
        time.sleep(0.1)  # Sends each 0.1 seconds 1 measurement to frontend