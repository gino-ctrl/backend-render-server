from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import base64, os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # <-- Questa riga risolve il tuo problema CORS
import base64, os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    image_data = data["image"]
    action = data["action"]

    image_data = image_data.split(",")[1]
    filename = f"{action}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    path = os.path.join(UPLOAD_FOLDER, filename)

    with open(path, "wb") as f:
        f.write(base64.b64decode(image_data))

    return jsonify({"status": "success", "file": filename})

# ROUTE PER VEDERE UNA SINGOLA IMMAGINE
@app.route('/uploads/<filename>')
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ROUTE PER LISTARE TUTTE LE IMMAGINI
@app.route('/list', methods=["GET"])
def list_images():
    files = os.listdir(UPLOAD_FOLDER)
    urls = [f"https://{request.host}/uploads/{f}" for f in files]
    return jsonify(urls)

# HOMEPAGE PER VERIFICA SERVER
@app.route("/")
def home():
    return "<h2>Server attivo. Usa /upload per POST e /list per vedere le immagini.</h2>"

# AVVIO SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
