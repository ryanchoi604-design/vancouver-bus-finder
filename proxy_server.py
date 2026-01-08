from flask import Flask, Response
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("i95CeGKk3M7wzbteE3cl")
GTFS_URL = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"

@app.route("/")
def home():
    return "Proxy server is running"

@app.route("/gtfs")
def gtfs_proxy():
    try:
        r = requests.get(GTFS_URL, timeout=15)
        return Response(
            r.content,
            status=r.status_code,
            content_type="application/octet-stream"
        )
    except Exception as e:
        return Response(str(e), status=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
