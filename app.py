import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

# ---------------- Proxy Settings ----------------
PROXY_USER = "aapka_proxy_username"
PROXY_PASS = "aapka_proxy_password"
PROXY_HOST = "aapka_proxy_host"  # e.g., p.webshare.io
PROXY_PORT = "aapka_proxy_port"  # e.g., 8080

# Proxy URL String (Agar proxy hai toh ye active ho jayega)
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

    # yt-dlp Configuration with Proxy & Browser Headers
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    # Proxy add karna agar details bhari gayi hain
    if PROXY_URL and "aapka_proxy_host" not in PROXY_URL:
        ydl_opts['proxy'] = PROXY_URL

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)

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

    except Exception as e:
        print("yt-dlp error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/fetch-video', methods=['GET'])
def fetch_video():
    video_url = request.args.get('url')
    if not video_url:
        return "URL required", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # Proxy stream ke liye (agar proxy use kar rahe ho)
        proxies = {"http": PROXY_URL, "https": PROXY_URL} if (PROXY_URL and "aapka_proxy_host" not in PROXY_URL) else None

        req = requests.get(video_url, headers=headers, stream=True, proxies=proxies, timeout=15)
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
