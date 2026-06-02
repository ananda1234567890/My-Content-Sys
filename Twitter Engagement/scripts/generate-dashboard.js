import { readFileSync, writeFileSync } from 'fs';

const TWEETS_FILE = 'data/tweets.json';
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
  const tweets = JSON.parse(readFileSync(TWEETS_FILE, 'utf-8'));

  if (!tweets.length) {
    writeFileSync(OUTPUT_FILE, '<!DOCTYPE html><html><body style="font-family:system-ui;padding:40px"><h2>No tweets yet. Run /fetch-tweets first.</h2></body></html>');
    console.log('No tweets to render.');
    return;
  }

  tweets.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

  const groups = {};
  for (const t of tweets) {
    const key = t.author.username;
    if (!groups[key]) groups[key] = [];
    groups[key].push(t);
  }

  const lastFetch = new Date().toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: 'numeric', minute: '2-digit', hour12: true
  });

  const tweetRows = [];
  for (const [username, authorTweets] of Object.entries(groups)) {
    const tweet = authorTweets[0];
    const hasComment = tweet.comment && tweet.comment.trim().length > 0;
    const commentText = hasComment ? escapeHtml(tweet.comment) : '';
    const placeholder = hasComment ? '' : 'Write your comment here...';
    const copyLabel = hasComment ? 'Copy' : '—';

    const isThread = /https:\/\/t\.co\/\w+$/.test(tweet.text.trim());
    const viewStr = tweet.viewCount ? `<span class="stat" title="Views">👁 ${formatCount(tweet.viewCount)}</span>` : '';
    const bookmarkStr = tweet.bookmarkCount ? `<span class="stat" title="Bookmarks">🔖 ${formatCount(tweet.bookmarkCount)}</span>` : '';
    const imagesHtml = tweet.imageUrls && tweet.imageUrls.length > 0
      ? `<div class="tweet-images">${tweet.imageUrls.map(url => `<img src="${escapeAttr(url)}" alt=" tweet image" loading="lazy" />`).join('')}</div>`
      : '';

    tweetRows.push(`<div class="author-sep">
  <span class="author-avatar">${escapeHtml(tweet.author.displayName[0])}</span>
  <span class="author-name">${escapeHtml(tweet.author.displayName)}</span>
  <span class="author-handle">@${escapeHtml(username)}</span>
</div>

<div class="tweet-row">
  <div class="tweet-card">
    <div class="tweet-header">
      <a class="tweet-link" href="${escapeAttr(tweet.url)}" target="_blank" rel="noopener">
        <span class="author-name">${escapeHtml(tweet.author.displayName)}</span>
        <span class="author-handle">@${escapeHtml(tweet.author.username)}</span>
      </a>
      ${isThread ? '<span class="thread-badge">🧵 Thread</span>' : ''}
      <span class="tweet-time" title="${formatDate(tweet.createdAt)}">${timeAgo(tweet.createdAt)}</span>
    </div>
    <div class="tweet-text">${escapeHtml(tweet.text)}</div>
    ${imagesHtml}
    <div class="tweet-meta">
      ${viewStr}
      <span class="stat" title="Likes">♥ ${formatCount(tweet.likeCount)}</span>
      <span class="stat" title="Replies">↩ ${formatCount(tweet.replyCount)}</span>
      <span class="stat" title="Reposts">🔁 ${formatCount(tweet.retweetCount)}</span>
      <span class="stat" title="Quotes">" ${formatCount(tweet.quoteCount)}</span>
      ${bookmarkStr}
    </div>
  </div>
  <div class="comment-col">
    <textarea
      class="comment-box ${hasComment ? '' : 'empty'}"
      placeholder="Write your comment here..."
      data-tweet-id="${tweet.id}"
    >${commentText}</textarea>
    <div class="btn-row">
      <button class="btn-copy">${copyLabel}</button>
      <button class="btn-open" data-url="${escapeAttr(tweet.url)}">Open Tweet ↗</button>
      <span class="save-status"></span>
    </div>
  </div>
</div>`);
  }

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Twitter Engagement Dashboard</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #f4f4f4;
      --card-bg: #ffffff;
      --border: #e2e2e2;
      --text-primary: #1a1a1a;
      --text-secondary: #666666;
      --text-muted: #999999;
      --accent: #1a9be6;
      --accent-hover: #177ddf;
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

    .tweets-container {
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
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: var(--text-primary);
      color: #fff;
      font-size: 13px;
      font-weight: 600;
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

    .tweet-count {
      margin-left: auto;
      font-size: 12px;
      color: var(--text-muted);
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 2px 10px;
    }

    .tweet-row {
      display: grid;
      grid-template-columns: 1fr 360px;
      gap: 16px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px 20px;
      margin-bottom: 8px;
    }

    .tweet-link {
      text-decoration: none;
      color: inherit;
    }

    .tweet-link:hover .author-name {
      text-decoration: underline;
    }

    .tweet-header {
      display: flex;
      align-items: baseline;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 10px;
    }

    .tweet-time {
      font-size: 12px;
      color: var(--text-muted);
      margin-left: auto;
      cursor: default;
    }

    .thread-badge {
      font-size: 11px;
      font-weight: 600;
      color: #b8860b;
      background: #fff8e1;
      border: 1px solid #f0d060;
      border-radius: 20px;
      padding: 2px 8px;
      margin-left: auto;
    }

    .tweet-text {
      font-size: 15px;
      color: var(--text-primary);
      white-space: pre-wrap;
      word-break: break-word;
      margin-bottom: 12px;
      line-height: 1.6;
    }

    .tweet-meta {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }

    .tweet-images {
      display: flex;
      gap: 8px;
      margin: 10px 0;
      flex-wrap: wrap;
    }

    .tweet-images img {
      max-width: 200px;
      max-height: 200px;
      border-radius: 12px;
      object-fit: cover;
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
      box-shadow: 0 0 0 3px rgba(26, 155, 230, 0.1);
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
      .tweet-row {
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
    <h1>Twitter Engagement</h1>
    <div class="page-header-right">
      <p>${tweets.length} tweets across ${Object.keys(groups).length} accounts</p>
      <p>Last fetched ${lastFetch}</p>
    </div>
  </div>

  <div class="tweets-container">
    ${tweetRows.join('\n')}
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

    // Auto-resize textarea to fit content
    function autoResize(ta) {
      ta.style.height = 'auto';
      ta.style.height = ta.scrollHeight + 'px';
    }

    document.querySelectorAll('.comment-box').forEach(ta => autoResize(ta));

    // Auto-save: debounced POST to local server on every keystroke
    function debounce(fn, ms) {
      let t;
      return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
    }

    document.querySelectorAll('.comment-box').forEach(ta => {
      const col = ta.closest('.comment-col');
      const status = col.querySelector('.save-status');
      const copyBtn = col.querySelector('.btn-copy');

      const save = debounce(async () => {
        const id = ta.dataset.tweetId;
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
