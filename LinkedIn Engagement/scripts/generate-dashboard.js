import { readFileSync, writeFileSync } from 'fs';

const POSTS_FILE = 'data/posts.json';
const OUTPUT_FILE = 'dashboard/index.html';

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeAttr(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;');
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: 'numeric', minute: '2-digit', hour12: true
    });
  } catch {
    return iso;
  }
}

function timeAgo(iso) {
  try {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  } catch {
    return '';
  }
}

function formatCount(n) {
  if (!n && n !== 0) return '';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

async function main() {
  const posts = JSON.parse(readFileSync(POSTS_FILE, 'utf-8'));

  if (!posts.length) {
    writeFileSync(OUTPUT_FILE, '<!DOCTYPE html><html><body style="font-family:system-ui;padding:40px"><h2>No posts yet. Run fetch-posts first.</h2></body></html>');
    console.log('No posts to render.');
    return;
  }

  posts.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

  const lastFetch = new Date().toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: 'numeric', minute: '2-digit', hour12: true
  });

  const postRows = posts.map(post => {
    const hasComment = post.comment && post.comment.trim().length > 0;
    const commentText = hasComment ? escapeHtml(post.comment) : '';
    const copyLabel = hasComment ? 'Copy' : '—';

    const displayImages = (post.localImagePaths && post.localImagePaths.length > 0)
      ? post.localImagePaths
      : (post.imageUrls || []);
    const imagesHtml = displayImages.length > 0
      ? `<div class="post-images">${displayImages.map(url => `<img src="${escapeAttr(url)}" alt="post image" loading="lazy" />`).join('')}</div>`
      : '';

    const initials = (post.author.displayName || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();

    return `<div class="author-sep">
  <span class="author-avatar">${escapeHtml(initials)}</span>
  <span class="author-name">${escapeHtml(post.author.displayName)}</span>
  <span class="author-handle">${escapeHtml(post.author.username)}</span>
</div>

<div class="post-row">
  <div class="post-card">
    <div class="post-header">
      <a class="post-link" href="${escapeAttr(post.author.profileUrl || post.url)}" target="_blank" rel="noopener">
        <span class="author-name">${escapeHtml(post.author.displayName)}</span>
      </a>
      <span class="post-time" title="${formatDate(post.createdAt)}">${timeAgo(post.createdAt)}</span>
    </div>
    ${(post.text.length > 280)
      ? `<div class="post-text"><span class="text-short">${escapeHtml(post.text.slice(0, 280))}<span class="text-ellipsis">...</span></span><span class="text-full" style="display:none">${escapeHtml(post.text)}</span><button class="btn-read-more">Read more</button></div>`
      : `<div class="post-text">${escapeHtml(post.text)}</div>`
    }
    ${imagesHtml}
    <div class="post-meta">
      <span class="stat" title="Reactions">👍 ${formatCount(post.likeCount)}</span>
      <span class="stat" title="Comments">💬 ${formatCount(post.commentCount)}</span>
      <span class="stat" title="Reposts">🔁 ${formatCount(post.repostCount)}</span>
    </div>
  </div>
  <div class="comment-col">
    <textarea
      class="comment-box ${hasComment ? '' : 'empty'}"
      placeholder="Write your comment here..."
      data-post-id="${escapeAttr(post.id)}"
    >${commentText}</textarea>
    <div class="btn-row">
      <button class="btn-copy">${copyLabel}</button>
      <button class="btn-open" data-url="${escapeAttr(post.url)}">Open Post ↗</button>
      <span class="save-status"></span>
    </div>
  </div>
</div>`;
  });

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LinkedIn Engagement Dashboard</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #f3f2ef;
      --card-bg: #ffffff;
      --border: #e0dfdc;
      --text-primary: #1a1a1a;
      --text-secondary: #666666;
      --text-muted: #999999;
      --accent: #0077b5;
      --accent-hover: #005fa3;
      --copy-btn-bg: #fff;
      --copy-btn-border: #ccc;
      --comment-bg: #fafafa;
      --comment-empty-bg: #f7f7f7;
      --comment-empty-text: #bbb;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text-primary);
      padding: 28px 20px;
      line-height: 1.5;
    }

    .page-header {
      max-width: 1100px;
      margin: 0 auto 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }

    .page-header h1 {
      font-size: 22px;
      font-weight: 700;
      color: var(--text-primary);
    }

    .page-header-right {
      text-align: right;
    }

    .page-header-right p {
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.6;
    }

    .posts-container {
      max-width: 1100px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 0;
    }

    .author-sep {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 18px 0 8px;
      border-bottom: 2px solid var(--border);
      margin-bottom: 10px;
    }

    .author-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: var(--accent);
      color: #fff;
      font-size: 12px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .author-name {
      font-weight: 700;
      font-size: 15px;
      color: var(--text-primary);
    }

    .author-handle {
      font-size: 13px;
      color: var(--text-secondary);
    }

    .post-row {
      display: grid;
      grid-template-columns: 1fr 360px;
      gap: 16px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px 20px;
      margin-bottom: 8px;
    }

    .post-link {
      text-decoration: none;
      color: inherit;
    }

    .post-link:hover .author-name {
      text-decoration: underline;
      color: var(--accent);
    }

    .post-header {
      display: flex;
      align-items: baseline;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }

    .post-time {
      font-size: 12px;
      color: var(--text-muted);
      margin-left: auto;
      cursor: default;
    }

    .post-text {
      font-size: 15px;
      color: var(--text-primary);
      white-space: pre-wrap;
      word-break: break-word;
      margin-bottom: 12px;
      line-height: 1.6;
    }

    .post-meta {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }

    .post-images {
      display: flex;
      gap: 8px;
      margin: 10px 0;
      flex-wrap: wrap;
    }

    .post-images img {
      max-width: 280px;
      max-height: 280px;
      border-radius: 8px;
      object-fit: cover;
    }

    .btn-read-more {
      background: none;
      border: none;
      color: var(--accent);
      font-size: 13px;
      cursor: pointer;
      padding: 2px 0 0;
      font-family: inherit;
      display: block;
    }

    .btn-read-more:hover {
      text-decoration: underline;
    }

    .stat {
      font-size: 12px;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 3px;
    }

    .comment-col {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .comment-box {
      width: 100%;
      min-height: 96px;
      padding: 10px 14px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      color: var(--text-primary);
      background: var(--comment-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      resize: none;
      overflow: hidden;
      outline: none;
      transition: border-color 0.15s, box-shadow 0.15s;
      line-height: 1.55;
    }

    .comment-box.empty {
      color: var(--comment-empty-text);
      background: var(--comment-empty-bg);
      cursor: default;
    }

    .comment-box:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(0, 119, 181, 0.1);
    }

    .btn-row {
      display: flex;
      gap: 8px;
    }

    .btn-copy {
      flex: 1;
      padding: 8px 0;
      font-size: 13px;
      border: 1px solid var(--copy-btn-border);
      border-radius: 24px;
      background: var(--copy-btn-bg);
      color: var(--text-secondary);
      cursor: pointer;
      font-family: inherit;
      transition: background 0.15s, color 0.15s;
    }

    .btn-copy:hover {
      background: #f0f0f0;
      color: var(--text-primary);
    }

    .btn-copy.copied {
      color: #1a9a4a;
      border-color: #1a9a4a;
    }

    .btn-open {
      flex: 1;
      padding: 8px 0;
      font-size: 13px;
      border: none;
      border-radius: 24px;
      background: var(--accent);
      color: #fff;
      cursor: pointer;
      text-decoration: none;
      font-family: inherit;
      text-align: center;
      display: inline-block;
      transition: background 0.15s;
    }

    .btn-open:hover {
      background: var(--accent-hover);
    }

    .save-status {
      font-size: 11px;
      color: #1a9a4a;
      white-space: nowrap;
      align-self: center;
      min-width: 44px;
      text-align: right;
      opacity: 0;
      transition: opacity 0.2s;
    }

    .save-status.show {
      opacity: 1;
    }

    .copied-toast {
      position: fixed;
      bottom: 28px;
      left: 50%;
      transform: translateX(-50%) translateY(8px);
      background: var(--text-primary);
      color: #fff;
      padding: 9px 20px;
      border-radius: 24px;
      font-size: 13px;
      opacity: 0;
      transition: opacity 0.2s, transform 0.2s;
      pointer-events: none;
      z-index: 100;
    }

    .copied-toast.show {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }

    @media (max-width: 720px) {
      .post-row {
        grid-template-columns: 1fr;
        padding: 14px 16px;
      }
      body {
        padding: 16px 12px;
      }
    }
  </style>
</head>
<body>
  <div class="page-header">
    <h1>LinkedIn Engagement</h1>
    <div class="page-header-right">
      <p>${posts.length} posts across ${posts.length} account(s)</p>
      <p>Last fetched ${lastFetch}</p>
    </div>
  </div>

  <div class="posts-container">
    ${postRows.join('\n')}
  </div>

  <div class="copied-toast" id="toast">Copied!</div>

  <script>
    function getCommentText(btn) {
      return btn.closest('.comment-col').querySelector('.comment-box').value;
    }

    function showCopied(btn) {
      const prev = btn.textContent;
      btn.classList.add('copied');
      btn.textContent = 'Copied!';
      const toast = document.getElementById('toast');
      toast.classList.add('show');
      setTimeout(() => {
        toast.classList.remove('show');
        btn.classList.remove('copied');
        btn.textContent = prev;
      }, 1800);
    }

    function copySync(text) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); } catch(e) {}
      document.body.removeChild(ta);
    }

    document.querySelectorAll('.btn-copy').forEach(btn => {
      btn.addEventListener('click', () => {
        const text = getCommentText(btn);
        if (!text) return;
        copySync(text);
        showCopied(btn);
      });
    });

    document.querySelectorAll('.btn-open').forEach(btn => {
      btn.addEventListener('click', () => {
        const text = getCommentText(btn);
        if (text) {
          copySync(text);
          showCopied(btn);
        }
        window.open(btn.dataset.url, '_blank', 'noopener,noreferrer');
      });
    });

    function autoResize(ta) {
      ta.style.height = 'auto';
      ta.style.height = ta.scrollHeight + 'px';
    }

    document.querySelectorAll('.comment-box').forEach(ta => autoResize(ta));

    function debounce(fn, ms) {
      let t;
      return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
    }

    document.querySelectorAll('.btn-read-more').forEach(btn => {
      btn.addEventListener('click', () => {
        const box = btn.closest('.post-text');
        const short = box.querySelector('.text-short');
        const full = box.querySelector('.text-full');
        const collapsed = full.style.display === 'none';
        short.style.display = collapsed ? 'none' : 'inline';
        full.style.display = collapsed ? 'inline' : 'none';
        btn.textContent = collapsed ? 'Show less' : 'Read more';
      });
    });

    document.querySelectorAll('.comment-box').forEach(ta => {
      const col = ta.closest('.comment-col');
      const status = col.querySelector('.save-status');
      const copyBtn = col.querySelector('.btn-copy');

      const save = debounce(async () => {
        const id = ta.dataset.postId;
        if (!id) return;
        try {
          const r = await fetch('/api/comment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, comment: ta.value })
          });
          if (r.ok && status) {
            status.textContent = 'Saved ✓';
            status.classList.add('show');
            setTimeout(() => status.classList.remove('show'), 2000);
          }
        } catch (_) {}
      }, 600);

      ta.addEventListener('input', () => {
        ta.classList.remove('empty');
        if (copyBtn && ta.value.trim()) copyBtn.textContent = 'Copy';
        autoResize(ta);
        save();
      });
    });
  </script>
</body>
</html>`;

  writeFileSync(OUTPUT_FILE, html);
  console.log(`Dashboard written to ${OUTPUT_FILE}`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
