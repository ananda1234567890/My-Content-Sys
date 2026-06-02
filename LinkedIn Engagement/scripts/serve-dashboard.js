import { createServer } from 'http';
import { readFileSync, writeFileSync } from 'fs';
import { extname, join } from 'path';
import { exec } from 'child_process';

const PORT = 3001;
const POSTS_FILE = 'data/posts.json';
const DASHBOARD_FILE = 'dashboard/index.html';

const server = createServer((req, res) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  if (req.method === 'OPTIONS') {
    res.writeHead(204, headers);
    res.end();
    return;
  }

  // Serve local post images
  if (req.method === 'GET' && req.url.startsWith('/images/')) {
    try {
      const filePath = join('dashboard', req.url);
      const ext = extname(filePath).toLowerCase();
      const mime = { '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.gif': 'image/gif' }[ext] || 'application/octet-stream';
      const data = readFileSync(filePath);
      res.writeHead(200, { ...headers, 'Content-Type': mime, 'Cache-Control': 'max-age=86400' });
      res.end(data);
    } catch {
      res.writeHead(404, headers);
      res.end('Image not found');
    }
    return;
  }

  if (req.method === 'GET' && (req.url === '/' || req.url === '/index.html')) {
    try {
      const html = readFileSync(DASHBOARD_FILE, 'utf-8');
      res.writeHead(200, { ...headers, 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
      res.end(html);
    } catch {
      res.writeHead(500, headers);
      res.end('<h2>Dashboard not found. Run generate-dashboard.js first.</h2>');
    }
    return;
  }

  if (req.method === 'POST' && req.url === '/api/comment') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const { id, comment } = JSON.parse(body);
        const posts = JSON.parse(readFileSync(POSTS_FILE, 'utf-8'));
        const post = posts.find(p => p.id === id);
        if (post) {
          post.comment = comment;
          writeFileSync(POSTS_FILE, JSON.stringify(posts, null, 2));
          res.writeHead(200, { ...headers, 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ ok: true }));
        } else {
          res.writeHead(404, headers);
          res.end(JSON.stringify({ ok: false, error: 'Post not found' }));
        }
      } catch (e) {
        res.writeHead(400, headers);
        res.end(JSON.stringify({ ok: false, error: e.message }));
      }
    });
    return;
  }

  res.writeHead(404, headers);
  res.end('Not found');
});

server.on('error', e => {
  if (e.code === 'EADDRINUSE') {
    exec(`lsof -ti tcp:${PORT} | xargs kill -9`, () => {
      setTimeout(() => server.listen(PORT), 500);
    });
  } else {
    console.error('Server error:', e);
    process.exit(1);
  }
});

server.listen(PORT, () => {
  const url = `http://localhost:${PORT}`;
  console.log(`Dashboard running at ${url}`);
  exec(`open ${url}`);
});
