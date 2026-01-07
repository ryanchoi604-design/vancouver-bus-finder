# proxy_server.py - Public Flask proxy
from flask import Flask, Response
import requests
import os

app = Flask(__name__)

# TransLink API Key (Render Environment Variable로 설정)
API_KEY = os.getenv("TRANS_LINK_API_KEY")
GTFS_URL = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"

@app.route("/gtfs")
def gtfs_proxy():
    try:
        r = requests.get(GTFS_URL, timeout=10)
        return Response(r.content, status=r.status_code, content_type="application/octet-stream")
    except Exception as e:
        return Response(str(e), status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Render에서 공개용