from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

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

    # Clean URL (Remove tracking parameters)
    clean_url = video_url.split('?')[0]

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            
            # Extract video URL
            download_url = None
            if 'url' in info:
                download_url = info['url']
            elif 'entries' in info and len(info['entries']) > 0:
                download_url = info['entries'][0].get('url')

            if download_url:
                return jsonify({
                    'status': 'success',
                    'title': info.get('title', 'Instagram Video'),
                    'download_url': download_url
                })
            else:
                return jsonify({'status': 'error', 'message': 'Video URL not found'}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
