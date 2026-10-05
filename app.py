from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Backend is active and running!"
    })


@app.route("/download", methods=["GET"])
def download():
    video_url = request.args.get("url")

    if not video_url:
        return jsonify({
            "error": "URL is required"
        }), 400

    clean_url = video_url.strip()

    ydl_opts = {
        "format": "best",
        "quiet": True,
        "no_warnings": True,
        "nochekcertificate": True,
        "ignoreerrors": True,
        "extractor_args": {
            "instagram": {
                "web_query": True
            }
        },
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Fetch-Mode": "navigate"
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                clean_url,
                download=False
            )

            if not info:
                return jsonify({
                    "status": "error",
                    "message": "वीडियो नहीं मिला"
                }), 404

            download_url = None

            if info.get("entries") and len(info["entries"]) > 0:
                first_entry = info["entries"][0]

                if first_entry:
                    download_url = first_entry.get("url")

            else:
                download_url = info.get("url")

            if not download_url:
                return jsonify({
                    "status": "error",
                    "message": "Direct download link प्राप्त नहीं हुआ"
                }), 404

            title = info.get("title", "Downloaded Video")
            thumbnail = info.get("thumbnail", "")

            return jsonify({
                "status": "success",
                "title": title,
                "thumbnail": thumbnail,
                "download_url": download_url
            })

    except Exception as e:
        print("yt-dlp error:", str(e))

        return jsonify({
            "status": "error",
            "message": "वीडियो प्राप्त करने में समस्या हुई"
        }), 500


@app.route("/fetch-video", methods=["GET"])
def fetch_video():
    video_url = request.args.get("url")

    if not video_url:
        return jsonify({
            "error": "URL is required"
        }), 400

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        req = requests.get(
            video_url,
            headers=headers,
            stream=True,
            timeout=20
        )

        req.raise_for_status()

        response_headers = {
            "Content-Disposition": 'attachment; filename="video.mp4"',
            "Content-Type": req.headers.get(
                "Content-Type",
                "video/mp4"
            )
        }

        content_length = req.headers.get("Content-Length")

        if content_length:
            response_headers["Content-Length"] = content_length

        return Response(
            req.iter_content(chunk_size=1024 * 1024),
            headers=response_headers
        )

    except Exception as e:
        print("fetch-video error:", str(e))

        return jsonify({
            "status": "error",
            "message": "वीडियो डाउनलोड नहीं हो सका"
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
