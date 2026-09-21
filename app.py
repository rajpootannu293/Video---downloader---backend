from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Server is running live!'})

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'URL is required'}), 400

    clean_url = video_url.split('?')[0]

    ydl_opts = {
        'format': 'best',
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

            if download_url:
                return jsonify({
                    'status': 'success',
                    'download_url': download_url
                })
            else:
                return jsonify({'status': 'error', 'message': 'Video URL not found'}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Direct Force Download Endpoint
@app.route('/fetch-video', methods=['GET'])
def fetch_video():
    video_url = request.args.get('url')
    if not video_url:
        return "URL required", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Stream video directly from Instagram CDN
    req = requests.get(video_url, headers=headers, stream=True)
    
    return Response(
        req.iter_content(chunk_size=1024*1024),
        content_type='video/mp4',
        headers={
            "Content-Disposition": "attachment; filename=instagram_video.mp4"
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
