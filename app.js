const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.json({
    success: true,
    message: "Video Downloader Backend is running!"
  });
});

app.post("/api/download", (req, res) => {
  const { url } = req.body;

  if (!url) {
    return res.status(400).json({
      success: false,
      message: "Video URL is required"
    });
  }

  try {
    const videoUrl = new URL(url);

    if (
      videoUrl.protocol !== "http:" &&
      videoUrl.protocol !== "https:"
    ) {
      throw new Error("Invalid URL");
    }

    res.json({
      success: true,
      downloadUrl: videoUrl.toString()
    });

  } catch (error) {
    res.status(400).json({
      success: false,
      message: "Invalid video URL"
    });
  }
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on port ${PORT}`);
});
