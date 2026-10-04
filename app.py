from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Backend is active and running!'})

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'URL is required'}), 400

    clean_url = video_url.strip()

    # yt-dlp Configuration optimized for Instagram, YouTube, Facebook & TikTok
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            
            if not info:
                return jsonify({'status': 'error', 'message': 'वीडियो डेटा नहीं मिल सका'}), 404

            download_url = None
            if 'entries' in info and len(info['entries']) > 0:
                download_url = info['entries'][0].get('url')
            else:
                download_url = info.get('url')

            title = info.get('title', 'Downloaded Video')
            thumbnail = info.get('thumbnail', '')

            if download_url:
                return jsonify({
                    'status': 'success',
                    'title': title,
                    'thumbnail': thumbnail,
                    'download_url': download_url
                })
            else:
                return jsonify({'status': 'error', 'message': 'डायरेक्ट डाउनलोड लिंक प्राप्त नहीं हुआ'}), 404

    except Exception as e:
        print("yt-dlp error:", str(e))
        return jsonify({'status': 'error', 'message': 'वीडियो डाउनलोड करने में असमर्थ। लिंक जांचें।'}), 500


@app.route('/fetch-video', methods=['GET'])
def fetch_video():
    video_url = request.args.get('url')
    if not video_url:
        return "URL required", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        req = requests.get(video_url, headers=headers, stream=True, timeout=20)
        content_length = req.headers.get('content-length')
        
        response_headers = {
            "Content-Disposition": "attachment; filename=video.mp4",
            "Content-Type": "video/mp4"
        }
        
        if content_length:
            response_headers["Content-Length"] = content_length

        return Response(
            req.iter_content(chunk_size=1024*1024),
            headers=response_headers
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
