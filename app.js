const express = require('express');
const cors = require('cors');
const ytdlp = require('yt-dlp-exec');
const axios = require('axios');

const app = express();

app.use(cors());
app.use(express.json());

app.post('/api/get-reel', async (req, res) => {
    const { reelUrl } = req.body;

    if (!reelUrl) {
        return res.status(400).json({ success: false, message: 'URL zaroori hai.' });
    }

    try {
        const output = await ytdlp(reelUrl, {
            dumpSingleJson: true,
            noCheckCertificates: true,
            noWarnings: true,
            preferFreeFormats: true,
            addHeader: [
                'referer:https://www.instagram.com/',
                'user-agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        });

        const directMp4Url = output.url || (output.formats && output.formats.length > 0 ? output.formats[0].url : null);

        if (!directMp4Url) {
            return res.status(404).json({ success: false, message: 'Download link nahi mila.' });
        }

        return res.json({
            success: true,
            data: {
                title: output.title || 'Instagram Reel',
                thumbnail: output.thumbnail || null,
                downloadUrl: directMp4Url
            }
        });

    } catch (error) {
        return res.status(500).json({ success: false, message: 'Server error ya Private post.' });
    }
});

// Proxy Route - CORS aur Blank Screen dikkat dur karne ke liye
app.get('/api/download-proxy', async (req, res) => {
    try {
        const videoUrl = req.query.url;
        if (!videoUrl) {
            return res.status(400).send('URL zaroori hai.');
        }

        const response = await axios({
            method: 'get',
            url: videoUrl,
            responseType: 'stream',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        });

        res.setHeader('Content-Disposition', 'attachment; filename="instagram-reel.mp4"');
        res.setHeader('Content-Type', 'video/mp4');

        response.data.pipe(res);
    } catch (error) {
        console.error('Proxy Error:', error.message);
        res.status(500).send('Video download me dikkat aayi.');
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
