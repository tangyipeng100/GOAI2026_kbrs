import { createServer } from "node:http";
import { createReadStream } from "node:fs";
import { realpath, stat } from "node:fs/promises";
import path from "node:path";
import { byteRange } from "./preview-media.mjs";

const root = await realpath(path.resolve("out"));
const prefix = "/GOAI2026_kbrs";
const port = Number(process.argv[2] || 8790);
const types = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8", ".json": "application/json",
  ".txt": "text/plain; charset=utf-8", ".svg": "image/svg+xml",
  ".png": "image/png", ".jpg": "image/jpeg", ".mp4": "video/mp4",
  ".vtt": "text/vtt; charset=utf-8", ".woff2": "font/woff2",
};

createServer(async (req, res) => {
  try {
    const pathname = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
    if (pathname === prefix) {
      res.writeHead(302, { Location: `${prefix}/` }); res.end(); return;
    }
    if (!pathname.startsWith(`${prefix}/`) || !["GET", "HEAD"].includes(req.method)) {
      res.writeHead(404); res.end(); return;
    }
    const relative = pathname.slice(prefix.length + 1) || "index.html";
    const candidate = path.resolve(root, relative.endsWith("/") ? `${relative}index.html` : relative);
    if (!candidate.startsWith(root + path.sep)) {
      res.writeHead(403); res.end(); return;
    }
    const filename = await realpath(candidate);
    if (!filename.startsWith(root + path.sep)) {
      res.writeHead(403); res.end(); return;
    }
    const info = await stat(filename);
    if (!info.isFile()) { res.writeHead(404); res.end(); return; }
    const range = req.headers.range ? byteRange(req.headers.range, info.size) : undefined;
    if (range === null) {
      res.writeHead(416, { "Content-Range": `bytes */${info.size}` }); res.end(); return;
    }
    res.writeHead(range ? 206 : 200, {
      "Content-Type": types[path.extname(filename)] || "application/octet-stream",
      "Content-Length": range ? range.end - range.start + 1 : info.size,
      "Accept-Ranges": "bytes",
      ...(range ? { "Content-Range": `bytes ${range.start}-${range.end}/${info.size}` } : {}),
    });
    if (req.method === "HEAD") { res.end(); return; }
    createReadStream(filename, range).pipe(res);
  } catch (error) {
    res.writeHead(error.code === "ENOENT" ? 404 : 400); res.end();
  }
}).listen(port, "127.0.0.1", () => {
  console.log(`Pages preview: http://127.0.0.1:${port}${prefix}/`);
});
