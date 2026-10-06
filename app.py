import requests
from flask import Flask, request, Response

@app.route('/download-video')
def download_video_proxy():
    video_url = request.args.get('url')
    if not video_url:
        return "URL is missing", 400

    # ============================================================
    # यहाँ आपको अपनी प्रॉक्सी की डिटेल्स लिखनी हैं:
    # FORMAT: http://username:password@ip_address:port
    # ============================================================
    PROXY_USER = "zivhkhbm-rotate"
    PROXY_PASS = "46c1nmnz4r1o"
    PROXY_HOST = "p.webshare.io"
    PROXY_PORT = "80"

    # प्रॉक्सी डिक्शनरी तैयार करना
    proxies = {
        "http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}",
        "https": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    }
    # ============================================================

    try:
        # नकली ब्राउज़र हेडर्स ताकि सोशल मीडिया को शक न हो
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'video/webm,video/any,video/*;q=0.9,/*;q=0.8',
            'Connection': 'keep-alive'
        }
        
        # यहाँ proxies=proxies जोड़ दिया गया है, अब रेलवे का असली IP छुप जाएगा
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
        return "Proxy Error: प्रॉक्सी कनेक्ट नहीं हो पा रही है। क्रेडेंशियल्स चेक करें।", 502
    except requests.exceptions.RequestException as e:
        return f"Server Error: {str(e)}", 500
