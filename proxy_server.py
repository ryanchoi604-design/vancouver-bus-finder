from flask import Flask, Response
import requests

app = Flask(__name__)

TRANS_LINK_URL = "https://gtfs.translink.ca/v2/gtfsrealtime"
API_KEY = "여기에_너_API_KEY_그대로"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Vancouver Bus Finder)",
    "Accept": "application/json"
}

@app.route("/gtfs")
def gtfs_proxy():
    try:
        response = requests.get(
            TRANS_LINK_URL,
            params={"apikey": API_KEY},
            headers=HEADERS,
            timeout=20
        )

        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get("Content-Type", "application/json")
        )

    except Exception as e:
        return Response(
            f"Proxy error: {e}",
            status=500
        )

@app.route("/")
def health_check():
    return "Proxy server is running"
