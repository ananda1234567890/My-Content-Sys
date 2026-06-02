# /install

Set up the entire workspace on a new machine. Run this once when opening the project for the first time.

---

## What this does

Installs all dependencies, creates all `.env` files with the user's API keys, and verifies that each system works. Takes 2–3 minutes total.

---

## Step 1 — Check runtime dependencies

**Node.js:**
Run `node --version`.
- If it works (shows a version), continue.
- If it fails:
  - On Mac: run `brew install node` (if Homebrew is installed) or tell the user to download Node.js from https://nodejs.org and install the LTS version, then restart the terminal.
  - On Windows: run `winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements`
  - After install, run `node --version` again to confirm before continuing.

**Python 3:**
Run `python3 --version`.
- If it fails, try `python --version`.
- If neither works, tell the user to install Python 3 from https://python.org.

---

## Step 2 — Install Python packages

```
pip3 install -r requirements.txt
```

If `pip3` fails, try `pip install -r requirements.txt`.

---

## Step 3 — Install Node.js packages

Run both of these:

```
cd "Twitter Engagement" && npm install && cd ..
```

```
cd "LinkedIn Engagement" && npm install && cd ..
```

---

## Step 4 — Gather API keys

Ask the user for each key one at a time. Tell them exactly where to find each one.

**Apify token** (required for both engagement systems and Instagram scraping):
> "I need your Apify API token. Go to https://apify.com → sign in → top-right profile → Settings → Integrations → copy the Personal API token."

**Kie.ai API key** (required for generating images and carousels):
> "I need your Kie.ai API key. Go to https://kie.ai → sign in → API section → copy your key."

**OpenRouter API key** (required for Instagram video analysis):
> "I need your OpenRouter API key. Go to https://openrouter.ai/keys → sign in → create a key → copy it."

---

## Step 5 — Create .env files

Create three `.env` files using the keys collected above.

**Main workspace `.env`** (at the root, next to CLAUDE.md):
```
# Apify — social media scraping (LinkedIn, Instagram, YouTube, Twitter)
APIFY_API_KEY=<apify token>

# Kie.ai — image generation
KIE_AI_API_KEY=<kie.ai key>

# OpenRouter — LLM routing (Gemini, etc.)
OPENROUTER_API_KEY=<openrouter key>
```

**Twitter Engagement `.env`** (inside `Twitter Engagement/`):
```
APIFY_TOKEN=<apify token>
```

**LinkedIn Engagement `.env`** (inside `LinkedIn Engagement/`):
```
APIFY_TOKEN=<apify token>
```

Note: The main workspace uses `APIFY_API_KEY`. The engagement systems use `APIFY_TOKEN`. Same token value, different variable names. Write both exactly as shown.

---

## Step 6 — Verify everything works

Run these checks in order. If any fail, show the exact error and stop.

**Twitter fetch test:**
```
cd "Twitter Engagement" && node scripts/fetch-tweets.js && cd ..
```

**LinkedIn fetch test:**
```
cd "LinkedIn Engagement" && node scripts/fetch-posts.js && cd ..
```

**Python import test:**
```
python3 -c "import requests; from PIL import Image; print('Python packages OK')"
```

---

## Step 7 — Confirm setup complete

Tell the user:

"Setup complete. Here's how to use the workspace:

**Daily engagement:**
- `/linkedin-engage` — fetch LinkedIn posts, write comments, open dashboard
- `/twitter-engage` — fetch tweets, write comments, open dashboard

**Content creation:**
- `/prime` — load full context at the start of every session
- `/create-10-posts` — generate 10 LinkedIn posts with visuals

**To add LinkedIn accounts to monitor:** edit `LinkedIn Engagement/accounts.json` — add full profile URLs like `https://www.linkedin.com/in/username/`
**To add Twitter accounts to monitor:** edit `Twitter Engagement/accounts.json` — add usernames only, no @ symbol"
