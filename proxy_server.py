import os
from flask import Flask, Response
import requests

app = Flask(__name__)

TRANS_LINK_URL = "https://gtfs.translink.ca/v2/gtfsrealtime"
API_KEY = "여기에_네_API_KEY"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Vancouver Bus Finder)",
    "Accept": "application/json"
}

@app.route("/")
def home():
    return "Proxy server is running"

@app.route("/gtfs")
def gtfs_proxy():
    try:
        r = requests.get(
            TRANS_LINK_URL,
            params={"apikey": API_KEY},
            headers=HEADERS,
            timeout=20
        )

        return Response(
            r.content,
            status=r.status_code,
            content_type=r.headers.get("Content-Type", "application/octet-stream")
        )

    except Exception as e:
        return Response(f"Proxy error: {e}", status=500)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
