# -*- coding: utf-8 -*-
from flask import Flask, render_template
from sense_emu import SenseHat
import sqlite3
import pyrebase
import datetime
import time
import numpy as np
from threading import Thread

# Cấu hình Firebase
config = {
    "apiKey": "AIzaSyCnkskt-9hhF-HPREalfqC74QkqfkLdDzw",
    "authDomain": "dung57kmt.firebaseapp.com",
    "databaseURL": "https://dung57kmt-default-rtdb.firebaseio.com",
    "projectId": "dung57kmt",
    "storageBucket": "dung57kmt.firebasestorage.app",
    "messagingSenderId": "630686372061",
    "appId": "1:630686372061:web:7b84c0916c255b9bea0b34"
}

n = 5  # Kích thước lịch sử mảng
history = [0] * n  # Khởi tạo mảng lịch sử
previous_T = 0  # Giá trị T trước đó
temperature_change_threshold = 1

# Khởi tạo Firebase
firebase = pyrebase.initialize_app(config)
db_rt = firebase.database()  # Sửa lỗi này

sense = SenseHat()

def push_optimized_data():
    global history, previous_T  # Sử dụng biến toàn cục
    try:
        hum = sense.humidity
        temp = sense.temp
        current_temp = temp

        # Tính trung bình của lịch sử
        mean_temp = np.mean(history)

        # Tính T_cập_nhật
        T_cap_nhat = round((current_temp + mean_temp) / 2, 2)

        # So sánh sự thay đổi nhiệt độ với ngưỡng
        if abs(current_temp - previous_T) > temperature_change_threshold:
            # Gửi dữ liệu lên Firebase
            save_firebase(hum, temp)
            save_db(hum, temp)

            previous_T = T_cap_nhat  # Cập nhật T

        # Cập nhật mảng lịch sử
        history.pop(0)  # Xóa phần tử đầu tiên
        history.append(current_temp)  # Thêm giá trị mới vào cuối

        # In mảng lịch sử ra màn hình
        print("Lịch sử nhiệt độ:", history)

        # Tạm dừng 5 giây
        time.sleep(5)

    except Exception as e:
        print("Lỗi xảy ra:", e)

def save_firebase(hum, temp):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")  # Định dạng ngày và giờ

    data = {
        'humidity': hum,
        'temperature': temp,
        'timestamp': timestamp  # Thêm ngày và giờ vào dữ liệu
    }

    # Lưu dữ liệu vào Firebase
    db_rt.child("sense_data").push(data)

def save_db(hum, temp):
    conn = sqlite3.connect('my_db.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sense_data (hum, temp) VALUES (?, ?)
    ''', (hum, temp))
    conn.commit()
    conn.close()

def background_task():
    while True:
        push_optimized_data()

# Tạo ứng dụng Flask
app = Flask(__name__)

@app.route('/')
def index():
    hum = sense.humidity
    temp = sense.temp
    return render_template('index.html', hum=hum, temp=temp)

@app.before_first_request
def start_background_task():
    thread = Thread(target=background_task)
    thread.daemon = True  # Điều này đảm bảo rằng thread sẽ kết thúc khi chương trình chính kết thúc
    thread.start()

# Chạy ứng dụng Flask
if __name__ == '__main__':
    app.run(port=5000, debug=True)