---
name: content-ideation
description: Generate content ideas for LinkedIn posts by scraping and analyzing Instagram video editing accounts. Ideas come from real videos — hacks, tools, techniques being taught by creators right now. Use when asked to "generate ideas", "find topics", "brainstorm content", or before running create-10-posts.
---

# Content Ideation — Instagram Video Analysis

All ideas come from watching real Instagram videos from video editing creators. The pipeline:

1. Scrape reels from accounts in `context/instagram-accounts.json`
2. Randomly sample 5 per account
3. Gemini watches each video and extracts the core idea
4. Present clean idea list for approval

---

## Running the Pipeline

```bash
python3 scripts/scrape-instagram-ideas.py
```

Options:
```bash
# Override accounts list
python3 scripts/scrape-instagram-ideas.py --accounts peter_mckinnon gradientfilms

# Change scrape volume and sample size
python3 scripts/scrape-instagram-ideas.py --per-account 20 --sample 5
```

---

## Managing the Accounts List

Accounts live in `context/instagram-accounts.json`:

```json
{
  "accounts": ["handle1", "handle2", "handle3"]
}
```

Target accounts that post video editing tricks, hacks, workflows, AI tools, or YouTube growth techniques. Posts in English or Hindi (Hindi is auto-translated).

---

## What the Script Extracts Per Video

For each video, Gemini returns:

| Field | Description |
|-------|-------------|
| `core_idea` | The main hack/trick/tool being shown |
| `category` | tool / technique / workflow / algorithm / ai-feature |
| `tool_name` | Specific software mentioned (Premiere, CapCut, DaVinci, etc.) |
| `process_steps` | Step-by-step breakdown of what's demonstrated |
| `key_insight` | Single most valuable takeaway for a video editor |
| `post_angle` | Suggested LinkedIn angle |
| `post_title` | Suggested headline |
| `cta_flag` | Whether creator gates content behind "comment X" |
| `personal_claims` | Any first-person claims that need reframing |

---

## Flags to Watch

**`comment_for_guide`** — Creator asks viewers to comment to receive a resource.
→ Do not try to get the guide. Research the topic yourself using WebSearch during Phase 2.

**`personal_claims`** — Creator says "I did X" or "I experienced Y".
→ Reframe as factual craft knowledge during writing. Never attribute personal experience to Ananda unless it's genuinely his.

**Non-English video** — Script auto-translates Hindi and other languages to English.

---

## Presenting Ideas for Approval

After the script runs, read `outputs/YYYY-MM-DD-instagram-ideas.json` and present:

```
| # | Account | Core Idea | Format | Flags |
|---|---------|-----------|--------|-------|
| 1 | @handle | ... | Infographic | — |
| 2 | @handle | ... | Carousel | ⚠️ comment-for-guide |
```

Format assignment guide:
- Step-by-step processes, workflows → **Carousel**
- Data, tool comparisons, verdicts, stats → **Infographic**

Wait for user approval before moving to Phase 2.
