import { createServer, request } from 'node:http';
import { createReadStream } from 'node:fs';
import { stat, realpath } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

export function byteRange(header, size) {
  const match = /^bytes=(\d*)-(\d*)$/.exec(header);
  if (!match || (!match[1] && !match[2]) || size === 0) return null;
  const start = match[1] ? Number(match[1]) : Math.max(0, size - Number(match[2]));
  const end = match[1] && match[2] ? Math.min(Number(match[2]), size - 1) : size - 1;
  return Number.isSafeInteger(start) && Number.isSafeInteger(end) && start <= end && start < size
    ? { start, end } : null;
}

const types = { '.mp4': 'video/mp4', '.webm': 'video/webm', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.png': 'image/png', '.vtt': 'text/vtt; charset=utf-8', '.svg': 'image/svg+xml' };

export async function previewServer({ port = 8787, upstreamPort = 8788, root = process.cwd() } = {}) {
  const mediaRoot = await realpath(path.join(root, 'public', 'media'));
  const server = createServer(async (req, res) => {
    try {
      const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      if (!pathname.startsWith('/media/')) {
        const upstream = request({ hostname: '127.0.0.1', port: upstreamPort,
          path: req.url, method: req.method, headers: { ...req.headers, host: `127.0.0.1:${upstreamPort}` } }, response => {
          res.writeHead(response.statusCode, response.headers);
          response.pipe(res);
        });
        upstream.on('error', () => { if (!res.headersSent) res.writeHead(502); res.end('Preview backend unavailable'); });
        req.on('aborted', () => upstream.destroy());
        req.pipe(upstream);
        return;
      }
      if (!['GET', 'HEAD'].includes(req.method)) {
        res.writeHead(405, { Allow: 'GET, HEAD' }); res.end(); return;
      }
      const candidate = path.resolve(mediaRoot, pathname.slice('/media/'.length));
      if (!candidate.startsWith(mediaRoot + path.sep)) { res.writeHead(403); res.end(); return; }
      const filename = await realpath(candidate);
      if (!filename.startsWith(mediaRoot + path.sep)) { res.writeHead(403); res.end(); return; }
      const info = await stat(filename);
      if (!info.isFile()) { res.writeHead(404); res.end(); return; }
      const range = req.headers.range ? byteRange(req.headers.range, info.size) : undefined;
      if (range === null) {
        res.writeHead(416, { 'Content-Range': `bytes */${info.size}` }); res.end(); return;
      }
      res.writeHead(range ? 206 : 200, {
        'Content-Type': types[path.extname(filename).toLowerCase()] || 'application/octet-stream',
        'Accept-Ranges': 'bytes',
        'Content-Length': range ? range.end - range.start + 1 : info.size,
        'Cache-Control': 'no-cache',
        ...(range ? { 'Content-Range': `bytes ${range.start}-${range.end}/${info.size}` } : {}),
      });
      if (req.method === 'HEAD') { res.end(); return; }
      const stream = createReadStream(filename, range);
      stream.on('error', () => res.destroy());
      res.on('close', () => stream.destroy());
      stream.pipe(res);
    } catch (error) {
      if (!res.headersSent) res.writeHead(error.code === 'ENOENT' ? 404 : 400);
      res.end();
    }
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(port, '127.0.0.1', resolve);
  });
  return server;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  const { values } = parseArgs({ options: { port: { type: 'string', default: '8787' },
    'upstream-port': { type: 'string', default: '8788' } } });
  await previewServer({ port: Number(values.port), upstreamPort: Number(values['upstream-port']) });
  console.log(`Media-enabled preview: http://127.0.0.1:${values.port}`);
}
