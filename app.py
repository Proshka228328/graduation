from flask import *
from flask_socketio import *
from flask_sqlalchemy import *
import json
import cv2
import base64
from io import BytesIO
from PIL import Image
import mysql.connector  # Добавлен импорт модуля для работы с MySQL
import os
import socket
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Horsegay328'

class Instruments:
    @staticmethod
    def config():
        with open('config.json') as config_file:
            config_data = json.load(config_file)
        db_config = config_data['db']
        db_name = db_config['name']
        db_login = db_config['login']
        db_password = db_config['password']
        db_host = db_config['host']
        return config_data, db_config, db_password, db_login, db_name, db_host
    
    @staticmethod
    def connectdb():
        config_data, db_config, db_password, db_login, db_name, db_host = Instruments.config()

        connection = mysql.connector.connect(
            user=db_login,
            password=db_password,
            host=db_host,
            database=db_name
        )
        cursor = connection.cursor()
        return cursor, connection  # Исправлено возвращаемое значение
    @staticmethod
    def clear():
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

class VideoCamera:
    def __init__(self):
    
        self.video = cv2.VideoCapture('rtsp://Horse:s10102008s@192.168.1.100:554/your_video_stream')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        if success:
            _, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()
        else:
            return b''



video_stream = VideoCamera()

@app.route('/video_feed')
def video_feed():
    try:
        return Response(gen(video_stream),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in /video_feed: {str(e)}")
        return Response(b'', status=500)


@app.route('/video')
def video():
    return render_template('video_feed.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/camera/<int:id>')
def camera(id):
    cursor, connection = Instruments.connectdb()
    query = f"SELECT * FROM webcam WHERE id = {id}"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        id, ip, password, login = result
        print(f"ID: {id}")
        print(f"ip: {ip}")
        print(f"password: {password}")
        print(f"login: {login}")

        # Отправка запроса ping
        ping_result = subprocess.run(["ping", "-n", "4", ip], capture_output=True)
        if "Заданный узел недоступен" in ping_result.stderr.decode():
            print(f"Ping неудачен для IP-адреса {ip}")
        else:
            print(f"Ping успешен для IP-адреса {ip}")

    else:
        print(f"Запись с ID {id} не найдена в таблице webcam")

    cursor.close()
    connection.close()

    return render_template('camera.html', id=id, ip=ip, password=password, login=login)


@app.route('/camera/<int:id>/ping')
def check_camera_ping(id):
    cursor, connection = Instruments.connectdb()
    query = f"SELECT ip FROM webcam WHERE id = {id}"
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        ip_address = result[0]

        try:
            subprocess.run(["ping", "-n", "4", ip_address], check=True, capture_output=True, text=True)
            status = "online"
        except subprocess.CalledProcessError:
            status = "offline"
    else:
        status = "offline"

    print(f"Статус {id} - {status}")
    cursor.close()
    connection.close()

    return jsonify({"success": status == "online"})



if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=5000)

