# ==========================================================
# app.py - Production-Ready Flask API for POS System
# ==========================================================
import json
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS # ใช้สำหรับ Production Environment

# --- 1. การตั้งค่าเริ่มต้น ---
app = Flask(__name__)
# อนุญาต CORS สำหรับทุก Origin (จำเป็นเมื่อใช้ API Service)
CORS(app) 

DATA_FILE = 'data.json'
# กำหนด path ที่แน่นอนเพื่อหลีกเลี่ยงปัญหาบน Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, DATA_FILE)

# --- 2. โครงสร้างข้อมูลตั้งต้น (DEFAULT DATA) ---
# ใช้ในกรณีที่ data.json ยังไม่มีอยู่ หรือไฟล์เสียหาย
DEFAULT_DATA_STRUCTURE = {
    "products": [],
    "users": [],
    "logs": [],
    "sales": [],
    "members": [],
    "discountCodes": [],
    "qrCodes": [],
    "settings": {
        "appName": "POS Startosphere",
        "currency": "THB",
        "taxRate": 7.0
    }
}

# --- 3. ฟังก์ชันจัดการไฟล์ข้อมูล (LOAD) ---

def load_data():
    """
    ดึงข้อมูลจาก data.json. หากไฟล์ไม่มีอยู่, ว่างเปล่า, หรือเสียหาย 
    จะส่งคืนโครงสร้างข้อมูลตั้งต้น (DEFAULT_DATA_STRUCTURE)
    """
    if os.path.exists(FILE_PATH) and os.path.getsize(FILE_PATH) > 0:
        try:
            with open(FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # ตรวจสอบความสมบูรณ์ขั้นพื้นฐาน
                if isinstance(data, dict) and 'products' in data:
                    return data
                else:
                    print("Warning: Data structure corrupted. Returning default structure.")
        except json.JSONDecodeError:
            print("Warning: Data file corrupted (JSON Decode Error). Returning default structure.")
        except Exception as e:
            print(f"Error reading file: {e}. Returning default structure.")
    
    print(f"Initializing with default data structure (file not found or empty: {DATA_FILE}).")
    return DEFAULT_DATA_STRUCTURE

# --- 4. ฟังก์ชันจัดการไฟล์ข้อมูล (SAVE) ---

def save_data(data):
    """
    บันทึกข้อมูลลงใน data.json โดยตรวจสอบความสมบูรณ์ของข้อมูลก่อน
    *สำคัญ: ไฟล์จะถูกสร้างขึ้นหากไม่มีอยู่
    """
    if not isinstance(data, dict):
        print("Error: Data to save is not a dictionary. Aborting save.")
        return False
        
    try:
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            # ใช้ ensure_ascii=False เพื่อรองรับภาษาไทย
            json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Data saved successfully to {DATA_FILE}")
            return True
    except Exception as e:
        print(f"Error writing to file: {e}")
        return False

# --- 5. Route หลัก: เสิร์ฟ index.html ---

@app.route('/')
def serve_index():
    # ส่งไฟล์ index.html ให้เบราว์เซอร์
    return send_from_directory(BASE_DIR, 'index.html')

# --- 6. API Route: จัดการข้อมูล (Load/Save) ---

@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        # --- บันทึกข้อมูล (Save) ---
        try:
            # พยายามดึง JSON จาก Request
            data_to_save = request.get_json()
            
            if data_to_save is None:
                # 400 Bad Request: หาก Front-end ไม่ได้ส่ง JSON มา
                return jsonify({"status": "error", "message": "No JSON data provided or invalid JSON format."}), 400
            
            # เรียกใช้ save_data() 
            if save_data(data_to_save):
                return jsonify({"status": "success", "message": "Data saved successfully."}), 200
            else:
                # 500 Internal Server Error: หาก save_data ล้มเหลวในการเขียนไฟล์
                return jsonify({"status": "error", "message": "Server failed to write data to file."}), 500
                
        except Exception as e:
             # ดักจับ Error ที่ไม่คาดคิด
             print(f"POST Error (Unhandled): {e}")
             return jsonify({"status": "error", "message": f"Server error during POST: {e}"}), 500

    elif request.method == 'GET':
        # --- ดึงข้อมูล (Load) ---
        try:
            stored_data = load_data()
            return jsonify(stored_data), 200
        except Exception as e:
            print(f"GET Error (Unhandled): {e}")
            return jsonify({"status": "error", "message": f"Server error during GET: {e}"}), 500

# --- 7. รันเซิร์ฟเวอร์ (สำหรับ Local Testing) ---
if __name__ == '__main__':
    # ห้ามใช้ debug=True เมื่อ Deploy จริงบน Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=False)