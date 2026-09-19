const express = require("express");

const app = express();

app.use(express.json());

// CORS
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.sendStatus(204);
  }

  next();
});

app.get("/", (req, res) => {
  res.send("Video Downloader Backend is running!");
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
