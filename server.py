from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import base64, os

app = Flask(__name__)
CORS(app, origins=["https://gino-ctrl.github.io"])

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

@app.route("/uploads/<filename>")
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/gallery")
def gallery():
    files = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    images = []

    for f in files:
        try:
            timestamp_str = f.rsplit("_", 1)[1].replace(".png", "")
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
            ora = timestamp.strftime("%d/%m/%Y - %H:%M:%S")
        except:
            ora = "Data sconosciuta"

        images.append(f"""
            <div style="margin:15px; max-width: 400px;">
                <img src="/uploads/{f}" style="max-width: 100%; height: auto; border:1px solid #ccc; border-radius:6px;"><br>
                <small>{f} – <strong>{ora}</strong></small>
            </div>
        """)

    html = f"""
    <html>
    <head><title>Galleria immagini</title></head>
    <body style="font-family:sans-serif; padding:20px;">
      <h2>Galleria Immagini</h2>
      <div style="display: flex; flex-wrap: wrap; justify-content: center;">
        {''.join(images)}
      </div>
    </body>
    </html>
    """
    return html

@app.route("/", methods=["GET", "POST"])
def home():
    return "<h2>Server attivo. Usa /upload per POST, /gallery per galleria.</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
