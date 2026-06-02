import 'dotenv/config';
import { readFileSync, writeFileSync } from 'fs';
import { mkdir } from 'fs/promises';

const ACCOUNTS_FILE = 'accounts.json';
const OUTPUT_FILE = 'data/posts.json';
const APIFY_TOKEN = process.env.APIFY_TOKEN;
const ACTOR_ID = 'supreme_coder~linkedin-post';

function mapPost(raw) {
  if (raw.error) return null;

  const text = raw.text || '';
  const url = raw.url || '';
  const authorName = raw.authorName || `${raw.author?.firstName || ''} ${raw.author?.lastName || ''}`.trim();
  const authorProfileUrl = raw.authorProfileUrl || '';
  const authorUsername = raw.authorProfileId || raw.author?.publicId || authorProfileUrl.match(/\/in\/([^/?]+)/)?.[1] || authorName;
  const createdAt = raw.postedAtISO || (raw.postedAtTimestamp ? new Date(raw.postedAtTimestamp).toISOString() : new Date().toISOString());

  const imageUrls = (raw.images || []).filter(Boolean);

  return {
    id: raw.urn || raw.shareUrn || url,
    text,
    url,
    author: {
      username: authorUsername,
      displayName: authorName,
      profileUrl: authorProfileUrl
    },
    createdAt,
    likeCount: raw.numLikes ?? 0,
    commentCount: raw.numComments ?? 0,
    repostCount: raw.numShares ?? 0,
    imageUrls,
    comment: ''
  };
}

async function fetchAccount(profileUrl) {
  const input = {
    urls: [profileUrl],
    limitPerSource: 1
  };

  const url = `https://api.apify.com/v2/acts/${ACTOR_ID}/run-sync-get-dataset-items?token=${APIFY_TOKEN}`;

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Apify API error ${res.status}: ${text}`);
  }

  const data = await res.json();
  return Array.isArray(data) ? data : [];
}

async function main() {
  if (!APIFY_TOKEN) {
    console.error('Error: APIFY_TOKEN not found in .env');
    process.exit(1);
  }

  const accounts = JSON.parse(readFileSync(ACCOUNTS_FILE, 'utf-8'));
  await mkdir('data', { recursive: true });

  let firstPostLogged = false;
  const CONCURRENCY = 4;
  const results = [];

  async function processAccount(profileUrl, index) {
    const label = profileUrl.match(/\/in\/([^/]+)/)?.[1] || profileUrl;
    process.stdout.write(`[${index + 1}/${accounts.length}] Fetching ${label}... `);
    try {
      const posts = await fetchAccount(profileUrl);

      if (posts.length === 0) {
        console.log('0 posts');
        return null;
      }

      if (!firstPostLogged) {
        console.log('\n--- RAW FIRST POST ---');
        console.log(JSON.stringify(posts[0], null, 2));
        console.log('----------------------\n');
        firstPostLogged = true;
      }

      // Take the most recent non-error post
      const mapped = mapPost(posts[0]);
      if (!mapped) {
        console.log(`ERROR: ${posts[0].error}`);
        return null;
      }
      console.log(`1 post found`);
      return mapped;
    } catch (err) {
      console.log(`ERROR: ${err.message}`);
      return null;
    }
  }

  const queue = accounts.map((url, i) => ({ url, i }));
  const inFlight = new Set();

  await new Promise(resolve => {
    function dispatch() {
      while (inFlight.size < CONCURRENCY && queue.length > 0) {
        const { url, i } = queue.shift();
        const p = processAccount(url, i).then(result => {
          if (result) results.push(result);
          inFlight.delete(p);
          if (queue.length === 0 && inFlight.size === 0) resolve();
          else dispatch();
        });
        inFlight.add(p);
      }
    }
    dispatch();
  });

  writeFileSync(OUTPUT_FILE, JSON.stringify(results, null, 2));
  console.log(`\nDone. ${results.length} posts from ${results.length} account(s).`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
