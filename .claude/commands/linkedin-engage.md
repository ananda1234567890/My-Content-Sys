# /linkedin-engage

Run the full LinkedIn engagement workflow for Ananda.

## What this does

Fetches the latest LinkedIn posts from all monitored accounts, reads each post (and views any images visually), writes a comment in Ananda's voice for every post, rebuilds the dashboard, and opens it in the browser.

## Steps — run these in order

**Step 1 — Fetch posts**

```
cd "LinkedIn Engagement" && node scripts/fetch-posts.js
```

If it errors with "APIFY_TOKEN not found", check that `LinkedIn Engagement/.env` exists with `APIFY_TOKEN=<token>`.

**Apify actor:** `harvestapi~linkedin-profile-posts`. Input: `{ profileUrls: [profileUrl], resultsLimit: 3 }`. For quick testing, pass `--limit N` to only fetch the first N accounts: `node scripts/fetch-posts.js --limit 10`.

**Step 2 — Write comments**

1. Read `LinkedIn Engagement/data/posts.json` — note every post ID and the full post text
2. For every post that has `localImagePaths` (auto-downloaded by fetch-posts.js to `dashboard/images/`):
   - Read each image at its local path visually before writing the comment
3. Read `LinkedIn Engagement/.claude/skills/comment-voice.md` — this is the voice bible, follow it exactly
4. Write a comment for every single post (10–40 words, one thought per line)
5. Edit `LinkedIn Engagement/scripts/write-comments.js` — fill the COMMENTS map with every post ID and its comment
6. Run: `cd "LinkedIn Engagement" && node scripts/write-comments.js`

**Step 3 — Build and open dashboard**

```
cd "LinkedIn Engagement" && node scripts/generate-dashboard.js && node scripts/serve-dashboard.js
```

This opens the dashboard at http://localhost:3001. Every card has a Copy button and an "Open Post ↗" button that auto-copies the comment and opens the LinkedIn post.

## Done

Tell the user how many posts were found and how many comments were written. Remind them to go through the dashboard, click "Open Post ↗" on each card, and paste the comment into LinkedIn.
