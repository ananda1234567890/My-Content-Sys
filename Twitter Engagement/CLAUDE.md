# Twitter Engagement System — Ananda

## What This Is

A daily Twitter/X engagement workflow. It fetches the latest tweets from a curated list of accounts, Claude writes comments in Ananda's authentic voice, then a dashboard lets you copy each comment and paste it directly into Twitter.

**The pipeline:**
```
Fetch tweets → Claude writes comments → View dashboard → Copy → Paste in Twitter
```

There is NO automatic posting. You copy and paste manually. Full control.

---

## Quick Commands

Tell Claude Code any of these:

| What you say | What happens |
|---|---|
| `fetch tweets` | Pulls today's tweets from all accounts in accounts.json |
| `write comments` | Claude reads every tweet and writes a comment in Ananda's voice |
| `open dashboard` | Generates the HTML dashboard and opens it in browser |
| `fetch and write` | Does all three steps in sequence |

**First time setup:** See `INSTALL.md` — it has one prompt to paste that handles everything automatically.

---

## Setup Workflow (first time only)

When asked to "set up" or "install":
1. Run `node --version` — if it fails, install Node.js via `winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements`, then verify again
2. Run `npm install`
3. Check if `.env` exists — if not, ask Ananda for his Apify token and create `.env` with `APIFY_TOKEN=<token>`
4. Run `node scripts/fetch-tweets.js` to verify the connection works
5. If successful, run `node scripts/generate-dashboard.js` then `node scripts/serve-dashboard.js`
6. Confirm setup is complete and remind him of the 3 daily commands

---

## Daily Workflow

**Each day, run this in order:**

1. **"fetch tweets"** — Claude runs `node scripts/fetch-tweets.js` then `node scripts/generate-dashboard.js`
2. **"write comments"** — Claude reads `data/tweets.json`, then for every tweet with images it downloads and views the images before writing. It writes comments using the voice guide at `.claude/skills/comment-voice.md`, hardcodes them into `scripts/write-comments.js`, runs the script, then regenerates the dashboard.
3. **"open dashboard"** — Claude runs `node scripts/serve-dashboard.js` which opens the dashboard in your browser at `http://localhost:3000`

Then go through the dashboard, click "Open Tweet ↗" on each card (it auto-copies the comment), and paste it in Twitter.

---

## Voice Guide

Claude writes comments by following `.claude/skills/comment-voice.md`. This file defines exactly how Ananda writes — his rhythm, his slang, his thought structure, and what to never do. Claude reads this before writing every comment.

**Never edit the write-comments.js COMMENTS map by hand** — let Claude write all comments. It needs to see the tweet (and any images) to write well.

---

## File Structure

```
Twitter Engagement/
├── CLAUDE.md                    ← This file
├── README.md                    ← Setup guide
├── accounts.json                ← Twitter accounts to monitor
├── .env                         ← Your API credentials (never share this)
├── .env.example                 ← Template showing what goes in .env
├── package.json
├── .claude/
│   └── skills/
│       └── comment-voice.md    ← Ananda's comment voice guide
├── scripts/
│   ├── fetch-tweets.js         ← Fetches tweets via Apify
│   ├── write-comments.js       ← Stamps comments onto tweets.json
│   ├── generate-dashboard.js   ← Builds the HTML dashboard
│   └── serve-dashboard.js      ← Serves dashboard at localhost:3000
├── data/
│   └── tweets.json             ← All fetched tweets + comments
└── dashboard/
    └── index.html              ← Generated dashboard (don't edit manually)
```

---

## accounts.json

This is the list of Twitter accounts Claude monitors each day. Add or remove usernames freely — just usernames, no @ symbol.

---

## Troubleshooting

**"APIFY_TOKEN not found"** — Make sure you created `.env` (not just `.env.example`) and put your token in it.

**"0 tweets"** — The account may not have posted today or yesterday. That's normal. It'll show up when they post.

**Dashboard shows old tweets** — Run "fetch tweets" again. It overwrites the previous data.

**Comment is empty** — A tweet was fetched after comments were written. Say "write comments" again and Claude will fill in the missing ones.

---

## API Credentials You Need

| Service | What it's for | Cost |
|---|---|---|
| Apify | Fetching tweets without a Twitter API key | Free tier available (~$5/mo for heavy use) |

You do NOT need a Twitter API key. Apify handles all the scraping.
