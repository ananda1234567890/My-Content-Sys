import { createServer } from 'http';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { exec } from 'child_process';

const PORT = 3002;
const DASHBOARD_FILE = 'outputs/dashboard.html';
const STATUS_FILE = 'outputs/post-status.json';

function readStatus() {
  try { return JSON.parse(readFileSync(STATUS_FILE, 'utf-8')); }
  catch { return {}; }
}

function writeStatus(data) {
  writeFileSync(STATUS_FILE, JSON.stringify(data, null, 2));
}

const server = createServer((req, res) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  if (req.method === 'OPTIONS') { res.writeHead(204, headers); res.end(); return; }

  if (req.method === 'GET' && (req.url === '/' || req.url === '/index.html')) {
    try {
      const html = readFileSync(DASHBOARD_FILE, 'utf-8');
      res.writeHead(200, { ...headers, 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
      res.end(html);
    } catch {
      res.writeHead(500, headers);
      res.end('<h2>Dashboard not found. Run: python scripts/build-dashboard.py</h2>');
    }
    return;
  }

  if (req.method === 'GET' && req.url === '/api/status') {
    res.writeHead(200, { ...headers, 'Content-Type': 'application/json' });
    res.end(JSON.stringify(readStatus()));
    return;
  }

  if (req.method === 'POST' && req.url === '/api/status') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const { num, platform, value } = JSON.parse(body);
        const data = readStatus();
        if (!data[num]) data[num] = {};
        data[num][platform] = value;
        writeStatus(data);
        res.writeHead(200, { ...headers, 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: true }));
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
    exec(`powershell -Command "Get-NetTCPConnection -LocalPort ${PORT} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"`, () => {
      setTimeout(() => server.listen(PORT), 800);
    });
  } else {
    console.error('Server error:', e);
    process.exit(1);
  }
});

server.listen(PORT, () => {
  console.log(`Content dashboard running at http://localhost:${PORT}`);
});
