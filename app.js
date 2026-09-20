const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();

app.use(cors());
app.use(express.json());

// Cobalt Direct Bypass Route (No API Key Required)
app.post('/api/get-reel', async (req, res) => {
    const { reelUrl } = req.body;

    if (!reelUrl) {
        return res.status(400).json({ success: false, message: 'URL zaroori hai.' });
    }

    try {
        const cleanUrl = reelUrl.split('?')[0];

        // Public Cobalt Engine Request
        const response = await axios.post('https://api.cobalt.tools/api/json', {
            url: cleanUrl
        }, {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });

        if (response.data && response.data.url) {
            return res.json({
                success: true,
                data: { downloadUrl: response.data.url }
            });
        } else {
            return res.status(404).json({ success: false, message: 'Video URL fetch nahi ho saka.' });
        }

    } catch (error) {
        console.error('Bypass Error:', error.message);
        return res.status(500).json({ success: false, message: 'Server busy hai. Dobara try karein.' });
    }
});

// Proxy Stream Route (Video download ke liye)
app.get('/api/download-proxy', async (req, res) => {
    try {
        const videoUrl = req.query.url;
        if (!videoUrl) return res.status(400).send('URL missing');

        const response = await axios({
            method: 'get',
            url: videoUrl,
            responseType: 'stream'
        });

        res.setHeader('Content-Disposition', 'attachment; filename="Instagram_Reel.mp4"');
        res.setHeader('Content-Type', 'video/mp4');

        response.data.pipe(res);
    } catch (error) {
        res.status(500).send('Stream Error');
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server live on port ${PORT}`));
