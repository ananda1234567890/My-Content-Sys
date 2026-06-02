# Twitter Engagement System

A daily automation for engaging on Twitter in your own voice — powered by Claude Code.

---

## What it does

Every day, you run three commands and get a dashboard with tweets from your target accounts + a ready-to-paste comment written in your exact voice. You copy, you paste, you engage.

**No auto-posting. Full manual control.**

---

## One-time setup

### Step 1 — Install Node.js
Go to https://nodejs.org and install the LTS version.

### Step 2 — Install dependencies
Open a terminal in this folder and run:
```
npm install
```

### Step 3 — Get your Apify token
1. Go to https://apify.com and create a free account
2. Go to Settings → Integrations
3. Copy your API token

### Step 4 — Create your .env file
In this folder, create a file called `.env` (no extension) with this content:
```
APIFY_TOKEN=paste_your_token_here
```

### Step 5 — Open this folder in Claude Code
Open the Claude Code app, open this folder as your project, and you're ready.

---

## Daily usage

Just type these into Claude Code:

1. **"fetch tweets"** — gets today's tweets from all accounts
2. **"write comments"** — Claude writes comments in your voice
3. **"open dashboard"** — opens the dashboard in your browser

In the dashboard, click **"Open Tweet ↗"** on each card — it auto-copies the comment and opens the tweet in a new tab. Just paste and post.

---

## Add or remove accounts

Edit `accounts.json` — add Twitter usernames you want to engage with. One username per line, no @ symbol.

---

## Your API costs

| Service | Cost |
|---|---|
| Apify | Free tier covers ~100 accounts/day. Paid plan ~$5/mo for more |
| Claude Code | Your existing subscription |

---

## Troubleshooting

**"APIFY_TOKEN not found"** — Check that your `.env` file exists and has the token in it.

**"0 tweets"** — That account hasn't posted today or yesterday. Normal.

**Comment is empty on dashboard** — Say "write comments" again so Claude fills in the missing ones.
