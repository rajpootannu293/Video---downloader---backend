const express = require("express");
const { Readable } = require("stream");

const app = express();

app.use(express.json());

// Allow your TrebEdit/local website to connect
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  next();
});

app.get("/", (req, res) => {
  res.send("Video Downloader Backend is running!");
});

app.post("/api/download", async (req, res) => {
  try {
    const { url } = req.body;

    if (!url) {
      return res.status(400).json({
        success: false,
        message: "Video URL is required"
      });
    }

    const videoUrl = new URL(url);

    // For testing: only this authorized direct-video host
    if (
      videoUrl.protocol !== "https:" ||
      videoUrl.hostname !== "interactive-examples.mdn.mozilla.net"
    ) {
      return res.status(400).json({
        success: false,
        message: "Please use an authorized direct MP4 video URL."
      });
    }

    const response = await fetch(videoUrl);

    if (!response.ok || !response.body) {
      return res.status(502).json({
        success: false,
        message: "Video could not be fetched."
      });
    }

    res.setHeader(
      "Content-Type",
      response.headers.get("content-type") || "video/mp4"
    );

    res.setHeader(
      "Content-Disposition",
      'attachment; filename="video.mp4"'
    );

    const contentLength = response.headers.get("content-length");

    if (contentLength) {
      res.setHeader("Content-Length", contentLength);
    }

    Readable.fromWeb(response.body).pipe(res);

  } catch (error) {
    console.error(error);

    res.status(500).json({
      success: false,
      message: "Video download failed."
    });
  }
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on port ${PORT}`);
});
