import os
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
from urllib.parse import quote # स्पेशल कैरेक्टर (#) को ठीक करने के लिए

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ==========================================
# Webshare Rotating Proxy Settings
# ==========================================
PROXY_USER = "zivhkhbm-rotate"
PROXY_PASS = "46c1nmnz4r1o"
PROXY_HOST = "p.webshare.io"
PROXY_PORT = "80"

# पासवर्ड में '#' होने के कारण इसे स्पेशल एनकोडिंग (quote) करना ज़रूरी है
ENCODED_PASS = quote(PROXY_PASS)

# यह आपका बिल्कुल सही प्रॉक्सी यूआरएल फॉर्मेट है
PROXY_URL = f"http://{PROXY_USER}:{ENCODED_PASS}@{PROXY_HOST}:{PROXY_PORT}"

# requests लाइब्रेरी के लिए प्रॉक्सी डिक्शनरी
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
              
    # 🟢 इसे अपने app.py में पुराने ydl_opts वाले हिस्से की जगह पेस्ट करें
   
    ydl_opts = {
        # यह फ़ॉर्मेट सख्त नियम लागू करेगा कि वीडियो mp4 हो और उसमें ऑडियो ज़रूर शामिल हो
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
# NEW DOWNLOAD PROXY ROUTE (क्रोम पर वीडियो प्ले होने से रोकने के लिए)
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
        
        # वेबशेयर प्रॉक्सी के साथ सोशल मीडिया से कनेक्ट करना
        req = requests.get(video_url, stream=True, headers=headers, proxies=request_proxies, timeout=60)
        
        if req.status_code != 200:
            return f"Error from source server: {req.status_code}", 400

        # वीडियो का कुल साइज (Length) निकालना
        total_size = req.headers.get('content-length')

        response_headers = {
            'Content-Disposition': 'attachment; filename="video.mp4"',
            'Content-Type': 'video/mp4',
            'X-Content-Type-Options': 'nosniff'
        }
        
        # क्रोम ब्राउज़र को कुल साइज बताना ताकि ऑडियो-वीडियो न अटके और '?' हट जाए
        if total_size:
            response_headers['Content-Length'] = total_size

        return Response(
            req.iter_content(chunk_size=64 * 1024), 
            headers=response_headers,
            direct_passthrough=True
        )
        
    except Exception as e:
        return f"Error downloading video: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
