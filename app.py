import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

# --- USER-AGENT ROTATION SETUP (नया कोड) ---
from fake_useragent import UserAgent
ua = UserAgent()
# --------------------------------------------

app = Flask(__name__)
CORS(app)

# ----------------- Proxy Settings -----------------
PROXY_USER = "zivhkhbm-rotate"
PROXY_PASS = "46c1nmnz4r10"
PROXY_HOST = "p.webshare.io"
PROXY_PORT = "80"

# Proxy URL String
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}" if PROXY_HOST else None
# --------------------------------------------------

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Backend is active and running!"})

@app.route('/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url')

    if not video_url:
        return jsonify({"status": "error", "message": "URL is required"}), 400

    clean_url = video_url.strip()
    info = None
    
    # Proxy ke saath automatic 3 baar retry karega
    max_retries = 3

    for attempt in range(max_retries):
        try:
            random_ua = ua.random
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'concurrent_fragment_downloads': 5,
                'proxy': PROXY_URL,  # Direct Webshare Proxy use hogi
                'http_headers': {
                    'User-Agent': random_ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                if info:
                    print(f"Success on attempt {attempt + 1}")
                    break  # Success hone par loop khatam
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {str(e)}")

    if not info:
        return jsonify({"status": "error", "message": "Video info extract nahi ho saki"}), 500

    # Video Download Link Extract karna
    download_url = None
    if 'url' in info and info['url']:
        download_url = info['url']
    elif 'entries' in info and len(info['entries']) > 0:
        download_url = info['entries'][0].get('url')

    title = info.get('title', 'Downloaded Video')
    thumbnail = info.get('thumbnail', '')

    if download_url:
        return jsonify({
            "status": "success",
            "title": title,
            "thumbnail": thumbnail,
            "download_url": download_url
        })

    return jsonify({"status": "error", "message": "Direct download link nahi mila"}), 500
