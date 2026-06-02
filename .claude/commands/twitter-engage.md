# /twitter-engage

Run the full Twitter/X engagement workflow for Ananda.

## What this does

Fetches today's tweets from all monitored accounts, reads each tweet (and views any images visually), writes a comment in Ananda's voice for every tweet, rebuilds the dashboard, and opens it in the browser.

## Steps — run these in order

**Step 1 — Fetch tweets**

```
cd "Twitter Engagement" && node scripts/fetch-tweets.js
```

If it errors with "APIFY_TOKEN not found", check that `Twitter Engagement/.env` exists with `APIFY_TOKEN=<token>`.

**Step 2 — Write comments**

1. Read `Twitter Engagement/data/tweets.json` — note every tweet ID and the full tweet text
2. For every tweet that has `imageUrls`:
   - Run `mkdir -p /tmp/tweet-images`
   - Download each image: `curl -L -o /tmp/tweet-images/<filename> <url>`
   - View the image visually before writing the comment
3. Read `Twitter Engagement/.claude/skills/comment-voice.md` — this is the voice bible, follow it exactly
4. Write a comment for every single tweet
5. Edit `Twitter Engagement/scripts/write-comments.js` — fill the COMMENTS map with every tweet ID and its comment
6. Run: `cd "Twitter Engagement" && node scripts/write-comments.js`

**Step 3 — Build and open dashboard**

```
cd "Twitter Engagement" && node scripts/generate-dashboard.js && node scripts/serve-dashboard.js
```

This opens the dashboard at http://localhost:3000. Every card has a Copy button and an "Open Tweet ↗" button that auto-copies the comment and opens the tweet.

## Done

Tell the user how many tweets were found and how many comments were written. Remind them to go through the dashboard, click "Open Tweet ↗" on each card, and paste the comment into Twitter.
