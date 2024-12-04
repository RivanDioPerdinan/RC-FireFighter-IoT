# from flask import Flask, render_template, jsonify, request, Response
# import random
# import cv2  # Import OpenCV

# app = Flask(__name__)

# # Updated dummy sensor data generator with your specific data
# def generate_dummy_data():
#     return {
#         "total_data": 22,
#         "average_temperature": 27.48,
#         "average_humidity": 49.22,
#         "device_online": 1,  # 1 means online, 0 means offline
#         "temperature_data": [
#             26.73, 27.94, 28.14, 25.68, 29.23,
#             27.51, 28.94, 29.18, 26.81, 27.56
#         ],
#         "humidity_data": [
#             47.83, 51.23, 49.04, 45.57, 50.99,
#             48.24, 52.16, 46.41, 48.68, 50.12
#         ],
#         "battery": 10,  # Battery percentage (from 0 to 100)
#         "signal": 52,   # Signal strength (from 0 to 100)
#     }

# @app.route('/')
# def dashboard():
#     return render_template('dashboard.html')

# @app.route('/controlling')
# def controlling():
#     return render_template('controlling.html')

# @app.route('/sensor-data')
# def sensor_data():
#     data = generate_dummy_data()
#     return jsonify(data)

# @app.route('/control-car', methods=['GET'])
# def control_car():
#     direction = request.args.get('direction')
#     # Process the direction command here (for example, send command to RC car)
#     print(f"Received control command: {direction}")
#     return jsonify({"status": "success", "direction": direction})

# # Dummy camera feed route
# @app.route('/camera-feed')
# def camera_feed():
#     # Open the camera (0 is the default camera)
#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         # Camera is not available
#         return "Camera Not Found", 404

#     def generate_frame():
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break
#             # Encode the frame as JPEG
#             ret, jpeg = cv2.imencode('.jpg', frame)
#             if not ret:
#                 break
#             # Convert the JPEG to bytes and yield it as a stream
#             frame_bytes = jpeg.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

#     return Response(generate_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == '__main__':
#     app.run(debug=True)
