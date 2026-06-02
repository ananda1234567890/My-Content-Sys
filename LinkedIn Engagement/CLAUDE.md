# LinkedIn Engagement System — Ananda

## What This Is

A daily LinkedIn engagement workflow. It fetches the latest posts from a curated list of profiles, Claude writes comments in Ananda's authentic voice, then a dashboard lets you copy each comment and paste it directly into LinkedIn.

**The pipeline:**
```
Fetch posts → Claude writes comments → View dashboard → Copy → Paste in LinkedIn
```

There is NO automatic posting. You copy and paste manually. Full control.

---

## Quick Commands

Tell Claude Code any of these:

| What you say | What happens |
|---|---|
| `fetch posts` | Pulls today's posts from all profiles in accounts.json |
| `write comments` | Claude reads every post (and views any images) then writes a comment in Ananda's voice |
| `open dashboard` | Generates the HTML dashboard and opens it in browser |
| `fetch and write` | Does all three steps in sequence |

---

## Setup (first time only)

1. Run `node --version` — if it fails, install Node.js
2. Run `npm install`
3. Check if `.env` exists — if not, create it with `APIFY_TOKEN=<your token>`
4. Run `node scripts/fetch-posts.js` to verify the connection works
5. Run `node scripts/generate-dashboard.js` then `node scripts/serve-dashboard.js`

---

## Daily Workflow

**Each day, run this in order:**

1. **"fetch posts"** — Claude runs `node scripts/fetch-posts.js` then `node scripts/generate-dashboard.js`
2. **"write comments"** — Claude reads `data/posts.json`. For every post with images, Claude downloads them to `/tmp/linkedin-images/` and reads them visually before writing. It writes comments using the voice guide at `.claude/skills/comment-voice.md`, hardcodes them into `scripts/write-comments.js`, runs the script, then regenerates the dashboard.
3. **"open dashboard"** — Claude runs `node scripts/serve-dashboard.js` which opens the dashboard in your browser at `http://localhost:3001`

Then go through the dashboard, click "Open Post ↗" on each card (it auto-copies the comment), and paste it in LinkedIn.

---

## Writing Comments — Claude's Exact Process

When told "write comments":

1. Read `data/posts.json`
2. For each post that has `imageUrls`:
   - Download each image to `/tmp/linkedin-images/` using `curl -L -o /tmp/linkedin-images/<filename> <url>`
   - Read the image visually before writing the comment
3. Read `.claude/skills/comment-voice.md` — this is the single source of truth for voice
4. Write a comment for every post following the voice guide exactly
5. Edit `scripts/write-comments.js` — fill the COMMENTS map with `{ postId: 'comment text' }` entries
6. Run `node scripts/write-comments.js`
7. Run `node scripts/generate-dashboard.js`
8. Confirm how many comments were written

**Never edit the COMMENTS map by hand** — let Claude write all comments. It needs to see the post (and any images) to write well.

---

## Voice Guide

Claude writes comments by following `.claude/skills/comment-voice.md`. This file defines exactly how Ananda writes on LinkedIn — his rhythm, his perspective, his thought structure, and what to never do.

Key principles from the voice guide:
- Craft-first — brings everything back to video editing, YouTube retention, or creator work when it fits naturally
- No em dashes, no hashtags, no validation openers
- 15-60 words max per comment
- One thought per line where it lands better
- Picks ONE mode per comment (pushback, add what they missed, honest admit, etc.)

---

## accounts.json

This is the list of LinkedIn profile URLs Claude monitors each day. Add or remove freely — full profile URLs like `https://www.linkedin.com/in/username/`.

The Apify actor used is `supreme_coder/linkedin-post`. It takes `profileUrls` as input and returns the most recent posts.

---

## File Structure

```
LinkedIn Engagement/
├── CLAUDE.md                    ← This file
├── accounts.json                ← LinkedIn profiles to monitor
├── .env                         ← Your API credentials (never share this)
├── .env.example                 ← Template showing what goes in .env
├── package.json
├── .claude/
│   └── skills/
│       └── comment-voice.md    ← Ananda's LinkedIn comment voice guide
├── scripts/
│   ├── fetch-posts.js          ← Fetches LinkedIn posts via Apify
│   ├── write-comments.js       ← Stamps comments onto posts.json
│   ├── generate-dashboard.js   ← Builds the HTML dashboard
│   └── serve-dashboard.js      ← Serves dashboard at localhost:3001
├── data/
│   └── posts.json              ← All fetched posts + comments
└── dashboard/
    └── index.html              ← Generated dashboard (don't edit manually)
```

---

## Troubleshooting

**"APIFY_TOKEN not found"** — Make sure you created `.env` (not just `.env.example`) and put your token in it.

**"0 posts"** — The profile may not have posted recently, or the actor couldn't reach it. Try again later.

**Dashboard shows old posts** — Run "fetch posts" again. It overwrites the previous data.

**Comment is empty** — A post was fetched after comments were written. Say "write comments" again and Claude will fill in the missing ones.

**Port 3001 in use** — The server auto-kills and restarts on the same port. If it hangs, run `lsof -ti tcp:3001 | xargs kill -9` manually.

---

## API Credentials You Need

| Service | What it's for | Cost |
|---|---|---|
| Apify | Fetching LinkedIn posts without a LinkedIn API key | Free tier available |

You do NOT need a LinkedIn API key. Apify handles all the scraping.
