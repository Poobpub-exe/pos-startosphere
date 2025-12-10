# app.py (Back-end Server Code)

import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

# --- ตั้งค่า Flask ---
app = Flask(__name__)
# เปิดใช้งาน CORS เพื่อให้ Front-end สามารถเรียกใช้ API ได้โดยไม่มีปัญหา
CORS(app) 
# ตั้งชื่อไฟล์ที่ใช้เก็บข้อมูลถาวร
DATA_FILE = 'data.json' 
# กำหนดโฟลเดอร์สำหรับไฟล์ต่างๆ (ที่อยู่เดียวกับ app.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
# เส้นทางเต็มไปยังไฟล์ข้อมูล
FILE_PATH = os.path.join(BASE_DIR, DATA_FILE)

# --- โครงสร้างข้อมูลตั้งต้น ---
# ใช้โครงสร้างนี้ถ้าไฟล์ data.json ยังไม่มีหรือว่างเปล่า
DEFAULT_DATA_STRUCTURE = {
    "products": [],
    "users": [],
    "logs": [],
    "sales": [],
    "members": [],
    "discountCodes": [],
    "qrCodes": [],
    "settings": {}
}

# --- ฟังก์ชันจัดการไฟล์ข้อมูล ---

def load_data():
    """ดึงข้อมูลจาก data.json หากมีและถูกต้อง"""
    if os.path.exists(FILE_PATH) and os.path.getsize(FILE_PATH) > 0:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            try:
                # พยายามโหลดข้อมูล JSON
                return json.load(f)
            except json.JSONDecodeError:
                print("Warning: Data file corrupted or empty, returning default structure.")
    
    # ส่งโครงสร้างข้อมูลตั้งต้นกลับไป
    return DEFAULT_DATA_STRUCTURE

def save_data(data):
    """
    บันทึกข้อมูลลงใน data.json
    *ไฟล์จะถูกสร้างขึ้นหากไม่มีอยู่
    """
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        # บันทึกข้อมูลด้วยการจัดรูปแบบสวยงาม และรองรับภาษาไทย
        json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved successfully to {DATA_FILE}")

# --- Routes (API Endpoints) ---

# 1. Route สำหรับเสิร์ฟไฟล์ index.html (หน้าหลัก)
@app.route('/')
def serve_index():
    """เสิร์ฟไฟล์ index.html จากโฟลเดอร์ปัจจุบัน"""
    return send_from_directory(BASE_DIR, 'index.html')

# 2. Route สำหรับ API (โหลดและบันทึกข้อมูล)
@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        # --- บันทึกข้อมูล (Save) ---
        try:
            data_to_save = request.get_json()
            if data_to_save is None:
                return jsonify({"status": "error", "message": "No JSON data provided"}), 400
            
            # เมื่อมาถึงจุดนี้ เราจะเรียก save_data ซึ่งจะสร้างไฟล์ data.json
            save_data(data_to_save)
            return jsonify({"status": "success", "message": "Data saved successfully."}), 200
        except Exception as e:
             print(f"POST Error: {e}")
             return jsonify({"status": "error", "message": f"Server error during POST: {e}"}), 500

    elif request.method == 'GET':
        # --- ดึงข้อมูล (Load) ---
        try:
            stored_data = load_data()
            return jsonify(stored_data), 200
        except Exception as e:
            print(f"GET Error: {e}")
            return jsonify({"status": "error", "message": f"Server error during GET: {e}"}), 500

# รันเซิร์ฟเวอร์
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)