import os
import requests
from flask import Flask, request, jsonify, Response
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

# पासवर्ड में '#' होने के कारण स्पेशल एन코डिंग
ENCODED_PASS = quote(PROXY_PASS)
PROXY_URL = f"http://{PROXY_USER}:{ENCODED_PASS}@{PROXY_HOST}:{PROXY_PORT}"

# प्रॉक्सी केवल लिंक फेच करने (yt-dlp) के लिए इस्तेमाल होगी
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

    # फेसबुक-इंस्टाग्राम एंटी-ब्लॉक फ़िल्टर (केवल लिंक निकालने के लिए)
    ydl_opts = {
        'format': 'best[vcodec!=none][acodec!=none]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'proxy': PROXY_URL, # प्रॉक्सी यहाँ काम करेगी (खर्च: सिर्फ 2 KB)
        'extractor_args': {
            'instagram': {'check_embed': True},
            'facebook': {'force_dash': False}
        },
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

        if 'entries' in info and len(info['entries']) > 0:
            first_entry = info['entries'][0]
            download_url = first_entry.get('url')
            title = first_entry.get('title', 'Downloaded_Video')
            thumbnail = first_entry.get('thumbnail', '')
        else:
            download_url = info.get('url')
            title = info.get('title', 'Downloaded_Video')
            thumbnail = info.get('thumbnail', '')

        if not download_url:
            formats = info.get('formats', [])
            for fmt in reversed(formats):
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none' and fmt.get('url'):
                    download_url = fmt.get('url')
                    break

        if download_url:
            return jsonify({
                'status': 'success',
                'title': title,
                'thumbnail': thumbnail,
                'download_url': download_url,
                'sd_url': download_url,
                'hd_url': download_url
            })
        else:
            return jsonify({'status': 'error', 'message': 'Direct download link not found!'}), 400

    except Exception as e:
        print(f"yt-dlp error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================
# लीक-प्रूफ़ डाउनलोड रूट (प्रॉक्सी का ₹1 का भी डेटा खर्च नहीं होगा)
# ============================================================
@app.route('/download-video')
def download_video_proxy():
    video_url = request.args.get('url')
    if not video_url:
        return "URL is missing", 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Connection': 'keep-alive'
        }
        
        # 🟢 सुरक्षा कवच: यहाँ से proxies=request_proxies पूरी तरह हटा दिया गया है।
        # यूज़र चाहे 100 बार डाउनलोड शुरू या बंद करे, प्रॉक्सी का डेटा 0 MB खर्च होगा।
        req = requests.get(video_url, stream=True, headers=headers, timeout=60)
        
        if req.status_code != 200:
            return f"Error from source server: {req.status_code}", 400

        total_size = req.headers.get('content-length')

        import time
        unique_id = int(time.time())
        dynamic_filename = f"video_{unique_id}.mp4"

        # बफ़र लीक और क्रोम का 'Download Again' रोकने वाले हेडर्स
        response_headers = {
            'Content-Disposition': f'attachment; filename="{dynamic_filename}"',
            'Content-Type': 'video/mp4',
            'X-Content-Type-Options': 'nosniff',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        
        if total_size:
            response_headers['Content-Length'] = total_size

        return Response(
            # 256KB का चंक साइज़ जो स्लो नेटवर्क (4G) और बड़ी फ़ाइलों (100MB+) दोनों के लिए बेस्ट है
            req.iter_content(chunk_size=256 * 1024), 
            headers=response_headers,
            direct_passthrough=True
        )
        
    except Exception as e:
        return f"Error downloading video: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
