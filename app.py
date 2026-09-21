from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'All-in-One Downloader Backend Running!'})

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'URL is required'}), 400

    # URL से extra query parameters हटाएं
    clean_url = video_url.split('?')[0] if 'youtube' not in video_url and 'youtu.be' not in video_url else video_url

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            download_url = info.get('url')
            title = info.get('title', 'Downloaded Video')
            thumbnail = info.get('thumbnail', '')
            duration = info.get('duration_string', '')

            if download_url:
                return jsonify({
                    'status': 'success',
                    'title': title,
                    'thumbnail': thumbnail,
                    'duration': duration,
                    'download_url': download_url
                })
            else:
                return jsonify({'status': 'error', 'message': 'Video not found or private'}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/fetch-video', methods=['GET'])
def fetch_video():
    video_url = request.args.get('url')
    if not video_url:
        return "URL required", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        req = requests.get(video_url, headers=headers, stream=True)
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
