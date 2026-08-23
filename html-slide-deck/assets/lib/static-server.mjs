/**
 * static-server.mjs — check-slides.mjs / render-previews.mjs 共用の最小静的サーバ
 *
 * `.dc.html` も見本 HTML も相対参照（`./support.js`・`../../tokens/colors.css`）を持つため、
 * `file://` ではなく http で配信して開く。ポートは 0 を指定して空きを自動選択する。
 *
 *   const srv = await startStaticServer({ root, fallbackDirs, routes });
 *   await page.goto(`${srv.origin}/${basename}`);
 *   await srv.close();
 *
 * - root         : 配信のルートディレクトリ（この外へは出られない）
 * - fallbackDirs : root に無いファイルを basename で探す代替ディレクトリ（runtime/ 等）
 * - routes       : { '/__probe__.html': { body, type } } の仮想ルート（ディスクに書かない）
 */
import http from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { extname, join, resolve, sep } from 'node:path';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.htm': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.otf': 'font/otf',
};

const mimeOf = (p) => MIME[extname(p).toLowerCase()] || 'application/octet-stream';

async function readIfFile(path) {
  try {
    const s = await stat(path);
    if (!s.isFile()) return null;
    return await readFile(path);
  } catch {
    return null;
  }
}

export async function startStaticServer({ root, fallbackDirs = [], routes = {} } = {}) {
  const rootAbs = resolve(root);
  const fallbacks = fallbackDirs.map((d) => resolve(d));

  const server = http.createServer(async (req, res) => {
    try {
      const url = new URL(req.url, 'http://127.0.0.1');
      const pathname = decodeURIComponent(url.pathname);

      const route = routes[pathname];
      if (route) {
        res.writeHead(200, { 'Content-Type': route.type || 'text/html; charset=utf-8' });
        res.end(route.body);
        return;
      }

      const rel = pathname.replace(/^\/+/, '');
      const target = resolve(rootAbs, rel);
      if (target !== rootAbs && !target.startsWith(rootAbs + sep)) {
        res.writeHead(403).end('forbidden');
        return;
      }

      let body = await readIfFile(target);
      let servedPath = target;
      if (body === null) {
        const base = rel.split('/').pop();
        for (const dir of fallbacks) {
          const cand = join(dir, base);
          const b = await readIfFile(cand);
          if (b !== null) { body = b; servedPath = cand; break; }
        }
      }
      if (body === null) {
        res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('not found: ' + pathname);
        return;
      }
      res.writeHead(200, { 'Content-Type': mimeOf(servedPath), 'Cache-Control': 'no-store' });
      res.end(body);
    } catch (e) {
      res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' }).end(String(e && e.message));
    }
  });

  await new Promise((ok, ng) => {
    server.once('error', ng);
    server.listen(0, '127.0.0.1', ok);
  });

  const port = server.address().port;
  return {
    server,
    port,
    origin: `http://127.0.0.1:${port}`,
    close: () => new Promise((ok) => server.close(() => ok())),
  };
}
