from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from datetime import datetime
from functools import wraps
import base64, os, pytz, json

# === CONFIGURAZIONE === #
UPLOAD_FOLDER = "uploads"
LOG_FILE = "accessi.log"
USERNAME = "748239"
PASSWORD = "JMpspLd8e!KXRfXst*N"
ORIGIN = "https://gino-ctrl.github.io"

# === AVVIO APP === #
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

# === UTILITY: Estrai IP reale === #
def estrai_ip():
    ip_raw = request.headers.get("X-Forwarded-For", request.remote_addr)
    ip_list = [ip.strip() for ip in ip_raw.split(",")]
    ip_real = ip_list[0] if ip_list else request.remote_addr
    proxy_info = f" (proxy: {', '.join(ip_list[1:])})" if len(ip_list) > 1 else ""
    return ip_real, proxy_info

# === UTILITY: Traduzioni umane === #
def descrizione_lingua(code):
    lang_map = {
        "it": "Italiano",
        "en": "Inglese",
        "fr": "Francese",
        "de": "Tedesco",
        "es": "Spagnolo",
        "pt": "Portoghese",
        "ru": "Russo",
        "zh": "Cinese",
        "ja": "Giapponese",
        "ar": "Arabo"
    }
    parts = code.split("-")
    lang = lang_map.get(parts[0], parts[0])
    country = parts[1].upper() if len(parts) > 1 else ""
    return f"{lang} ({country})" if country else lang

def descrizione_browser(browser):
    browser_map = {
        "chrome": "Google Chrome",
        "firefox": "Mozilla Firefox",
        "safari": "Apple Safari",
        "edge": "Microsoft Edge",
        "opera": "Opera",
        "android": "Browser Android",
        "ie": "Internet Explorer"
    }
    return browser_map.get(browser.lower(), browser)

def descrizione_piattaforma(platform):
    platform_map = {
        "windows": "Windows",
        "macos": "macOS",
        "linux": "Linux",
        "android": "Android",
        "iphone": "iPhone",
        "ipad": "iPad"
    }
    return platform_map.get(platform.lower(), platform)

# === UTILITY: Altri header informativi === #
def estrai_info(extra=None):
    lang_raw = request.headers.get("Accept-Language", "?").split(',')[0]
    lang_desc = descrizione_lingua(lang_raw)
    referer = request.headers.get("Referer", "nessun referer")
    dnt = request.headers.get("DNT", "Non specificato")
    encoding = request.headers.get("Accept-Encoding", "Non specificato")
    connection = request.headers.get("Connection", "Non specificato")
    ua = request.user_agent
    platform = descrizione_piattaforma(ua.platform or "sconosciuto")
    browser = descrizione_browser(ua.browser or "browser sconosciuto")
    version = ua.version or "?"

    info = f"Sistema operativo: {platform}, Browser: {browser} {version}, Lingua preferita: {lang_desc}, Do Not Track: {dnt}, Tipo connessione: {connection}, Compressione: {encoding}, Pagina di provenienza: {referer}"

    if extra:
        try:
            extra_data = json.loads(extra)
            if isinstance(extra_data, dict):
                for k, v in extra_data.items():
                    k_label = k.replace('_',' ').capitalize()
                    info += f", {k_label}: {v}"
        except:
            info += f" | Extra: {extra}"

    return info

# === ENDPOINT: /track === #
@app.route("/track", methods=["POST"])
def track():
    now = datetime.now(italian_tz)
    ip_real, proxy_info = estrai_ip()
    user_agent = request.headers.get("User-Agent", "Sconosciuto")
    data = request.get_json(silent=True) or {}
    extra = json.dumps(data, ensure_ascii=False)
    info = estrai_info(extra=extra)
    log_line = f"[{now.strftime('%d/%m/%Y %H:%M:%S')}] IP: {ip_real}{proxy_info} | {info} | Evento: visita sito\n"

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(log_line)

    return jsonify({"status": "logged"})
