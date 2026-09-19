const express = require('express');
const cors = require('cors');
const ytDlp = require('yt-dlp-exec');

const app = express();

app.use(cors());
app.use(express.json());

app.post('/api/get-reel', async (req, res) => {
    const { reelUrl } = req.body;

    if (!reelUrl) {
        return res.status(400).json({ success: false, message: 'URL zaroori hai.' });
    }

    try {
        const output = await ytDlp(reelUrl, {
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

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
