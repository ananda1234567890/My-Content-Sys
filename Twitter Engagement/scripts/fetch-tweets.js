import 'dotenv/config';
import { readFileSync } from 'fs';
import { mkdir } from 'fs/promises';

const ACCOUNTS_FILE = 'accounts.json';
const OUTPUT_FILE = 'data/tweets.json';
const APIFY_TOKEN = process.env.APIFY_TOKEN;
const ACTOR_ID = 'delicious_zebu~ultimate-x-twitter-advanced-search-scraper';
const TIMEOUT_MS = 60_000;
const POLL_INTERVAL_MS = 3_000;

function getDates() {
  const fmt = d => {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  };
  const today = new Date();
  const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1);
  const yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1);
  return {
    today:     { startDate: fmt(today),     endDate: fmt(tomorrow) },
    yesterday: { startDate: fmt(yesterday), endDate: fmt(today) }
  };
}

function buildApifyInput(username, { startDate, endDate }) {
  return {
    All_of_these_words: '-filter:replies -filter:retweets',
    From_these_accounts: `@${username}`,
    Minimum_likes: 0,
    Minimum_replies: 0,
    Minimum_reposts: 0,
    endDate,
    language: 'any',
    maxItems: 3,
    splitMode: 'day',
    startDate,
    This_exact_phrase: '',
    Any_of_these_words: '',
    None_of_these_words: '',
    These_hashtags: '',
    To_these_accounts: '',
    Mentioning_these_accounts: ''
  };
}

function mapTweet(raw) {
  return {
    id: raw.tweetId?.toString() || '',
    text: raw.fullText || raw.text || '',
    url: raw.tweetUrl || '',
    author: {
      username: raw.authorHandle || '',
      displayName: raw.authorName || raw.authorHandle || ''
    },
    createdAt: raw.createdAt
      ? raw.createdAt.replace(' ', 'T').replace(/(\+\d{2})(\d{2})$/, '$1:$2')
      : new Date().toISOString(),
    likeCount: raw.likeCount ?? 0,
    replyCount: raw.replyCount ?? 0,
    retweetCount: raw.repostCount ?? 0,
    quoteCount: raw.quoteCount ?? 0,
    viewCount: raw.viewCount ?? 0,
    bookmarkCount: raw.bookmarkCount ?? 0,
    imageUrls: raw.imageUrls || [],
    comment: ''
  };
}

function isReply(text) {
  if (!text) return false;
  return text.startsWith('RT @') || text.startsWith('@');
}

async function startRun(username, dateRange) {
  const input = buildApifyInput(username, dateRange);
  const res = await fetch(
    `https://api.apify.com/v2/acts/${ACTOR_ID}/runs?token=${APIFY_TOKEN}`,
    { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(input) }
  );
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Apify API error ${res.status}: ${text}`);
  }
  const { data } = await res.json();
  return data.id;
}

async function abortRun(runId) {
  await fetch(`https://api.apify.com/v2/actor-runs/${runId}/abort?token=${APIFY_TOKEN}`, { method: 'POST' });
}

async function fetchWithTimeout(username, dateRange) {
  const runId = await startRun(username, dateRange);
  const start = Date.now();

  while (true) {
    if (Date.now() - start > TIMEOUT_MS) {
      await abortRun(runId);
      return { data: null, timedOut: true };
    }

    await new Promise(r => setTimeout(r, POLL_INTERVAL_MS));

    const statusRes = await fetch(`https://api.apify.com/v2/actor-runs/${runId}?token=${APIFY_TOKEN}`);
    const { data: run } = await statusRes.json();

    if (run.status === 'SUCCEEDED') {
      const itemsRes = await fetch(`https://api.apify.com/v2/actor-runs/${runId}/dataset/items?token=${APIFY_TOKEN}`);
      const items = await itemsRes.json();
      return { data: Array.isArray(items) ? items : [], timedOut: false };
    }

    if (['FAILED', 'ABORTED', 'TIMED-OUT'].includes(run.status)) {
      throw new Error(`Run ended with status: ${run.status}`);
    }
  }
}

async function main() {
  if (!APIFY_TOKEN) {
    console.error('Error: APIFY_TOKEN not found in .env');
    process.exit(1);
  }

  const limitArg = process.argv.indexOf('--limit');
  const limitN = limitArg !== -1 ? parseInt(process.argv[limitArg + 1], 10) : null;

  let accounts = JSON.parse(readFileSync(ACCOUNTS_FILE, 'utf-8'));
  if (limitN && limitN > 0) accounts = accounts.slice(0, limitN);
  const dates = getDates();
  let firstTweetLogged = false;

  await mkdir('data', { recursive: true });

  const CONCURRENCY = 6; // always 6 — do not change

  async function processAccount(username, index, total, isRetry = false) {
    const label = isRetry ? `[RETRY ${index + 1}/${total}]` : `[${index + 1}/${total}]`;
    process.stdout.write(`${label} Fetching @${username}... `);
    try {
      let { data: tweets, timedOut } = await fetchWithTimeout(username, dates.today);
      let source = 'today';

      if (timedOut) {
        console.log('TIMEOUT (>60s) — will retry');
        return { tweet: null, timedOut: true, username };
      }

      if (tweets.length === 0) {
        const result = await fetchWithTimeout(username, dates.yesterday);
        if (result.timedOut) {
          console.log('TIMEOUT (>60s) — will retry');
          return { tweet: null, timedOut: true, username };
        }
        tweets = result.data;
        source = 'yesterday';
      }

      if (tweets.length === 0) {
        console.log('0 tweets (no posts in date range)');
        return { tweet: null, timedOut: false };
      }

      if (!firstTweetLogged) {
        console.log('\n--- RAW FIRST TWEET ---');
        console.log(JSON.stringify(tweets[0], null, 2));
        console.log('------------------------\n');
        firstTweetLogged = true;
      }

      const filtered = tweets.filter(t => !isReply(t.fullText || t.text || ''));
      if (filtered.length > 0) {
        filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        const mapped = mapTweet(filtered[0]);
        console.log(`1 tweet found (${source})`);
        return { tweet: mapped, timedOut: false };
      } else {
        console.log('0 tweets (no non-reply posts)');
        return { tweet: null, timedOut: false };
      }
    } catch (err) {
      console.log(`ERROR: ${err.message}`);
      return { tweet: null, timedOut: false };
    }
  }

  async function runQueue(items, total, isRetry = false) {
    const queue = [...items];
    const inFlight = new Set();
    const results = [];
    const timedOut = [];

    await new Promise(resolve => {
      function dispatch() {
        while (inFlight.size < CONCURRENCY && queue.length > 0) {
          const { username, i } = queue.shift();
          const p = processAccount(username, i, total, isRetry).then(result => {
            if (result.timedOut) timedOut.push({ username, i });
            else if (result.tweet) results.push(result.tweet);
            inFlight.delete(p);
            if (queue.length === 0 && inFlight.size === 0) resolve();
            else dispatch();
          });
          inFlight.add(p);
        }
      }
      dispatch();
    });

    return { results, timedOut };
  }

  const allItems = accounts.map((username, i) => ({ username, i }));
  const { results: firstResults, timedOut } = await runQueue(allItems, accounts.length);
  const results = [...firstResults];

  if (timedOut.length > 0) {
    console.log(`\nRetrying ${timedOut.length} timed-out account(s)...`);
    const retryItems = timedOut.map(({ username }, i) => ({ username, i }));
    const { results: retryResults } = await runQueue(retryItems, timedOut.length, true);
    results.push(...retryResults);
  }

  results.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

  const { writeFileSync } = await import('fs');
  writeFileSync(OUTPUT_FILE, JSON.stringify(results, null, 2));

  console.log(`\nDone. ${results.length} tweets from ${results.length} account(s).`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
