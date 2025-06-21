import json
import serial
import time
from datetime import datetime


# Function to initiate the serial connection
def init_serial():
    try:
        # Open the serial port once
        serial_port = '/dev/serial0'
        baud_rate = 115200
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        print(f"Connected to {serial_port} at {baud_rate} baud.")
        return ser
    except serial.SerialException as e:
        raise Exception(f"Error opening serial port: {e}")

def set_initiator(channel):
    """
    Reads data from a serial port and saves it as JSON files in the specified folder.
    Returns the first valid (even if all-zero) JSON object received, or None if parsing never succeeded.
    """
    attempts = 5
    uart_str = 'i' + str(channel)
    last_valid_json = None

    try:
        #### PRINT STATEMENTS FOR DELAY DEBUGGING ####
        #print(f"After step 8: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
        ser = init_serial()
        ser.write(uart_str.encode())
        #print(f"After step 9: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
        while attempts > 0:
            #print(f"Na stap 9.a: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            #print(f"Na stap 9.: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
            #print(f"Received: {line}")
            try:
                #print(f"Na stap 9.x: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
                data = json.loads(line)
                #print(f"Na stap 9.xx: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")

                last_valid_json = data  # Store last successfully parsed JSON
                #print(f"Na stap 9.xx: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")

                if all(v == 0 for v in data.get("i_local", [])):
                    attempts -= 1
                    #print("All i_local values are zero — triggering re-measurement.")
                    #print(f"Na stap 9..: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
                    ser.write(uart_str.encode())
                    time.sleep(0.01)
                    continue

                # print(f"Valid data received: {data}")
                return data  # Return first non-zero data

            except json.JSONDecodeError:
                #print(f"Na stap 9.y: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
                attempts -= 1
                print(f"Invalid JSON received: {line} — attempts left: {attempts}")

        print("Too many failed attempts, returning last valid (all-zero) JSON if available.")
        return last_valid_json  # Return last valid zero-data if no better available

    except Exception as e:
        print(f"Error: {e}")
        return None

# Function executed on role Reflector, starts a measurement on the nRF module with role reflector
def set_reflector(channel):
    uart_str = 'r' + str(channel)
    try:
        ser = init_serial()
        try:
            ser.write(uart_str.encode())
            line = ser.readline().decode("utf-8").strip()
            print(f"Received: {line}")
        except Exception as e:
            print(f"Error reading from serial port: {e}")
    except Exception as e:
        print(f"Error opening serial port: {e}")

# Function executed on role None (solely included for debugging) 
def set_none(channel):
    uart_str = 'n' + str(channel)
    try:
        ser = init_serial()
        try:
            ser.write(uart_str.encode())
            line = ser.readline().decode("utf-8").strip()
            print(f"Received: {line}")
        except Exception as e:
            print(f"Error reading from serial port: {e}")
    except Exception as e:
        print(f"Error opening serial port: {e}")