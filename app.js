const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();

app.use(cors());
app.use(express.json());

// RapidAPI Instagram Fetcher Bypass Route
app.post('/api/get-reel', async (req, res) => {
    const { reelUrl } = req.body;

    if (!reelUrl) {
        return res.status(400).json({ success: false, message: 'URL zaroori hai.' });
    }

    try {
        const options = {
            method: 'GET',
            url: 'https://instagram-looter2.p.rapidapi.com/reel',
            params: { url: reelUrl },
            headers: {
                // Aapki Original RapidAPI Key Yahan Set Kar Di Gayi Hai
                'x-rapidapi-key': 'de9ef331d3msh84dc97faf8d70cdp1630a9jsn0cdefc672446',
                'x-rapidapi-host': 'instagram-looter2.p.rapidapi.com'
            }
        };

        const response = await axios.request(options);
        
        // Video URL extraction
        const downloadUrl = response.data.download_url || response.data.media || (response.data[0] && response.data[0].url);

        if (!downloadUrl) {
            return res.status(404).json({ success: false, message: 'Video link nahi mil saka.' });
        }

        return res.json({
            success: true,
            data: { downloadUrl: downloadUrl }
        });

    } catch (error) {
        console.error('API Error:', error.message);
        return res.status(500).json({ success: false, message: 'Backend Sync Error! RapidAPI limit ya endpoint check karein.' });
    }
});

// Direct Video Stream Proxy Route (Blank Screen Problem Solve Karne Ke Liye)
app.get('/api/download-proxy', async (req, res) => {
    try {
        const videoUrl = req.query.url;
        if (!videoUrl) return res.status(400).send('URL missing');

        const response = await axios({
            method: 'get',
            url: videoUrl,
            responseType: 'stream',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        });

        res.setHeader('Content-Disposition', 'attachment; filename="Instagram_Reel.mp4"');
        res.setHeader('Content-Type', 'video/mp4');

        response.data.pipe(res);
    } catch (error) {
        res.status(500).send('Video stream karne me dikkat aayi.');
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server live on port ${PORT}`));
