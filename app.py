import os
import requests
from flask import Flask, request, jsonify, Response, redirect # 🟢 redirect यहाँ इम्पोर्ट किया है
from flask_cors import CORS
import yt_dlp
from urllib.parse import quote 

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
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'proxy': PROXY_URL, # 🟢 सिर्फ वीडियो इन्फो निकालने के लिए प्रॉक्सी का उपयोग (नाममात्र का खर्च)
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
            title = first_entry.get('title', 'MT_Video')
            thumbnail = first_entry.get('thumbnail', '')
        else:
            download_url = info.get('url')
            title = info.get('title', 'MT_Video')
            thumbnail = info.get('thumbnail', '')

        # 🟢 वीडियो टाइटल से स्पेस और स्पेशल कैरेक्टर हटाना ताकि फाइल नेम एकदम सही बने
        clean_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        clean_title = clean_title.replace(" ", "_")[:50] 

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
                'clean_title': clean_title, # 🟢 फ्रंटएंड में रैंडम नाम बनाने के लिए भेजा
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
# 🟢 सुपर-इकोनॉमी डाउनलोड रूट (प्रॉक्सी और रेलवे डेटा खर्च = 0)
# ============================================================
@app.route('/download-video')
def download_video_proxy():
    video_url = request.args.get('url')
    filename = request.args.get('title', 'MT_Video') # 🟢 फ्रंटएंड से डायनामिक नाम आ रहा है

    if not video_url:
        return "URL is missing", 400

    try:
        # 🟢 चालाकी भरा तरीका: वीडियो को रेलवे सर्वर पर डाउनलोड करने के बजाय
        # हम सिर्फ रिडायरेक्ट (302) कर रहे हैं। इससे वीडियो का पूरा हैवी डेटा सीधे 
        # इंस्टाग्राम/फेसबुक के सर्वर से यूज़र के फोन में जाएगा। 
        # आपका रेलवे बैंडविड्थ और प्रॉक्सी खर्च बिल्कुल ₹0 (जीरो) हो जाएगा!
        return redirect(video_url), 302
        
    except Exception as e:
        return f"Error redirection: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
