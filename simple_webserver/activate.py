import time
from datetime import datetime
from itertools import combinations
import paho.mqtt.client as mqtt

from connect import get_active_rpis, roles
from shared import expected_measurements, received_measurements, batch_done, stop_event

"""
This module contains the core logic used for performing continuous, 
coordinated channel sounding measurements in a distributed RF system.

The two main functions are:

- `batch_pairs(pairs)`: Groups non-overlapping node pairs into batches so that multiple measurements 
  can be performed in parallel without interference.

- `activate_nodes(client, interval_time)`: Continuously retrieves active nodes, forms measurement 
  pairs, batches them, and triggers simultaneous measurements via MQTT. It also tracks measurement 
  status and verifies result collection in real time.

These functions are called as part of the continuous measurement routine 
and assume that MQTT communication and node-side response handling are already implemented.
"""

# Split device pairs into batches with no overlapping devices
def batch_pairs(pairs):
    batches = []
    remaining = pairs[:]

    while remaining:
        active_devices = set()
        batch = []
        new_remaining = []

        for pair in remaining:
            if pair[0] not in active_devices and pair[1] not in active_devices:
                batch.append(pair)
                active_devices.update(pair)
            else:
                new_remaining.append(pair)

        batches.append(batch)
        remaining = new_remaining
    return batches

# Main loop to continuously activate nodes and trigger measurements
def activate_nodes(client,interval_time):
    while not stop_event.is_set(): # Event can be activated by user from frontend
        # Making and sorting list of active nodes
        active_rpis = list(get_active_rpis().keys())
        active_rpis.sort()
        print(f"Active Raspberry pi's: {active_rpis}")

        # Generate all possible node pairs (n < m)
        device_pairs = list(combinations(active_rpis,2))
        print(f"Possible pairs: {device_pairs}")

        # Group non-overlapping pairs into parallelizable batches
        batches = batch_pairs(device_pairs)
        print("Batches: " + ", ".join([f"Batch {i+1}: {batch}" for i, batch in enumerate(batches)])) # Printing all batches before starting iteration

        # Iterate over all batches
        for i, batch in enumerate(batches):
            print(f"Batch {i+1}: {batch}")

            # Prepare expected/received measurement tracking
            global expected_measurements
            global received_measurements
            expected_measurements.clear()
            expected_measurements.update(pair for pair in batch)
            received_measurements.clear()            
            print("Expected measurements:" + str(expected_measurements))
            print("Empty received measurements:" + str(received_measurements))

            
            batch_done.clear() # Clear event for batch done tracking
            freq_channel = 10  # Starting frequency channel for hopping sequences           
            
            print(f"Begin measurement: {datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")}") # Timestamp print for delay measurement
            # Iterate over all pairs in current batch
            for pair in batch:
                # Building MQTT messages with role and channel value for frequency hopping
                message_i = f"{roles["Initiator"]}/{freq_channel}"
                message_r = f"{roles["Reflector"]}/{freq_channel}"

                # Sending MQTT messages to Initiator/Reflector
                client.publish("measure/" + pair[0],message_i)
                client.publish("measure/" + pair[1],message_r)
                
                freq_channel += 1 # Ensure unique frequency channel per measurement
           
            batch_done.wait(timeout=3) # Waiting until result received or 3 seconds

            # Check if all results were received in the 3 second timeframe
            if not batch_done.is_set():
                print("⚠️  Not all measurements received in time!")
            else:
                print("✅ All measurements received successfully.")
        time.sleep(interval_time) # Wait for user set interval time

