from flask import Flask, request, jsonify
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
