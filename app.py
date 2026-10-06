import os
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# सभी डोमेन और रूट से CORS सपोर्ट चालू करने के लिए
CORS(app, resources={r"/*": {"origins": "*"}})

# ----------- Webshare Rotating Proxy Settings -----------
# Webshare Dashboard details
PROXY_USER = "zivhkhbm-rotate"
PROXY_PASS = "46tlmmnzdr1o"
PROXY_HOST = "p.webshare.io"
PROXY_PORT = "80"

# Direct Rotating Proxy String
PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}/"


@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Backend is active and running!"})


@app.route('/download', methods=['GET', 'POST'])
def download():
    # Support both GET query (?url=) and POST JSON body
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        video_url = data.get('url')
    else:
        video_url = request.args.get('url')

    if not video_url:
        return jsonify({"status": "error", "message": "URL is required!"}), 400

    clean_url = video_url.strip()

    # yt_dlp Configuration with Rotating Proxy
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'proxy': PROXY_URL,  # Automatic Rotating Proxy via Webshare
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # download=False में केवल वीडियो का मेटाडेटा निकाला जाता है, वीडियो डाउनलोड नहीं होती
            info = ydl.extract_info(clean_url, download=False)

        if not info:
            return jsonify({"status": "error", "message": "Video info fetch failed"}), 400

        download_url = None

        # Extract direct playable/downloadable CDN link
        if 'entries' in info and len(info['entries']) > 0:
            download_url = info['entries'][0].get('url')
        else:
            download_url = info.get('url')

        title = info.get('title', 'Downloaded_Video')
        thumbnail = info.get('thumbnail', '')

        if download_url:
            return jsonify({
                "status": "success",
                "title": title,
                "thumbnail": thumbnail,
                "download_url": download_url
            })
        else:
            return jsonify({"status": "error", "message": "Direct download link not found!"}), 400

    except Exception as e:
        print(f"yt-dlp error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


# =========================================================
# ZERO BANDWIDTH DIRECT DOWNLOAD ROUTE (CORS & BILL FIX)
# =========================================================
@app.route('/download-direct', methods=['GET'])
def download_direct():
    video_url = request.args.get('url')
    file_name = request.args.get('name', 'video.mp4')

    if not video_url:
        return jsonify({"status": "error", "message": "URL is required"}), 400

    # Attachment हेडर के साथ सीधे वीडियो URL पर रीडायरेक्ट करेगा
    response = redirect(video_url)
    response.headers['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
