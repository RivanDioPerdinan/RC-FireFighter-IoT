from flask import Flask, render_template, jsonify, request, Response
import random
import cv2  # Import OpenCV
import paho.mqtt.client as mqtt  # Import paho-mqtt
from flask_socketio import SocketIO, emit
import requests  # Import requests for API calls
from time import sleep
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Inisialisasi Flask-SocketIO

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"  # Ganti dengan broker MQTT Anda
MQTT_PORT = 1883
MQTT_TOPIC_CONTROL = "rc/control"
MQTT_TOPIC_POMPA = "rc/pompa"
MQTT_TOPIC_STROBO = "rc/strobo"

# Monitoring Topics
TOPIC_WATERLEVEL = "rc/waterlevel"
TOPIC_BATTERY = "rc/baterailevel"
TOPIC_SPEED = "rc/speed"
TOPIC_NOTIFICATION = "rc/notification"

# Global variables for monitoring data
monitoring_data = {
    "waterlevel": None,
    "battery": None,
    "speed": None,
    "notification": None
}
# API Configuration
API_BASE_URL = "http://api.shidiq.com"
API_KEY = "apikeydarilangit"

# Create MQTT client
mqtt_client = mqtt.Client()

# Fungsi callback untuk debugging MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        # Subscribe to monitoring topics
        mqtt_client.subscribe([(TOPIC_WATERLEVEL, 0), (TOPIC_BATTERY, 0), 
                               (TOPIC_SPEED, 0), (TOPIC_NOTIFICATION, 0)])
    else:
        print(f"Failed to connect to MQTT Broker, return code {rc}")

def on_message(client, userdata, msg):
    global monitoring_data
    # Update monitoring data based on topic
    if msg.topic == TOPIC_WATERLEVEL:
        monitoring_data["waterlevel"] = msg.payload.decode('utf-8')
    elif msg.topic == TOPIC_BATTERY:
        monitoring_data["battery"] = msg.payload.decode('utf-8')
    elif msg.topic == TOPIC_SPEED:
        monitoring_data["speed"] = msg.payload.decode('utf-8')
    elif msg.topic == TOPIC_NOTIFICATION:
        monitoring_data["notification"] = msg.payload.decode('utf-8')

    # Kirim data real-time ke klien melalui WebSocket
    print(f"Emitting data to WebSocket: {monitoring_data}")
    socketio.emit('update_monitoring', monitoring_data)
    print(f"Received message from {msg.topic}: {msg.payload.decode('utf-8')}")

def on_publish(client, userdata, mid):
    print(f"Message published with mid {mid}")

# Set MQTT callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_publish = on_publish

# Connect to MQTT broker
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()  # Start MQTT loop

# Function to fetch monitoring data from API
def fetch_monitoring_data():
    endpoints = {
        "post": f"{API_BASE_URL}/post",
        "get_all": f"{API_BASE_URL}/get_all",
        "get_max": f"{API_BASE_URL}/get_max",
        "get_min": f"{API_BASE_URL}/get_min",
        "get_avg": f"{API_BASE_URL}/get_avg",
    }

    headers = {"API-Key": API_KEY}
    results = {}

    try:
        # Fetch data from all endpoints
        for key, url in endpoints.items():
            if key == "post":
                response = requests.post(url, params={"speed": 50, "battery": 79}, headers=headers)
            else:
                response = requests.get(url, headers=headers)

            if response.status_code == 200:
                results[key] = response.json()
            else:
                results[key] = {"error": f"Failed to fetch data from {key}"}

    except Exception as e:
        results = {"error": str(e)}

    return results

# Function to generate monitoring data
def generate_monitoring_data():
    global monitoring_data
    return {
        "waterlevel": monitoring_data["waterlevel"],
        "battery": monitoring_data["battery"],
        "speed": monitoring_data["speed"],
        "notification": monitoring_data["notification"]
    }


# Route to update data in real-time
@app.route('/update_data')
def update_data():
    data = generate_monitoring_data()
    return jsonify(data)

@app.route('/monitoring')
def dashboard():
    # Fetch data from API
    api_data = fetch_monitoring_data()

    # Combine API data and MQTT data
    data = {
        "mqtt_data": monitoring_data,
        "api_data": api_data
    }
    print(data)
    return render_template('dashboard.html', data=data)

@app.route('/check-monitoring')
def check_monitoring():
    return jsonify(fetch_monitoring_data())


@app.route('/sensor-data')
def sensor_data():
    data = generate_monitoring_data()
    return jsonify(data)

@app.route('/controlling')
def controlling():
    data = generate_monitoring_data()
    return render_template('controlling.html', data=data)

@app.route('/')
def profile():
    people = [

        {'profile_picture': '/static/images/raya.png', 'name': 'Muhammad Raya Fathaya', 'NRP': '15-2022-004'},
        {'profile_picture': '/static/images/shidiq.png', 'name': 'Shidiq Nur Hasan', 'NRP': '15-2022-016'},
        {'profile_picture': '/static/images/sadira.png', 'name': 'Sadira Amalina', 'NRP': '15-2022-018'},
        {'profile_picture': '/static/images/fadhil.png', 'name': 'Fadhil Teguh Amara', 'NRP': '15-2022-020'},
        {'profile_picture': '/static/images/jabir.png', 'name': 'Jabir Muhammad Nizar', 'NRP': '15-2022-021'},
        {'profile_picture': '/static/images/fajar.png', 'name': 'Fajar Faturohman', 'NRP': '15-2022-034'},
        {'profile_picture': '/static/images/farel.png', 'name': 'Farel Anugrah Al Fauzan', 'NRP': '15-2022-042'},
        {'profile_picture': '/static/images/dio.png', 'name': 'Rivan Dio Perdinan', 'NRP': '15-2022-048'},
        {'profile_picture': '/static/images/abhyasa.png', 'name': 'Abhyasa Gunawan Yusuf', 'NRP': '15-2022-087'},
        {'profile_picture': '/static/images/sakha.png', 'name': 'Muhammad Sakha Sandia', 'NRP': '15-2022-152'},
        {'profile_picture': '/static/images/dadan.png', 'name': 'Dadan Ramdani', 'NRP': '15-2022-153'},
    ]
    return render_template('profile.html', people=people)


@app.route('/control-car', methods=['GET'])
def control_car():
    direction = request.args.get('direction')
    mqtt_message = ""
    mqtt_topic = MQTT_TOPIC_CONTROL  # Default topic

    # Map direction to MQTT message and topic
    if direction == "W":
        mqtt_message = "forward"
    elif direction == "A":
        mqtt_message = "left"
    elif direction == "D":
        mqtt_message = "right"
    elif direction == "S":
        mqtt_message = "backward"
    elif direction == "X":
        mqtt_message = "stop"
    elif direction == "G":
        mqtt_message = "pompaHidup"
        mqtt_topic = "rc/pompa"  # Override topic
    elif direction == "F":
        mqtt_message = "pompaMati"
        mqtt_topic = "rc/pompa"  # Override topic
    elif direction == "4":
        mqtt_message = "kiri"
        mqtt_topic = "rc/pompa"  # Override topic
    elif direction == "5":
        mqtt_message = "tengah"
        mqtt_topic = "rc/pompa"  # Override topic    
    elif direction == "6":
        mqtt_message = "kanan"
        mqtt_topic = "rc/pompa"  # Override topic   
    elif direction == "2":
        mqtt_message = "stop"
        mqtt_topic = "rc/pompa"  # Override topic       
    elif direction == "L":
        mqtt_message = "stroboHidup"
        mqtt_topic = "rc/strobo"  # Override topic
    elif direction == "K":
        mqtt_message = "stroboMati"
        mqtt_topic = "rc/strobo"  # Override topic123

    if mqtt_message:
        # Publish message to MQTT topic
        result = mqtt_client.publish(mqtt_topic, mqtt_message)
        status = result.rc
        if status == 0:
            print(f"Published to {mqtt_topic}: {mqtt_message}")
        else:
            print(f"Failed to send message to {mqtt_topic}")

    return jsonify({"status": "success", "direction": direction, "message": mqtt_message})


# Dummy camera feed route
@app.route('/camera-feed')
def camera_feed():
    # URL dari stream kamera
    # stream_url = "http://192.168.150.16:81/stream"

    # Open the camera stream
    cap = cv2.VideoCapture(stream_url)

    if not cap.isOpened():
        # Stream tidak tersedia
        return "Camera Stream Not Found", 404

    def generate_frame():
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Encode frame ke dalam format JPEG tanpa flip
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                break
            # Convert JPEG ke bytes untuk streaming
            frame_bytes = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    return Response(generate_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == '__main__':
    socketio.run(app, debug=True)
