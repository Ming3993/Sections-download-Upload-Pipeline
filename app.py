import os
import threading
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from downloader import pipeline
from queue import Queue
from datetime import datetime
import time
from get_token import get_access_token
from get_pathId import get_item_id
from dotenv import load_dotenv
import json

# Setting variables
with open('settings.json', 'r', encoding='utf-8') as f:
    settings = json.load(f)
ONEDRIVE_PATH = settings.get("onedrive_path")
INPUT_STORAGE = settings.get("input_storage")

# Your own onedrive information
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")

# Initial for later fetching
ACCESS_TOKEN = ""
ITEM_ID = ""

os.makedirs(INPUT_STORAGE, exist_ok=True)

app = Flask(__name__, static_folder="static")
app.config["INPUT_STORAGE"] = INPUT_STORAGE

task_queue = Queue()
current_processing = None
last_access_time = 0
queue_list = []

def log_message(client_ip, msg=""):
    with open("access_log.txt", "a") as f:
        f.write(f"{client_ip} - {time.strftime('%Y-%m-%d %H:%M:%S')}{msg}\n")

def worker():
    global current_processing, ACCESS_TOKEN, ITEM_ID
    while True:
        fpath = task_queue.get()
        if fpath is None:
            break
        try:
            current_processing = os.path.basename(fpath)
            print("Processing:", fpath)
            pipeline(fpath,ACCESS_TOKEN,ITEM_ID)
            os.remove(fpath)
        except Exception as e:
            print("Error processing:", e)
        finally:
            current_processing = None
            queue_list.remove(os.path.basename(fpath))
            task_queue.task_done()

threading.Thread(target=worker, daemon=True).start()

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    global last_access_time, ACCESS_TOKEN, ITEM_ID, ONEDRIVE_PATH, CLIENT_ID, TENANT_ID
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    current_time = time.time()  # epoch second of current time
    client_ip = request.remote_addr
    
    if current_time - last_access_time >= 3600:  # get new token every hour
        last_access_time = current_time
        ACCESS_TOKEN = get_access_token(CLIENT_ID, TENANT_ID)
        ITEM_ID = get_item_id(ONEDRIVE_PATH, ACCESS_TOKEN)
        log_message(client_ip, " - reset")
    else:
        log_message(client_ip)
        
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename = f"{timestamp}{ext}"

    file_path = os.path.join(app.config["INPUT_STORAGE"], filename)
    file.save(file_path)

    queue_list.append(filename)
    task_queue.put(file_path)

    return jsonify({"message": "File added to queue", "filename": filename})

@app.route("/status")
def status():
    return jsonify({
        "processing": current_processing,
        "pending": [f for f in queue_list if f != current_processing]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)