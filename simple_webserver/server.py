import paho.mqtt.client as mqtt
import time
import os
import threading

from filehandler import get_image_folder,make_zip,check_permissions
from connect import connect_mqtt,server_loop,detect_active_rpis,send_measurements,disconnect_mqtt
from activate import activate_nodes
from shared import stop_event
from flask import Flask, send_from_directory,render_template,jsonify, request
from flask_socketio import SocketIO, emit

# Flask and socketIO setup
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
abs_path = ""

# MQTT connection setup
client = connect_mqtt()
client.loop_start()  # Start non-blocking loop
time.sleep(2)  # Wait to ensure connection is established

# Start Flask & socketio background thread
@socketio.on('connect')
def on_connect():
    print("Client connected.")

# Starting page GUI
@app.route('/')
def hello():
    return render_template('index.html', message='Control bluetooth modules')

# API-endpoint for starting a broadcast measurement
@app.route('/broadcast', methods=['POST'])
def start_broadcast():
    interval_time = float(request.form.get('interval'))
    stop_event.clear()

    # Starting continuous node measurements in a new thread
    threading.Thread(target=activate_nodes,args=(client,interval_time,)).start()

    return render_template('broadcast.html',interval = interval_time)

# API-endpoint for stopping a broadcast measurement
@app.route('/broadcast_stop', methods=['POST'])
def stop_broadcast():
    stop_event.set()
    return jsonify({'status': 'ok'}), 200


# API-endpoint for configure page when single measurement starts
@app.route('/configure', methods=['POST'])
def configure():
    title = request.form.get('title')
    initiator = request.form.get('initiator')
    reflector = request.form.get('reflector')

    # Starting single measurement, showing configuration page
    server_loop(client,title,int(initiator[-1]),int(reflector[-1]))

    return render_template(
        'configure.html',
        title = title,
        initiator=initiator,
        reflector=reflector,
    )

# API-endpoint for the result page of a single measurement
@app.route('/results', methods=['POST'])
def results():
    global abs_path
    # Get the image folder from file handler
    image_folder = get_image_folder()

    # Extract the needed folder link
    index = image_folder.find("/png")
    if index != -1:
        result = image_folder[:index]
    abs_path = result

    # Get image file names
    image_files = [f for f in os.listdir(image_folder) if f.endswith('.png')]

    # Check permissions on first file in directory
    check_permissions(os.path.join(image_folder,image_files[0]))

    # Return the filled in template
    return render_template(
        'results.html',
        folder = result,
        image_files=image_files
    )

# API-endpoint for sending folder path to frontend
@app.route('/<folder>/<filename>')
def send_image(folder, filename):
    global abs_path
    full_path = os.path.join(abs_path,folder) 
    if os.path.exists(full_path):
        return send_from_directory(full_path,filename)
    else:
        return "Folder not found", 404
    
# API-endpoint for sending files to frontend
@app.route('/<filename>')
def download_file(filename):
    global abs_path
    make_zip(abs_path)
    if os.path.exists(abs_path):
        return send_from_directory(abs_path,filename)
    else:
        return "Folder not found", 404

if __name__ == '__main__':
    # Starting send measurements function in seperate thread
    threading.Thread(target=send_measurements, args=(socketio,)).start()    
    
    # Starting detection of active nodes in seperate thread
    threading.Thread(target=detect_active_rpis, args=(client,socketio,)).start()
    
    # Starting web interface on port 5000 accessible for users
    socketio.run(app, host='0.0.0.0', port=5000)    
