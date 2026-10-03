import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

# ---------------- Proxy Settings ----------------
PROXY_USER = "zivhkhbm"
PROXY_PASS = "46c1nmnz4r1o"
PROXY_HOST = "31.59.20.176"
PROXY_PORT = "6754"

# Proxy URL String
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}" if PROXY_HOST else None
# ------------------------------------------------

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Backend is active and running!"})

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"status": "error", "message": "URL is required!"}), 400

    clean_url = video_url.strip()

    # Fast Speed yt-dlp Configuration
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'concurrent_fragment_downloads': 5, # Concurrent chunk downloading for high speed
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    info = None

    # Step 1: Pehle Direct bina proxy ke fast fetch karne ki koshish
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
    except Exception as e:
        print("Direct fetch failed, switching to proxy...", str(e))
        info = None

    # Step 2: Agar bina proxy ke request fail ya block ho, tabhi proxy use karein
    if not info and PROXY_URL:
        try:
            ydl_opts['proxy'] = PROXY_URL
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
        except Exception as e:
            print("Proxy fetch error:", str(e))
            return jsonify({"status": "error", "message": str(e)}), 500

    if not info:
        return jsonify({"status": "error", "message": "Video info extract nahi ho saki"}), 400

    download_url = None
    if 'entries' in info and len(info['entries']) > 0:
        download_url = info['entries'][0].get('url')
    else:
        download_url = info.get('url')

    title = info.get('title', 'Downloaded Video')
    thumbnail = info.get('thumbnail', '')

    if download_url:
        return jsonify({
            "status": "success",
            "title": title,
            "thumbnail": thumbnail,
            "download_url": download_url
        })
    else:
        return jsonify({"status": "error", "message": "Direct download link nahi mila"}), 400

@app.route('/fetch-video', methods=['GET'])
def fetch_video():
    video_url = request.args.get('url')
    if not video_url:
        return "URL required", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # Step 1: Pehle Bina Proxy Ke Fast Direct Stream
        req = requests.get(video_url, headers=headers, stream=True, timeout=10)
    except Exception as e:
        # Step 2: Agar Fail Ho Toh Proxy Se Stream
        if PROXY_URL:
            proxies = {"http": PROXY_URL, "https": PROXY_URL}
            req = requests.get(video_url, headers=headers, stream=True, proxies=proxies, timeout=15)
        else:
            return str(e), 500

    try:
        content_length = req.headers.get('content-length')

        response_headers = {
            'Content-Disposition': 'attachment; filename="video.mp4"',
            'Content-Type': 'video/mp4'
        }

        if content_length:
            response_headers['Content-Length'] = content_length

        return Response(
            req.iter_content(chunk_size=1024*1024),
            headers=response_headers
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
