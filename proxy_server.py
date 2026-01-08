# proxy_server.py - Public Flask proxy for TransLink GTFS
from flask import Flask, Response
import requests
import os

app = Flask(__name__)

API_KEY = "YOUR_TRANS_LINK_API_KEY"  # 여기에 실제 TransLink API Key 넣기
GTFS_URL = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"

@app.route("/gtfs")
def gtfs_proxy():
    try:
        r = requests.get(GTFS_URL, timeout=10)
        return Response(r.content, status=r.status_code, content_type="application/octet-stream")
    except Exception as e:
        return Response(str(e), status=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render에서 할당하는 포트 사용
    app.run(host="0.0.0.0", port=port)
