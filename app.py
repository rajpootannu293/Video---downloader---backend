import os
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)

# à¤¸à¤­à¥€ Origins à¤¸à¥‡ CORS à¤•à¥€ à¤…à¤¨à¥à¤®à¤¤à¤¿ à¤¦à¥‡à¤‚ à¤¤à¤¾à¤•à¤¿ à¤«à¥à¤°à¤‚à¤Ÿà¤à¤‚à¤¡ à¤¸à¥‡ à¤°à¤¿à¤•à¥à¤µà¥‡à¤¸à¥à¤Ÿ à¤† à¤¸à¤•à¥‡
CORS(app, resources={r"/*": {"origins": "*"}})

# Webshare Rotating Proxy Settings (à¤¯à¤¦à¤¿ à¤†à¤µà¤¶à¥à¤¯à¤• à¤¹à¥‹)
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
    # GET query à¤”à¤° POST JSON à¤¦à¥‹à¤¨à¥‹à¤‚ à¤¡à¥‡à¤Ÿà¤¾ à¤•à¥‹ à¤¹à¥ˆà¤‚à¤¡à¤² à¤•à¤°à¥‡à¤‚
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
            # à¤•à¥‡à¤µà¤² à¤œà¤¾à¤¨à¤•à¤¾à¤°à¥€ (Metadata/CDN URLs) Extract à¤•à¤°à¥‡à¤‚, à¤µà¥€à¤¡à¤¿à¤¯à¥‹ à¤¡à¤¾à¤‰à¤¨à¤²à¥‹à¤¡ à¤¨ à¤•à¤°à¥‡à¤‚
            info = ydl.extract_info(clean_url, download=False)

        if not info:
            return jsonify({'status': 'error', 'message': 'Video info fetch failed!'}), 400

        download_url = None
        hd_url = None
        sd_url = None

        # à¤…à¤—à¤° Playlist à¤¯à¤¾ à¤®à¤²à¥à¤Ÿà¥€à¤ªà¤² à¤µà¥€à¤¡à¤¿à¤¯à¥‹ à¤•à¤¾ à¤¸à¥‡à¤Ÿ à¤¹à¥ˆ
        if 'entries' in info and len(info['entries']) > 0:
            first_entry = info['entries'][0]
            download_url = first_entry.get('url')
            title = first_entry.get('title', 'Downloaded_Video')
            thumbnail = first_entry.get('thumbnail', '')
        else:
            download_url = info.get('url')
            title = info.get('title', 'Downloaded_Video')
            thumbnail = info.get('thumbnail', '')

        # à¤…à¤²à¤—-à¤…à¤²à¤— à¤•à¥à¤µà¤¾à¤²à¤¿à¤Ÿà¥€ (SD / HD) à¤šà¥‡à¤• à¤•à¤°à¤¨à¤¾
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
# ðŸ‘‡ à¤¨à¤¯à¤¾ à¤œà¥‹à¥œà¤¾ à¤—à¤¯à¤¾ à¤°à¥‚à¤Ÿ (New Download Proxy Route)
# ==========================================
@app.route('/download-video')
def download_video_proxy():
    # à¤«à¥à¤°à¤‚à¤Ÿ-à¤à¤‚à¤¡ à¤¸à¥‡ à¤†à¤¨à¥‡ à¤µà¤¾à¤²à¥‡ à¤µà¥€à¤¡à¤¿à¤¯à¥‹ à¤¯à¥‚à¤†à¤°à¤à¤² à¤•à¥‹ à¤ªà¤•à¥œà¤¨à¤¾
    video_url = request.args.get('url')
    if not video_url:
        return "URL is missing", 400

    try:
        # à¤¬à¤¿à¤¨à¤¾ à¤¸à¤°à¥à¤µà¤° à¤ªà¤° à¤¡à¤¾à¤‰à¤¨à¤²à¥‹à¤¡ à¤•à¤¿à¤ à¤¸à¥€à¤§à¥‡ à¤µà¥€à¤¡à¤¿à¤¯à¥‹ à¤ªà¥à¤°à¥‹à¤µà¤¾à¤‡à¤¡à¤° à¤¸à¥‡ à¤¡à¥‡à¤Ÿà¤¾ à¤¸à¥à¤Ÿà¥à¤°à¥€à¤® à¤•à¤°à¤¨à¤¾
        req = requests.get(video_url, stream=True, timeout=15)
        
        # à¤•à¥à¤°à¥‹à¤® à¤•à¥‹ à¤¡à¤¾à¤‰à¤¨à¤²à¥‹à¤¡ à¤µà¤¿à¤‚à¤¡à¥‹ à¤–à¥‹à¤²à¤¨à¥‡ à¤•à¥‡ à¤²à¤¿à¤ à¤®à¤œà¤¬à¥‚à¤° à¤•à¤°à¤¨à¥‡ à¤µà¤¾à¤²à¥‡ à¤¹à¥‡à¤¡à¤°à¥à¤¸
        headers = {
            'Content-Disposition': 'attachment; filename="video.mp4"',
            'Content-Type': 'video/mp4'
        }
        
        # à¤°à¥‡à¤²à¤µà¥‡ à¤¸à¤°à¥à¤µà¤° à¤ªà¤° à¤«à¤¾à¤‡à¤² à¤¸à¥‡à¤µ à¤¨à¤¹à¥€à¤‚ à¤¹à¥‹à¤—à¥€, à¤¡à¥‡à¤Ÿà¤¾ à¤¸à¥€à¤§à¥‡ à¤¯à¥‚à¤œà¤¼à¤° à¤•à¥‡ à¤ªà¤¾à¤¸ à¤šà¤²à¤¾ à¤œà¤¾à¤à¤—à¤¾
        return Response(req.iter_content(chunk_size=1024*1024), headers=headers)
        
    except Exception as e:
        return f"Error downloading video: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
