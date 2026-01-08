# proxy_server.py
from flask import Flask, Response
import requests
import os

app = Flask(__name__)

# 🔹 라이언님의 API 키가 적용되었습니다.
API_KEY = "i95CeGKk3M7wzbteE3cl"
GTFS_URL = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"

@app.route("/gtfs")
def gtfs_proxy():
    try:
        # TransLink 서버에서 데이터를 가져옵니다.
        r = requests.get(GTFS_URL, timeout=10)
        
        # 받은 데이터(Binary)를 그대로 전달합니다.
        return Response(
            r.content, 
            status=r.status_code, 
            content_type="application/octet-stream"
        )
    except Exception as e:
        return Response(str(e), status=500)

if __name__ == "__main__":
    # Render에서 할당하는 포트번호를 자동으로 사용합니다.
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
