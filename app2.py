from flask import Flask, render_template, jsonify, request, Response
import random
import cv2  # Import OpenCV
import paho.mqtt.client as mqtt  # Import paho-mqtt

app = Flask(__name__)

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"  # Ganti dengan broker MQTT Anda
MQTT_PORT = 1883
MQTT_TOPIC = "rc/control"

# Create MQTT client
mqtt_client = mqtt.Client()

# Fungsi callback untuk debugging MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect to MQTT Broker, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message published with mid {mid}")

# Set MQTT callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish

# Connect to MQTT broker
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()  # Start MQTT loop

# Dummy sensor data generator
def generate_dummy_data():
    return {
        "total_data": 22,
        "average_temperature": 27.48,
        "average_humidity": 49.22,
        "device_online": 1,  # 1 means online, 0 means offline
        "temperature_data": [
            26.73, 27.94, 28.14, 25.68, 29.23,
            27.51, 28.94, 29.18, 26.81, 27.56
        ],
        "humidity_data": [
            47.83, 51.23, 49.04, 45.57, 50.99,
            48.24, 52.16, 46.41, 48.68, 50.12
        ],
        "battery": 70,  # Battery percentage (from 0 to 100)
        "signal": 52,   # Signal strength (from 0 to 100)
    }

@app.route('/monitoring')
def dashboard():
    return render_template('dashboard.html')

@app.route('/controlling')
def controlling():
    return render_template('controlling.html')

@app.route('/')
def profile():
    people = [

        {'profile_picture': 'path/to/image1.jpg', 'name': 'Muhammad Raya Fathaya', 'NRP': '15-2022-004'},
        {'profile_picture': 'path/to/image1.jpg', 'name': 'Shidiq Nur Hasan', 'NRP': '15-2022-016'},
        {'profile_picture': 'path/to/image1.jpg', 'name': 'Sadira Amalina', 'NRP': '15-2022-018'},
        {'profile_picture': 'path/to/image1.jpg', 'name': 'Fadhil Teguh Amara', 'NRP': '15-2022-020'},
        {'profile_picture': 'path/to/image1.jpg', 'name': 'Jabir Muhammad Nizar', 'NRP': '15-2022-021'},
        {'profile_picture': 'path/to/image1.jpg', 'name': 'Fajar Faturohman', 'NRP': '15-2022-034'},
        {'profile_picture': 'path/to/image1.jpg', 'name': 'Farel Anugrah Al Fauzan', 'NRP': '15-2022-042'},
        {'profile_picture': '/static/images/rivan.jpg', 'name': 'Rivan Dio Perdinan', 'NRP': '15-2022-048'},
        {'profile_picture': 'path/to/image1.jpg', 'name': 'Abhyasa Gunawan Yusuf', 'NRP': '15-2022-087'},
        {'profile_picture': 'path/to/image1.jpg', 'name': 'Muhammad Sakha Sandia', 'NRP': '15-2022-152'},
        {'profile_picture': 'path/to/image1.jpg', 'name': 'Dadan Ramdani', 'NRP': '15-2022-153'},
    ]
    return render_template('profile.html', people=people)

@app.route('/sensor-data')
def sensor_data():
    data = generate_dummy_data()
    return jsonify(data)

@app.route('/control-car', methods=['GET'])
def control_car():
    direction = request.args.get('direction')
    mqtt_message = ""

    # Map direction to MQTT message
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

    if mqtt_message:
        # Publish message to MQTT topic
        result = mqtt_client.publish(MQTT_TOPIC, mqtt_message)
        status = result.rc
        if status == 0:
            print(f"Published to {MQTT_TOPIC}: {mqtt_message}")
        else:
            print(f"Failed to send message to {MQTT_TOPIC}")

    return jsonify({"status": "success", "direction": direction, "message": mqtt_message})

# Dummy camera feed route
@app.route('/camera-feed')
def camera_feed():
    # Open the camera (0 is the default camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        # Camera is not available
        return "Camera Not Found", 404

    def generate_frame():
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Encode the frame as JPEG
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                break
            # Convert the JPEG to bytes and yield it as a stream
            frame_bytes = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

    return Response(generate_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
