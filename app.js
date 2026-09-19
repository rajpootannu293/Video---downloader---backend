const http = require("http");
const { URL } = require("url");
const { Readable } = require("stream");

const PORT = process.env.PORT || 3000;

// अभी testing के लिए केवल इस authorized direct-video host को allow किया गया है
const ALLOWED_HOSTS = new Set([
  "interactive-examples.mdn.mozilla.net"
]);

function sendJSON(res, statusCode, data) {
  const body = JSON.stringify(data);

  res.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Content-Length": Buffer.byteLength(body)
  });

  res.end(body);
}

function sendText(res, statusCode, text) {
  res.writeHead(statusCode, {
    "Content-Type": "text/plain; charset=utf-8",
    "Access-Control-Allow-Origin": "*"
  });

  res.end(text);
}

const server = http.createServer(async (req, res) => {
  // CORS
  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
    });
    return res.end();
  }

  // Home
  if (req.method === "GET" && req.url === "/") {
    return sendText(
      res,
      200,
      "Video Downloader Backend is running!"
    );
  }

  // POST /api/download
  if (req.method === "POST" && req.url === "/api/download") {
    let body = "";

    req.on("data", chunk => {
      body += chunk.toString();

      // Request बहुत बड़ा होने से रोकना
      if (body.length > 10000) {
        req.destroy();
      }
    });

    req.on("end", () => {
      try {
        const data = JSON.parse(body);
        const videoURL = new URL(data.url);

        if (videoURL.protocol !== "https:") {
          return sendJSON(res, 400, {
            success: false,
            message: "Only HTTPS video URLs are allowed."
          });
        }

        if (!ALLOWED_HOSTS.has(videoURL.hostname)) {
          return sendJSON(res, 400, {
            success: false,
            message:
              "This video host is not allowed. Use an authorized direct MP4 URL."
          });
        }

        const downloadURL =
          `/api/fetch?url=${encodeURIComponent(videoURL.toString())}`;

        return sendJSON(res, 200, {
          success: true,
          downloadUrl: downloadURL
        });

      } catch (error) {
        return sendJSON(res, 400, {
          success: false,
          message: "Invalid video URL."
        });
      }
    });

    return;
  }

  // GET /api/fetch
  if (req.method === "GET" && req.url.startsWith("/api/fetch")) {
    try {
      const requestURL = new URL(
        req.url,
        `http://${req.headers.host}`
      );

      const target = requestURL.searchParams.get("url");

      if (!target) {
        return sendText(res, 400, "Video URL is required");
      }

      const videoURL = new URL(target);

      if (videoURL.protocol !== "https:") {
        return sendText(res, 400, "Only HTTPS URLs are allowed");
      }

      if (!ALLOWED_HOSTS.has(videoURL.hostname)) {
        return sendText(res, 403, "Video host is not allowed");
      }

      const response = await fetch(videoURL);

      if (!response.ok || !response.body) {
        return sendText(
          res,
          502,
          "Video could not be fetched"
        );
      }

      res.writeHead(200, {
        "Content-Type":
          response.headers.get("content-type") || "video/mp4",

        "Content-Disposition":
          'attachment; filename="video.mp4"',

        "Access-Control-Allow-Origin": "*"
      });

      Readable.fromWeb(response.body).pipe(res);

    } catch (error) {
      console.error("Download error:", error);

      if (!res.headersSent) {
        return sendText(
          res,
          500,
          "Download failed on server"
        );
      }
    }

    return;
  }

  sendText(res, 404, "Not Found");
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on port ${PORT}`);
});
