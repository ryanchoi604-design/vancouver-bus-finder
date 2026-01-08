from flask import Flask, Response
import requests
import os

app = Flask(__name__)

# 🔹 여기에 라이언님 TransLink API 키 넣기
API_KEY = "i95CeGKk3M7wzbteE3cl"
GTFS_URL = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"

@app.route("/gtfs")
def gtfs_proxy():
    try:
        r = requests.get(GTFS_URL, timeout=10)
        # 상태코드 확인
        if r.status_code != 200:
            return Response(
                f"TransLink API 요청 실패! 상태코드: {r.status_code}\n내용: {r.text[:500]}",
                status=500,
                content_type="text/plain"
            )
        # HTML로 오면 오류 표시
        if "html" in r.headers.get("Content-Type", "").lower():
            return Response(
                f"TransLink API가 HTML 응답을 반환했습니다!\n상태코드: {r.status_code}\n내용: {r.text[:500]}",
                status=500,
                content_type="text/plain"
            )

        # 정상 바이너리면 그대로 내려주기
        return Response(
            r.content,
            status=200,
            content_type="application/octet-stream"
        )
    except Exception as e:
        return Response(f"프록시 서버 에러: {e}", status=500, content_type="text/plain")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Proxy server running on port {port}")
    app.run(host="0.0.0.0", port=port)
