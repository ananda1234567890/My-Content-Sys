import 'dotenv/config';
import { readFileSync } from 'fs';
import { mkdir } from 'fs/promises';

const ACCOUNTS_FILE = 'accounts.json';
const OUTPUT_FILE = 'data/tweets.json';
const APIFY_TOKEN = process.env.APIFY_TOKEN;
const ACTOR_ID = 'delicious_zebu~ultimate-x-twitter-advanced-search-scraper';

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

async function fetchAccount(username, dates) {
  const input = buildApifyInput(username, dates);
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
  const dates = getDates();
  let firstTweetLogged = false;

  await mkdir('data', { recursive: true });

  const CONCURRENCY = 6;

  async function processAccount(username, index) {
    process.stdout.write(`[${index + 1}/${accounts.length}] Fetching @${username}... `);
    try {
      let tweets = await fetchAccount(username, dates.today);
      let source = 'today';

      if (tweets.length === 0) {
        tweets = await fetchAccount(username, dates.yesterday);
        source = 'yesterday';
      }

      if (tweets.length === 0) {
        console.log('0 tweets (no posts in date range)');
        return null;
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
        return mapped;
      } else {
        console.log(`0 tweets (no non-reply posts)`);
        return null;
      }
    } catch (err) {
      console.log(`ERROR: ${err.message}`);
      return null;
    }
  }

  const queue = accounts.map((username, i) => ({ username, i }));
  const inFlight = new Set();
  const results = [];

  await new Promise(resolve => {
    function dispatch() {
      while (inFlight.size < CONCURRENCY && queue.length > 0) {
        const { username, i } = queue.shift();
        const p = processAccount(username, i).then(result => {
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

  results.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

  const { writeFileSync } = await import('fs');
  writeFileSync(OUTPUT_FILE, JSON.stringify(results, null, 2));

  console.log(`\nDone. ${results.length} tweets from ${results.length} account(s).`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
