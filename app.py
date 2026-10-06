import requests
from flask import Flask, request, Response

@app.route('/download-video')
def download_video_proxy():
    video_url = request.args.get('url')
    if not video_url:
        return "URL is missing", 400

    # ============================================================
    # यहाँ अपने Decodo या ASocks प्रॉक्सी की डिटेल्स ध्यान से भरें
    # ============================================================
    PROXY_USER = "zivhkhbm-rotate"
    PROXY_PASS = "46c1nmnz4r1o"
    PROXY_HOST = "p.webshare.io"
    PROXY_PORT = "80"

    proxies = {
        "http": f"http://{zivhkhbm-rotate}:{46c1nmnz4r1o}@{p.webshare.io}:{80}",
        "https": f"http://{zivhkhbm-rotate}:{46c1nmnz4r1o}@{p.webshare.io}:{80}"
    }
    # ============================================================

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'video/webm,video/any,video/*;q=0.9,/*;q=0.8',
            'Connection': 'keep-alive'
        }
        
        # अब यह रिक्वेस्ट प्रॉक्सी के ज़रिए जाएगी, जिससे ब्लॉक हट जाएगा
        req = requests.get(video_url, stream=True, headers=headers, proxies=proxies, timeout=30)
        
        if req.status_code != 200:
            return f"Proxy Response Error! Status Code: {req.status_code}", 400
        
        response_headers = {
            'Content-Disposition': 'attachment; filename="video.mp4"',
            'Content-Type': 'video/mp4'
        }
        
        return Response(
            req.iter_content(chunk_size=64 * 1024), 
            headers=response_headers
        )
        
    except requests.exceptions.ProxyError:
        return "Proxy Connection Error: क्रेडेंशियल्स दोबारा चेक करें।", 502
    except requests.exceptions.RequestException as e:
        return f"Server Error: {str(e)}", 500
