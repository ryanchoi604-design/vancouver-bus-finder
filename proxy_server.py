# proxy_server.py
from flask import Flask, Response
import requests
import os

app = Flask(__name__)

# 여기에 진짜 라이언의 API 키를 꼭 넣으세요!
API_KEY = "여기에_진짜_API_키_넣으세요" 
GTFS_URL = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"

@app.route("/gtfs")
def gtfs_proxy():
    try:
        r = requests.get(GTFS_URL, timeout=10)
        # 렌더에서 외계어를 쏴주는 부분
        return Response(r.content, status=r.status_code, content_type="application/octet-stream")
    except Exception as e:
        return Response(str(e), status=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
