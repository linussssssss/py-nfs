# Verwendung: python3 server.py

from flask import Flask, request, jsonify
import os

app = Flask(__name__)
SHARED_FOLDER = "./shared"
os.makedirs(SHARED_FOLDER, exist_ok=True)

EXPORTS_CONFIG = {
    "allowed_clients": ["127.0.0.1"],
    "read_only": False}

def check_access(request):
    client_ip = request.remote_addr
    if client_ip not in EXPORTS_CONFIG["allowed_clients"]:
        return False, f"Zugriff verweigert: {client_ip}"
    return True, None

@app.get("/list")
def list_files():
    allowed, error = check_access(request)
    if not allowed:
        return jsonify({"Fehler: ": error}), 403 
    
    try:
        files = os.listdir(SHARED_FOLDER)
        return jsonify({
            "Dateien: ": files,
            "read-only: ": EXPORTS_CONFIG["read_only"]
        })
    except Exception:
        return jsonify({"Fehler beim Auflisten"}), 500

@app.get("/read")
def read_file():
    allowed, error = check_access(request)
    if not allowed: 
        return jsonify({"Fehler: ": error}), 403
    
    filename = request.args.get("name")
    if not filename:
        return jsonify({"Kein Dateiname angegeben"}), 400
    path = os.path.join(SHARED_FOLDER, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
        
    return "File not found", 404

@app.post("/write")
def write_file():
    allowed, error = check_access(request)
    if not allowed: 
        return jsonify({"Fehler: ": error}), 403
    
    if EXPORTS_CONFIG["read_only"]:
        return jsonify({"Fehler: Dateisystem ist im Read-Only Modus"}), 403
    data = request.json
    filename = data["name"]
    content = data["content"]
    path = os.path.join(SHARED_FOLDER, filename)
    with open(path, "w") as f:
        f.write(content)
    
    return "OK", 200

@app.delete("/delete")
def delete_file():
    allowed, error = check_access(request)
    if not allowed: 
        return jsonify({"Fehler:": error}), 403
    
    if EXPORTS_CONFIG["read_only"]:
        return jsonify({"Fehler": "Dateisystem ist im Read-Only Modus"}), 403
    
    data = request.json
    filename = data.get("name")
    if not filename:
        return jsonify({"Fehler": "Kein Dateiname angegeben"}), 400
    
    path = os.path.join(SHARED_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
        return jsonify({"Erfolg": "Datei wurde geloescht"}), 200
    
    else:
        return jsonify({"Fehler": "Datei nicht gefunden"}), 404

print("Server laeuft auf port 5000")
app.run(port=5000, debug=False)
