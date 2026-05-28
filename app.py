"""
Instagram Reel Analytics Dashboard - Production Backend
Serves static frontend + proxies all Apify API calls (no CORS issues)
Deploy to Render.com, Railway, or Heroku for free
"""

import json
import os
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration - APIFY_TOKEN must be set via environment variable
APIFY_TOKEN = os.environ.get("APIFY_TOKEN")
if not APIFY_TOKEN:
    raise RuntimeError("APIFY_TOKEN environment variable is required")
APIFY_BASE = "https://api.apify.com/v2"
REEL_SCRAPER = "apify~instagram-reel-scraper"


def _apify_request(method, path, body=None):
    """Make request to Apify API"""
    url = f"{APIFY_BASE}{path}"
    headers = {"Authorization": f"Bearer {APIFY_TOKEN}"}
    if body:
        headers["Content-Type"] = "application/json"
    
    if method == "GET":
        r = requests.get(url, headers=headers, timeout=30)
    elif method == "POST":
        r = requests.post(url, headers=headers, json=body, timeout=30)
    else:
        r = requests.request(method, url, headers=headers, json=body, timeout=30)
    
    r.raise_for_status()
    return r.status_code, r.json()


@app.route("/")
def index():
    """Serve the main dashboard"""
    return send_from_directory("static", "index.html")


@app.route("/pricing")
def pricing():
    """Serve pricing page"""
    try:
        with open("static/pricing.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Pricing page not found</h1>", 404


@app.route("/api/health")
def health():
    try:
        status, data = _apify_request("GET", "/users/me")
        return jsonify({
            "status": "ok",
            "apify_connected": status == 200,
            "user": data.get("data", {}).get("username", "unknown"),
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/scrape", methods=["POST"])
def start_scrape():
    try:
        payload = request.get_json() or {}
        username = payload.get("username", "")
        max_reels = min(int(payload.get("maxReels", 27)), 200)
        
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        status, data = _apify_request("POST", f"/acts/{REEL_SCRAPER}/runs", {
            "username": [username],
            "resultsLimit": max_reels,
            "includeCaption": True,
            "includeTranscript": True,
            "includeVideoUrl": False,
            "includeSharesCount": False,
        })
        
        return jsonify({
            "runId": data["data"]["id"],
            "datasetId": data["data"]["defaultDatasetId"],
            "status": data["data"]["status"],
        }), status
    except requests.exceptions.HTTPError as e:
        try:
            msg = e.response.json().get("error", {}).get("message", str(e))
        except:
            msg = str(e)
        return jsonify({"error": msg}), e.response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/status/<run_id>")
def check_status(run_id):
    try:
        status, data = _apify_request("GET", f"/actor-runs/{run_id}")
        return jsonify({
            "status": data["data"]["status"],
            "statusMessage": data["data"].get("statusMessage", ""),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/results/<dataset_id>")
def get_results(dataset_id):
    try:
        limit = request.args.get("limit", "1000")
        status, data = _apify_request("GET", f"/datasets/{dataset_id}/items?clean=true&limit={limit}")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
