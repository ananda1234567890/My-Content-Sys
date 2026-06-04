# CLAUDE.md

## FIRST TIME ON THIS MACHINE?

If `node_modules` folders don't exist inside `Twitter Engagement/` or `LinkedIn Engagement/`, or if `.env` files are missing — this is a fresh install. Run `/install` immediately and Claude will set up everything automatically. Do not try to use any other commands until `/install` is complete.

**Claude: if you detect missing `node_modules` or missing `.env` files on session start, proactively tell the user to run `/install` before doing anything else.**

---

## Quick Access

- **Content Dashboard:** `open outputs/dashboard.html`

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What This Is

This is a **Content Creation Workspace** — a structured environment for creating, planning, and managing social media content across LinkedIn, YouTube, Instagram, and Twitter. Claude operates as a content creation partner, helping draft posts, ideate topics, repurpose content across platforms, and maintain a consistent brand voice.

**This file (CLAUDE.md) is the foundation.** It is automatically loaded at the start of every session. Keep it current — it is the single source of truth for how Claude should understand and operate within this workspace.

---

## Who You Are

- **Name:** Ananda Paramanick
- **Age:** 24
- **Location:** Kolkata, India
- **Title:** Professional Video Editor — YouTube Growth & Retention Specialist
- **Background:** 3 years as a professional video editor. Went from ₹3000/month to $4000+/month freelancing. Deep expertise in YouTube retention editing, growth mechanics, and AI-powered video workflows. Generated 5M+ organic views for clients.
- **Mission:** Build authority as the go-to editor for YouTube growth by sharing craft knowledge and industry insights — not personal story.

### Social Profiles

- LinkedIn: https://www.linkedin.com/in/anandaparamanick/
- Twitter/X: https://x.com/OnlyAnanda_
- YouTube: TBD — add manually
- Instagram: TBD — add manually

---

## The Claude-User Relationship

Claude operates as a **content creation partner** with access to the workspace folders, context files, commands, and outputs. The relationship is:

- **You**: Set content direction, provide raw ideas/context, approve final content
- **Claude**: Draft content, suggest ideas, adapt posts across platforms, maintain voice consistency, and organize the content workflow

Claude should always orient itself through `/prime` at session start, then act with full awareness of your brand, voice, audience, and strategic goals.

### Voice & Tone Guidelines

All posts are written using the **LinkedIn Post Writer skill** at `.claude/skills/linkedin-post-writer/SKILL.md`. That file is the single source of truth for voice, formatting, post types, hooks, and banned words.

Key principles:
- **Craft-first** — every post leads with a technique, insight, or industry development — NOT personal story
- **Mouth-first** — reads like someone talking, not like someone writing. If it doesn't sound like something a real person said out loud, rewrite it.
- **Specific and technical** — real tool names, real numbers, real techniques
- **Three post types** — Step-by-Step Tutorial, Guide/Breakdown, Conversational. Each has a defined hook formula and body structure.
- **No em dashes anywhere** — hard rule, no exceptions
- **No motivational sign-offs** — no "Keep creating!", no hustle framing
- **No corporate speak** — see banned words list in the skill file

---

## Workspace Structure

```
.
├── CLAUDE.md              # This file — core context, always loaded
├── .claude/
│   ├── commands/          # Slash commands: /init, /prime, /create-10-posts, /create-plan, /implement
│   └── skills/            # Skills: linkedin-post-writer, viral-replication, content-ideation, carousel-creation
├── .env                   # API keys (Apify, Kie.ai) — NOT committed
├── context/               # Everything about you
│   ├── profile.md         #   Who you are (name, links, voice, personality)
│   ├── business.md        #   What you do (company, product, audience)
│   ├── strategy.md        #   Where you're going (goals, priorities)
│   ├── metrics.md         #   Current numbers (followers, engagement)
│   ├── images/            #   Personal photos for posts
│   └── data/              #   Scraped social data (LinkedIn, YouTube)
├── posts/                 # Final content — one folder per post (NNN-slug/)
├── outputs/               # Working files, dashboards, drafts
├── reference/             # Style guides, visual refs, copywriting examples
├── scripts/               # Automation (dashboard builder, carousel generator)
└── plans/                 # Implementation plans
```

**Key directories:**

| Directory    | Purpose                                                                |
| ------------ | ---------------------------------------------------------------------- |
| `context/`   | **All info about you** — profile, business, strategy, metrics, photos, scraped data. Read by `/prime`. |
| `posts/`     | **Final content** — one folder per post with image + text + originals. |
| `reference/` | Visual style refs, copywriting style guide, post examples.             |
| `outputs/`   | Working files, dashboards, drafts, idea banks, research.               |
| `scripts/`   | Dashboard builder, carousel generator, automation scripts.             |
| `plans/`     | Content plans and implementation plans. Created by `/create-plan`.     |

---

## Commands

### /install

**Purpose:** First-time setup on a new machine. Run this once after cloning the repo.

Installs Node.js packages in both engagement systems, installs Python packages, creates all `.env` files by asking for API keys, and verifies everything works. Nothing else will work until this is done.

### /init [URLs and/or text]

**Purpose:** Build the entire workspace context from scratch.

Takes any combination of URLs (LinkedIn, YouTube, Instagram, Twitter, website) and free-form text. Scrapes all sources via Apify, analyzes everything, and generates all context files + updates this CLAUDE.md.

Example: `/init https://www.linkedin.com/in/username/ https://www.youtube.com/@Channel They run a B2B SaaS for recruiters`

### /prime

**Purpose:** Initialize a new session with full context awareness.

Run this at the start of every session. Claude will read all context files and confirm readiness.

### /create-10-posts

**Purpose:** Generate 10 ready-to-publish LinkedIn posts in a single run.

Produces a diverse content batch:
- **By method:** 5 viral replication + 3 trend surfing + 2 pain points
- **By format:** 6 AI infographics + 4 carousels — NO personal photo posts
- **Every post has a visual** — no text-only posts
- All posts are self-sufficient (no "comment X for free resource" CTAs)
- Enforces diversity of topics, hooks, visuals, and tone across the batch

### /create-plan [request]

**Purpose:** Create a detailed implementation plan before making changes.

Example: `/create-plan weekly LinkedIn content series on personal branding mistakes`

### /implement [plan-path]

**Purpose:** Execute a plan created by /create-plan.

Example: `/implement plans/2026-03-05-linkedin-series.md`

### /linkedin-engage

**Purpose:** Run the full LinkedIn engagement workflow.

Fetches latest posts from all profiles in `LinkedIn Engagement/accounts.json`, reads each post and any images, writes a comment in Ananda's voice for every post, and opens the dashboard at http://localhost:3001.

Natural language triggers: "engage on LinkedIn", "do LinkedIn engagement", "LinkedIn comments", "fetch LinkedIn posts"

### /twitter-engage

**Purpose:** Run the full Twitter/X engagement workflow.

Fetches today's tweets from all accounts in `Twitter Engagement/accounts.json`, reads each tweet and any images, writes a comment in Ananda's voice for every tweet, and opens the dashboard at http://localhost:3000.

Natural language triggers: "engage on Twitter", "do Twitter engagement", "Twitter comments", "fetch tweets"

### /setup-buffer

**Purpose:** First-time setup of Buffer + Cloudinary integration on a new machine.

Asks for Buffer API token, Cloudinary API Key, and Cloudinary API Secret. Writes them to root `.env`, auto-fetches the LinkedIn channel ID, and confirms everything works with a test post.

Run this once after cloning. After it's done, the `/schedule-post` command works.

Natural language triggers: "setup buffer", "connect buffer", "configure buffer"

### /schedule-post [post-folder] [time]

**Purpose:** Schedule a LinkedIn post to Buffer so it publishes automatically.

Reads the post text from `posts/NNN-slug/post.md` and schedules it to LinkedIn via the Buffer API.

**When told to schedule a post:**
1. Identify the post folder from the post number or name (e.g., "post 017" → `posts/017-ai-transition-bridging`)
2. Parse the requested time and convert to IST (Asia/Kolkata, UTC+5:30)
3. Run: `python3 scripts/schedule-to-buffer.py posts/NNN-slug --time "YYYY-MM-DDTHH:MM:SS+05:30"`
4. Confirm the post ID and scheduled time back to the user

**Modes:**
- `--time "2026-06-09T09:00:00+05:30"` — schedule at a specific date and time (IST)
- `--queue` — add to Buffer queue (next available slot in posting schedule)
- No flag — defaults to 9am IST tomorrow

**Requires:** `BUFFER_TOKEN` and `BUFFER_LINKEDIN_CHANNEL_ID` in root `.env`

Natural language triggers: "schedule post", "queue this post", "post on June 9th", "add to Buffer"

---

## Engagement Systems

Two separate engagement systems live as subdirectories. Each has its own accounts list, scripts, and dashboard.

| System | Folder | Dashboard | Accounts file |
|---|---|---|---|
| LinkedIn | `LinkedIn Engagement/` | http://localhost:3001 | `LinkedIn Engagement/accounts.json` — full profile URLs |
| Twitter/X | `Twitter Engagement/` | http://localhost:3000 | `Twitter Engagement/accounts.json` — usernames only |

Both need `APIFY_TOKEN` in their own `.env` file. The token is the same for both — copy from your Apify dashboard.

---

## Content Platforms & Approach

> **Edit this table to match your platforms and focus areas.**

| Platform   | Audience                          | Content Focus                                           |
| ---------- | --------------------------------- | ------------------------------------------------------- |
| LinkedIn   | Creators, YouTubers, marketers, video editors | Video editing techniques, YouTube growth, AI tools in editing, industry news |
| Twitter/X  | Creators, editors, freelancers, builders | Quick tips, editing tricks, industry takes, networking |

---

## Critical Instruction: Maintain This File

**Whenever Claude makes changes to the workspace, Claude MUST consider whether CLAUDE.md needs updating.**

After any change — adding commands, scripts, workflows, or modifying structure — ask:

1. Does this change add new functionality users need to know about?
2. Does it modify the workspace structure documented above?
3. Should a new command be listed?
4. Does context/ need new files to capture this?

If yes to any, update the relevant sections. This file must always reflect the current state of the workspace so future sessions have accurate context.

---

## Content Creation Workflow: Instagram Video Analysis

All post ideas come from watching real Instagram videos from video editing creators. No trend guessing — every post is grounded in something a real creator is actually teaching.

The full process is documented in `.claude/commands/create-10-posts.md`. In summary:

**Phase 1 — Ideation:**
1. **Scrape** — `python3 scripts/scrape-instagram-ideas.py` pulls 20 reels per account from `context/instagram-accounts.json`, randomly samples 5 per account
2. **Analyze** — Gemini 3.1 Flash-Lite watches each video, extracts the core idea, flags "comment-for-guide" CTAs and personal claims, translates Hindi to English
3. **Approve** — Claude presents the idea list, user approves before anything is written

**Phase 2 — Creation:**
4. **Research** — WebSearch for real data backing each idea; "comment-for-guide" cases researched from scratch
5. **Reframe** — First-person creator claims ("I did X") converted to factual craft knowledge
6. **Write** — Post text + infographic or carousel prompt
7. **Generate** — Kie.ai image or carousel PDF
8. **Save** to `posts/NNN-slug/` folder with all assets
9. **Rebuild dashboard** — run `python3 scripts/build-dashboard.py`

### Visual Style

**Two content formats only — no personal photo posts.**

**Infographics** — reference file: `reference/infographic-ref-style.png`
- Dark background (#1A1630 / #0D0B1A)
- Purple accent palette: #6B3DF6 (primary), #8A5CFF, #B694FF (highlights)
- White body text, bold white headlines
- Inter / Manrope / Satoshi font family
- Data-driven: use real stats, bar charts, donut charts, timelines, progress bars
- Line icons with consistent stroke, rounded corners
- Layout: Header/title → Main visual/chart → Supporting info → Footer (optional)
- Vibe: Modern, Technical, Clean, Bold, Professional

**Carousels** — generated via Kie.ai (same API as infographics). Reference file: `reference/carousel-ref-style.png`
- Deep dark background (#0D0B16)
- Purple accents: #7C3AED (primary), #4C1D95 (deep), #A78BFA (highlight)
- Bold white headlines (60–100px), supporting statement in purple (24–36px)
- Inter / Helvetica Neue / Satoshi font family
- Cinematic, atmospheric imagery (movement, depth, solitude, mood)
- One idea per slide, high contrast, minimal text
- 8pt grid, 40–60px margins, safe area respected

### Image Generation — MANDATORY approach

**Always use Kie.ai API (model: `gpt-image-2-image-to-image`) with `input_urls` parameter.**
- Pass the Cloudinary URL as `input_urls: [url]` — Kie.ai fetches it directly, no base64 needed
- **Infographics:** `https://res.cloudinary.com/duoq5xmdp/image/upload/v1779533849/Infographic_Guide_g2ins5.png`
- **Carousels:** `https://res.cloudinary.com/duoq5xmdp/image/upload/v1779533851/Brand_Carousel_Guide_dz6mz3.png`
- Carousels are always **1:1 (1080x1080)**. Infographics are **4:5 (1080x1350)**.
- Never generate with Pillow alone — results are flat and template-like
- Never use light backgrounds, cream palettes, or off-brand colors
- Check existing posts before creating — vary layouts across consecutive posts

See `.claude/skills/viral-replication/SKILL.md` for full API code and prompt templates.

### Content Ideation

Generate content ideas using three complementary methods. Ask for any number of ideas — they split evenly across:

1. **Viral Replication Ideas** — find proven viral posts and propose replicating their packaging
2. **Trend Surfing Ideas** — find what's trending RIGHT NOW and create timely content
3. **Audience Pain Point Ideas** — think deeply about your audience's problems and create content that solves them

Full process documented in `.claude/skills/content-ideation/SKILL.md`. Output saves to `outputs/YYYY-MM-DD-content-ideas.md`.

### Carousel Creation

LinkedIn carousels are PDF documents uploaded as posts. Each slide is a cinematic AI-generated image via Kie.ai.

1. **Write content** — title + 5-9 numbered points, each with heading, subtitle, takeaway
2. **Create JSON** — must use `slides` key with objects containing `number`, `heading`, `subtitle`, `takeaway`
3. **Generate PDF** — `python3 scripts/generate-carousel-kieai.py --json content.json --output posts/NNN-slug/carousel.pdf`
   - Uses `reference/carousel-ref-style.png` as style reference (cinematic dark purple)
   - Submits all slides to Kie.ai in parallel, then polls for results
   - Auto-stitches slides into PDF
4. **Save** to `posts/NNN-slug/` with carousel.pdf + post.md
5. **Slide PNGs** are auto-saved to `carousel-slides/` subfolder for dashboard preview

### Copywriting Style

All posts use the **LinkedIn Post Writer skill** — see `.claude/skills/linkedin-post-writer/SKILL.md`.

Three post types (Step-by-Step Tutorial, Guide/Breakdown, Conversational), each with defined hook formulas, body formats, and closing structures. Key rules: mouth-first voice, no em dashes, specific numbers, exact tool names, no banned words.

---

## Post Storage Convention

Each post lives in `posts/NNN-slug/` where NNN is a zero-padded number:

```
posts/001-example-post/
├── post.md              # Metadata + copy-paste ready text
├── image.png            # Final image (personal photo or AI infographic)
├── carousel.pdf         # Carousel PDF (for carousel posts)
├── carousel-slides/     # Auto-generated slide PNGs (for dashboard preview)
├── content.json         # Carousel content JSON (for carousel posts)
├── original.md          # Original viral post reference
└── original-image.jpg   # Original image for comparison
```

**Every post MUST have a visual** — either `image.png` (photo/infographic) or `carousel.pdf` + `carousel-slides/`. No text-only posts.

After adding/updating posts, run `python3 scripts/build-dashboard.py` to regenerate the HTML dashboard at `outputs/dashboard.html`.

---

## Session Workflow

1. **Start**: Run `/prime` to load context
2. **Work**: Ask Claude to draft content, brainstorm ideas, or refine posts
3. **Plan changes**: Use `/create-plan` for content campaigns or workspace changes
4. **Execute**: Use `/implement` to execute plans
5. **Maintain**: Claude updates CLAUDE.md and context/ as the workspace evolves

---

## Tools & APIs

| Tool | Purpose | Config |
| ---- | ------- | ------ |
| **Apify** | Instagram reel scraping. Actor: `xMc5Ga1oCONPmWJIa`. Input: `{username: [...], resultsLimit: 20}` | `APIFY_API_KEY` in `.env` |
| **OpenRouter** | LLM routing for video analysis. Model: `google/gemini-3.1-flash-lite`. Passes video as base64 `video_url`. API: `openrouter.ai/api/v1/chat/completions` | `OPENROUTER_API_KEY` in `.env` |
| **Kie.ai** | Image generation. Model: `gpt-image-2-image-to-image`. Uses `input_urls` with Cloudinary reference URLs. API: POST `api.kie.ai/api/v1/jobs/createTask`, poll `api.kie.ai/api/v1/jobs/recordInfo?taskId=`. Infographics: 1080x1350. Carousels: 1080x1080. Resolution: 1K. | `KIE_AI_API_KEY` in `.env` |
| **Buffer** | LinkedIn post scheduling. GraphQL API at `https://api.buffer.com`. Script: `scripts/schedule-to-buffer.py`. Full setup in `Buffer Setup Guide.md`. | `BUFFER_TOKEN` + `BUFFER_LINKEDIN_CHANNEL_ID` in root `.env` |

### Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/scrape-instagram-ideas.py` | Phase 1: scrape Instagram → analyze with Gemini → extract ideas |
| `scripts/generate-infographic.py` | Generate infographic via Kie.ai from post.md prompt |
| `scripts/generate-carousel-kieai.py` | Generate carousel PDF via Kie.ai from content.json |
| `scripts/build-dashboard.py` | Rebuild HTML dashboard at outputs/dashboard.html |
| `scripts/test-video-analysis.py` | Test Gemini video analysis on a single URL |

---

## Notes

- Keep context minimal but sufficient — avoid bloat
- Plans live in `plans/` with dated filenames for history
- Outputs are organized by platform/type in `outputs/`
- Reference materials go in `reference/` for reuse
- Content should always reflect your authentic voice — never generic or corporate
- `context/data/` contains scraped social media data — re-scrape periodically to keep current
