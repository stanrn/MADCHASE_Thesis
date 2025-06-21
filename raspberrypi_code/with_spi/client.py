import json
import serial
import time
import spidev
from datetime import datetime



def init_serial():
    try:
        # Open the serial port once
        serial_port = '/dev/serial0'
        baud_rate = 115200
        ser = serial.Serial(serial_port, baud_rate, timeout=0.1)
        print(f"Connected to {serial_port} at {baud_rate} baud.")
        return ser
    except serial.SerialException as e:
        raise Exception(f"Error opening serial port: {e}")

def init_spi():
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 8000000
    spi.mode = 0b00
    return spi

def send_command(command, response_length=10):
    spi = init_spi()
    time.sleep(0.5)
    tx = list(command.encode("utf-8")) + [0] * (response_length - len(command))
    print(tx)
    rx = spi.xfer2(tx)
    response = bytes(rx).decode("utf-8", errors='ignore')
    return response.strip('\x00')


def set_initiator(channel):
    """
    Reads data from a serial port and saves it as JSON files in the specified folder.
    Returns the first valid (even if all-zero) JSON object received, or None if parsing never succeeded.
    """
    print(f"Na stap 7: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
    attempts = 5
    uart_str = 'i' + str(channel)
    last_valid_json = None
    #time.sleep(0.01)
    try:
        print(f"Na stap 8: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
        ser = init_serial()
        ser.write(uart_str.encode())
        send_command("START")
        time.sleep(0.05)
        print(f"Na stap 9: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
        while attempts > 0:
            print(f"Na stap 9.a: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            print(f"Na stap 9.: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
            print(f"Received: {line}")
            try:
                print(f"Na stap 9.x: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
                data = json.loads(line)
                print(f"Na stap 9.xx: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")

                last_valid_json = data  # Store last successfully parsed JSON
                print(f"Na stap 9.xx: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")

                if all(v == 0 for v in data.get("i_local", [])):
                    attempts -= 1
                    print("All i_local values are zero — triggering re-measurement.")
                    print(f"Na stap 9..: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
                    ser.write(uart_str.encode())
                    time.sleep(0.01)
                    continue

                #print(f"Valid data received: {data}")
                return data  # Return first non-zero data

            except json.JSONDecodeError:
                print(f"Na stap 9.y: {datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')}")
                attempts -= 1
                print(f"Invalid JSON received: {line} — attempts left: {attempts}")

        print("Too many failed attempts, returning last valid (all-zero) JSON if available.")
        return last_valid_json  # Return last valid zero-data if no better available

    except Exception as e:
        print(f"Error: {e}")
        return None


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


def set_none(channel):
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