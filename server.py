from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import base64, os

app = Flask(__name__)
CORS(app, origins=["https://gino-ctrl.github.io"])  # Consente solo richieste dal tuo GitHub Pages

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

@app.route("/list", methods=["GET"])
def list_images():
    files = sorted(os.listdir(UPLOAD_FOLDER))
    items = []

    for f in files:
        try:
            parts = f.rsplit("_", 1)[1].replace(".png", "")
            timestamp = datetime.strptime(parts, "%Y%m%d%H%M%S")
            dt = timestamp.strftime("%d/%m/%Y ore %H:%M:%S")
        except:
            dt = "Data sconosciuta"

        url = f"https://{request.host}/uploads/{f}"
        items.append(f"<li><strong>{f}</strong> – {dt} – <a href='{url}' target='_blank'>[Apri immagine]</a></li>")

    html = f"""
    <html>
    <head><title>Elenco immagini</title></head>
    <body style="font-family:Arial">
        <h2>Lista immagini caricate</h2>
        <ul>
            {''.join(items)}
        </ul>
    </body>
    </html>
    """
    return html

@app.route("/gallery")
def gallery():
    files = os.listdir(UPLOAD_FOLDER)
    images = [
        f'<div style="margin:10px"><img src="/uploads/{f}" width="300"><br><small>{f}</small></div>'
        for f in files
    ]
    return f"""
    <html>
      <head><title>Galleria immagini</title></head>
      <body style="font-family:sans-serif">
        <h2>Foto salvate</h2>
        <div style="display:flex; flex-wrap:wrap">{''.join(images)}</div>
      </body>
    </html>
    """

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        return jsonify({"status": "error", "message": "Usa /upload per inviare immagini"}), 405
    return "<h2>Server attivo. Usa /upload per POST, /list per elenco o /gallery per galleria.</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
