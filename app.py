import os
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)

# सभी Origins से CORS की अनुमति दें ताकि फ्रंटएंड से रिक्वेस्ट आ सके
CORS(app, resources={r"/*": {"origins": "*"}})

# Webshare Rotating Proxy Settings (यदि आवश्यक हो)
PROXY_USER = "zichmhbo-rotate"
PROXY_PASS = "4bc1hns6mrio"
PROXY_HOST = "p.webshare.io"
PROXY_PORT = "80"

PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}/"

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Backend is active and running!'})

@app.route('/download', methods=['GET', 'POST'])
def download():
    # GET query और POST JSON दोनों डेटा को हैंडल करें
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
        'proxy': PROXY_URL, # Webshare Rotating Proxy
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # केवल जानकारी (Metadata/CDN URLs) Extract करें, वीडियो डाउनलोड न करें
            info = ydl.extract_info(clean_url, download=False)

        if not info:
            return jsonify({'status': 'error', 'message': 'Video info fetch failed!'}), 400

        download_url = None
        hd_url = None
        sd_url = None

        # अगर Playlist या मल्टीपल वीडियो का सेट है
        if 'entries' in info and len(info['entries']) > 0:
            first_entry = info['entries'][0]
            download_url = first_entry.get('url')
            title = first_entry.get('title', 'Downloaded_Video')
            thumbnail = first_entry.get('thumbnail', '')
        else:
            download_url = info.get('url')
            title = info.get('title', 'Downloaded_Video')
            thumbnail = info.get('thumbnail', '')

        # अलग-अलग क्वालिटी (SD / HD) चेक करना
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


# ==========================================
# 👇 नया जोड़ा गया रूट (New Download Proxy Route)
# ==========================================
@app.route('/download-video')
def download_video_proxy():
    # फ्रंट-एंड से आने वाले वीडियो यूआरएल को पकड़ना
    video_url = request.args.get('url')
    if not video_url:
        return "URL is missing", 400

    try:
        # बिना सर्वर पर डाउनलोड किए सीधे वीडियो प्रोवाइडर से डेटा स्ट्रीम करना
        req = requests.get(video_url, stream=True, timeout=15)
        
        # क्रोम को डाउनलोड विंडो खोलने के लिए मजबूर करने वाले हेडर्स
        headers = {
            'Content-Disposition': 'attachment; filename="video.mp4"',
            'Content-Type': 'video/mp4'
        }
        
        # रेलवे सर्वर पर फाइल सेव नहीं होगी, डेटा सीधे यूज़र के पास चला जाएगा
        return Response(req.iter_content(chunk_size=1024*1024), headers=headers)
        
    except Exception as e:
        return f"Error downloading video: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
