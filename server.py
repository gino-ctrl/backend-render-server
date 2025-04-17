from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from datetime import datetime
from functools import wraps
import base64, os, pytz

# === CONFIGURAZIONE === #
UPLOAD_FOLDER = "uploads"
LOG_FILE = "accessi.log"
USERNAME = "7482739"
PASSWORD = "JMpspLd8e!!KXRfXst*N"
ORIGIN = "https://gino-ctrl.github.io"  # autorizza solo il tuo dominio

# === SETUP APP === #
app = Flask(__name__)
CORS(app, origins=[ORIGIN])
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
italian_tz = pytz.timezone("Europe/Rome")

# === AUTENTICAZIONE BASE === #
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        "Accesso negato.\n", 401,
        {"WWW-Authenticate": 'Basic realm="Area Protetta"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# === ENDPOINT: /upload === #
@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    image_data = data["image"]
    action = data.get("action", "unknown")
    image_data = image_data.split(",")[1]

    now = datetime.now(italian_tz)
    timestamp_str = now.strftime('%Y%m%d%H%M%S')
    filename = f"{action}_{timestamp_str}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Salva immagine
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(image_data))

    # Salva log
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent", "Sconosciuto")
    log_line = f"[{now.strftime('%d/%m/%Y %H:%M:%S')}] IP: {ip} | User-Agent: {user_agent} | File: {filename}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(log_line)

    return jsonify({"status": "success", "file": filename})

# === ENDPOINT: /logs (protetto) === #
@app.route("/logs")
@requires_auth
def logs():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as log_file:
            lines = log_file.readlines()
    except FileNotFoundError:
        lines = ["Nessun accesso registrato."]

    html_lines = "<br>".join(
        line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for line in lines
    )

    return f"""
    <html>
    <head><title>Log Accessi</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="font-family: monospace; padding: 20px; background: #f0f0f0;">
      <h2>Log Accessi</h2>
      <div style="white-space: pre-wrap; background: #fff; padding: 1em; border-radius: 8px;">
        {html_lines}
      </div>
    </body>
    </html>
    """

# === ENDPOINT: /gallery (protetto) === #
@app.route("/gallery")
@requires_auth
def gallery():
    files = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    images_html = ""

    for filename in files:
        if not filename.endswith(".png"):
            continue
        try:
            timestamp_str = filename.rsplit("_", 1)[1].replace(".png", "")
            timestamp = italian_tz.localize(datetime.strptime(timestamp_str, "%Y%m%d%H%M%S"))
            readable_time = timestamp.strftime("%d/%m/%Y - %H:%M:%S")
        except:
            readable_time = "Data sconosciuta"

        images_html += f"""
        <div style="margin: 15px; text-align: center; max-width: 400px;">
          <img src="/uploads/{filename}" style="max-width: 100%; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.2);"><br>
          <div style="margin-top: 6px; font-size: 14px;">{readable_time}</div>
        </div>
        """

    return f"""
    <html>
    <head><title>Galleria Accessi</title><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="font-family: sans-serif; padding: 20px; background: #fafafa;">
      <h2 style="text-align: center;">Galleria Immagini</h2>
      <div style="display: flex; flex-wrap: wrap; justify-content: center;">
        {images_html}
      </div>
    </body>
    </html>
    """

# === FILE STATICO: /uploads/<filename> === #
@app.route("/uploads/<filename>")
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# === HOME PAGE === #
@app.route("/")
def home():
    return "<h3>Server attivo. Usa /upload per invio, /gallery e /logs con password.</h3>"

# === AVVIO SERVER LOCALE (solo debug) === #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)