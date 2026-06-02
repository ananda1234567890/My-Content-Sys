# Installation Guide

## Step 1 — Open this folder in Claude Code

Open the Claude Code app on your PC. Open this `Twitter Engagement` folder as your project.

---

## Step 2 — Paste this prompt into Claude Code

Copy the entire block below and paste it. Claude Code will handle everything — including installing Node.js if you don't have it. It will only stop to ask you for your Apify token.

---

```
Set up my Twitter Engagement system. Do all of this in order:

1. Check if Node.js is installed by running `node --version`.
   - If it works, continue to step 2.
   - If it fails, install Node.js automatically using: `winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements`
   - After installing, close and reopen the terminal, then verify with `node --version` before continuing.

2. Run `npm install` to install all project dependencies.

3. Check if a `.env` file already exists in this folder.
   - If it doesn't exist, ask me for my Apify API token, then create the `.env` file with exactly this content:
     APIFY_TOKEN=<the token I give you>
   - If it already exists, skip this step.

4. Run `node scripts/fetch-tweets.js` to test the connection. If it fails, tell me the exact error message.

5. If the fetch worked, run `node scripts/generate-dashboard.js` then `node scripts/serve-dashboard.js` to open my dashboard.

6. Confirm setup is complete and remind me of the 3 daily commands:
   - "fetch tweets"
   - "write comments"
   - "open dashboard"
```

---

## Where to get your Apify token

1. Go to **https://apify.com** and create a free account
2. Click your profile photo → **Settings** → **Integrations**
3. Copy the **Personal API token**

Paste it when Claude Code asks.

---

## You're done

After setup, every day just open Claude Code in this folder and say:

1. **"fetch tweets"**
2. **"write comments"**
3. **"open dashboard"**

Claude handles everything. You copy comments from the dashboard and paste them directly into Twitter.

---

## Note on dependencies

`npm install` covers all required packages (`@anthropic-ai/sdk` and `dotenv`). There's nothing else to install manually — no Playwright, no additional tools. Apify handles all the tweet fetching via its API.
