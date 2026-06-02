import 'dotenv/config';
import { readFileSync, writeFileSync } from 'fs';
import { mkdir, writeFile } from 'fs/promises';
import { extname } from 'path';

const ACCOUNTS_FILE = 'accounts.json';
const OUTPUT_FILE = 'data/posts.json';
const APIFY_TOKEN = process.env.APIFY_TOKEN;
const ACTOR_ID = 'harvestapi~linkedin-profile-posts';

function mapPost(raw) {
  const profileUrl = raw.author?.linkedinUrl?.split('?')[0].replace(/\/?$/, '/') || '';
  const username = raw.author?.publicIdentifier || profileUrl.match(/\/in\/([^/?]+)/)?.[1] || '';

  return {
    id: raw.id || raw.entityId || raw.linkedinUrl || '',
    text: raw.content || '',
    url: raw.linkedinUrl || raw.socialContent?.shareUrl || '',
    author: {
      username,
      displayName: raw.author?.name || username,
      profileUrl
    },
    createdAt: raw.postedAt?.date || new Date().toISOString(),
    likeCount: raw.engagement?.likes ?? 0,
    commentCount: raw.engagement?.comments ?? 0,
    repostCount: raw.engagement?.shares ?? 0,
    imageUrls: (raw.postImages || []).map(img => img.url).filter(Boolean),
    localImagePaths: [],
    comment: ''
  };
}

async function downloadImages(post) {
  if (!post.imageUrls.length) return;
  const slug = post.id.replace(/[^a-z0-9]/gi, '_').slice(-40);
  const dir = `dashboard/images/${slug}`;
  await mkdir(dir, { recursive: true });
  const paths = [];
  for (let i = 0; i < post.imageUrls.length; i++) {
    const imgUrl = post.imageUrls[i];
    try {
      const res = await fetch(imgUrl, { headers: { 'Referer': 'https://www.linkedin.com/' } });
      if (!res.ok) continue;
      const buf = Buffer.from(await res.arrayBuffer());
      const ext = extname(new URL(imgUrl).pathname) || '.jpg';
      const localPath = `${dir}/image_${i}${ext}`;
      await writeFile(localPath, buf);
      paths.push(`/images/${slug}/image_${i}${ext}`);
    } catch { /* skip failed images */ }
  }
  post.localImagePaths = paths;
}

async function fetchAccount(profileUrl) {
  const input = {
    targetUrls: [profileUrl],
    maxPosts: 1,
    includeQuotePosts: true,
    includeReposts: false,
    maxComments: 0,
    maxReactions: 0,
    postNestedComments: false,
    postNestedReactions: false,
    scrapeComments: false,
    scrapeReactions: false
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

  const limitArg = process.argv.indexOf('--limit');
  const limit = limitArg !== -1 ? parseInt(process.argv[limitArg + 1], 10) : null;

  let accounts = JSON.parse(readFileSync(ACCOUNTS_FILE, 'utf-8'));
  if (limit && limit > 0) {
    accounts = accounts.slice(0, limit);
    console.log(`Test mode: limiting to first ${limit} accounts`);
  }
  await mkdir('data', { recursive: true });

  let firstPostLogged = false;
  const CONCURRENCY = 10;
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
      await downloadImages(mapped);
      const imgNote = mapped.localImagePaths.length ? ` (${mapped.localImagePaths.length} img)` : '';
      console.log(`1 post found${imgNote}`);
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
