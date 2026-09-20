const express = require('express');
const cors = require('cors');
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
        // RapidAPI ki madad se video link lena
        const options = {
            method: 'GET',
            url: 'https://instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com/index',
            params: { url: reelUrl },
            headers: {
                // NEECHE APNI RAPIDAPI KEY CHIPAEYIN
                'x-rapidapi-key': 'de9ef331d3msh84dc97faf8d70cdp1...',
                'x-rapidapi-host': 'instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com'
            }
        };

        const response = await axios.request(options);
        const downloadUrl = response.data.media || response.data.download_url || (Array.isArray(response.data) ? response.data[0]?.url : null);

        if (!downloadUrl) {
            return res.status(404).json({ success: false, message: 'Download link nahi mila.' });
        }

        return res.json({
            success: true,
            data: {
                downloadUrl: downloadUrl
            }
        });

    } catch (error) {
        console.error('API Error:', error.message);
        return res.status(500).json({ success: false, message: 'Server error ya Invalid URL.' });
    }
});

// Proxy Route - Video File Stream karne ke liye
app.get('/api/download-proxy', async (req, res) => {
    try {
        const videoUrl = req.query.url;
        if (!videoUrl) {
            return res.status(400).send('URL zaroori hai.');
        }

        const response = await axios({
            method: 'get',
            url: videoUrl,
            responseType: 'stream'
        });

        res.setHeader('Content-Disposition', 'attachment; filename="reel.mp4"');
        res.setHeader('Content-Type', 'video/mp4');

        response.data.pipe(res);
    } catch (error) {
        res.status(500).send('Video download karne me dikkat aayi.');
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
