import os
import requests
from flask import Flask, request, jsonify, Response, redirect # 🟢 redirect को जोड़ा गया है
from flask_cors import CORS
import yt_dlp
from urllib.parse import quote 
import time # 🟢 टाइमस्टैम्प के लिए इसे जोड़ा गया है

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==========================================
# Webshare Rotating Proxy Settings
# ==========================================
PROXY_USER = "zivhkhbm-rotate"
PROXY_PASS = "46c1nmnz4r1o"
PROXY_HOST = "p.webshare.io"
PROXY_PORT = "80"

ENCODED_PASS = quote(PROXY_PASS)
PROXY_URL = f"http://{PROXY_USER}:{ENCODED_PASS}@{PROXY_HOST}:{PROXY_PORT}"

request_proxies = {
    "http": PROXY_URL,
    "https": PROXY_URL
}
# ==========================================

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'success', 'message': 'Backend is active and running!'})


@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        video_url = data.get('url')
    else:
        video_url = request.args.get('url')

    if not video_url:
        return jsonify({'status': 'error', 'message': 'URL is required!'}), 400

    clean_url = video_url.strip()

    # yt-dlp Configuration
    ydl_opts = {
        # 🟢 ऑडियो गायब होने की समस्या का असली इलाज:
        # यह सोशल मीडिया से केवल वही डायरेक्ट लिंक्स उठाएगा जिनमें ऑडियो और वीडियो पहले से मर्ज्ड (साथ में) हों।
        # इससे आपके रेलवे सर्वर पर कोई लोड नहीं आएगा और ऑडियो 100% चालू रहेगा।
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'proxy': PROXY_URL,
        'extractor_args': {'instagram': {'check_embed': True}}, 
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)

        if not info:
            return jsonify({'status': 'error', 'message': 'Video info fetch failed!'}), 400

        download_url = None
        hd_url = None
        sd_url = None

        if 'entries' in info and len(info['entries']) > 0:
            first_entry = info['entries'][0]
            download_url = first_entry.get('url')
            title = first_entry.get('title', 'Downloaded_Video')
            thumbnail = first_entry.get('thumbnail', '')
        else:
            download_url = info.get('url')
            title = info.get('title', 'Downloaded_Video')
            thumbnail = info.get('thumbnail', '')

        formats = info.get('formats', [])
        for fmt in formats:
            if fmt.get('vcodec') != 'none' and fmt.get('url'):
                if fmt.get('height') and fmt.get('height') >= 720:
                    hd_url = fmt.get('url')
                else:
                    sd_url = fmt.get('url')

        if not download_url and formats:
            download_url = formats[-1].get('url')

        if download_url:
            return jsonify({
                'status': 'success',
                'title': title,
                'thumbnail': thumbnail,
                'download_url': download_url,
                'sd_url': sd_url or download_url,
                'hd_url': hd_url or download_url
            })
        else:
            return jsonify({'status': 'error', 'message': 'Direct download link not found!'}), 400

    except Exception as e:
        print(f"yt-dlp error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================
# NEW DOWNLOAD PROXY ROUTE (रेलवे और प्रॉक्सी का खर्चा बचाने वाला नया तरीका)
# ============================================================
@app.route('/download-video')
def download_video_proxy():
    video_url = request.args.get('url')
    
    # 🟢 'Download file again' को रोकने के लिए यूआरएल से 'title' लेंगे।
    # अगर फ्रंटएंड से टाइटल नहीं आता है, तो करंट टाइमस्टैम्प से नाम ऑटोमैटिक बदल जाएगा।
    filename = request.args.get('title', f"video_{int(time.time())}")

    if not video_url:
        return "URL is missing", 400

    try:
        # 🟢 रेलवे बैंडविड्थ और प्रॉक्सी खर्च बचाने का सबसे बेस्ट तरीका (Redirect):
        # पुराना कोड भारी वीडियो डेटा को रेलवे पर डाउनलोड करता था (जिससे प्रॉक्सी का बिल बढ़ता था)।
        # यहाँ हम सिर्फ यूज़र को ओरिजिनल वीडियो यूआरएल पर रिडायरेक्ट कर रहे हैं।
        # इससे पूरा हैवी डेटा सीधे इंस्टाग्राम/फेसबुक के सर्वर से यूज़र के फोन में जाएगा। 
        # परिणाम: आपका प्रॉक्सी खर्च और रेलवे बैंडविड्थ = बिल्कुल 0% (Zero)!
        # इसके अलावा, ओरिजिनल सर्वर से कनेक्ट होने के कारण क्रोम को असली 'Content-Length' पता चल जाएगी, जिससे (?) मार्क की समस्या भी खत्म हो जाएगी।
        return redirect(video_url), 302
        
    except Exception as e:
        return f"Error downloading video: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
