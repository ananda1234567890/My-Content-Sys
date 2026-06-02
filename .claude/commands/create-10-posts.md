# Batch Content Generation

Generate a batch of LinkedIn posts in two distinct phases:
**Phase 1 — Ideation:** Scrape Instagram accounts, analyze videos, extract ideas, present for approval.
**Phase 2 — Creation:** Only begins after the user confirms the ideas.

Never skip to Phase 2 automatically. Always wait for explicit approval.

---

## Where Ideas Come From

All ideas come from analyzing real Instagram videos from video editing creators. No trend surfing. No pain point guessing. Every post is grounded in something a real creator is actually teaching right now.

The accounts to scrape live in `context/instagram-accounts.json`. Add handles there before running.

---

## Content Mix

Every post MUST have a visual. No text-only posts. No personal photo posts.

| Format | Share | Description |
|--------|-------|-------------|
| AI Infographic | ~60% | Kie.ai generated, 1080x1350, infographic brand guide as reference |
| Carousel | ~40% | Kie.ai generated slides, 1:1, carousel brand guide as reference |

For 10 posts: 6 infographics + 4 carousels.
For 5 posts: 3 infographics + 2 carousels.
Scale proportionally for other counts.

---

## PHASE 1: Ideation

### Step 1 — Run the scraper

```bash
python3 scripts/scrape-instagram-ideas.py
```

This will:
- Scrape 20 reels from each account in `context/instagram-accounts.json`
- Randomly sample 5 per account
- Send each video to Gemini 3.1 Flash-Lite via OpenRouter
- Extract: core idea, category, tool name, process steps, key insight
- Flag: "comment X for guide" cases and first-person personal claims
- Translate any Hindi or non-English videos to English
- Save raw ideas to `outputs/YYYY-MM-DD-instagram-ideas.json`
- Print a clean idea summary

### Step 2 — Read the raw ideas file

After the script finishes, read:
```
outputs/YYYY-MM-DD-instagram-ideas.json
```

Review each idea:
- Is the core idea specific enough to build a post around?
- Assign format: step-by-step processes → Carousel, data/comparisons/tool verdicts → Infographic

### Step 3 — Present ideas for approval

```
Here are the [N] ideas extracted from Instagram. Approve to start creating, or tell me what to swap.

| # | Account | Core Idea | Format | Flags |
|---|---------|-----------|--------|-------|
| 1 | @handle | ... | Infographic | — |
| 2 | @handle | ... | Carousel | ⚠️ comment-for-guide |
...

Ready to create all [N]? Or swap anything first?
```

**STOP HERE. Wait for the user to respond before doing anything else.**

---

## PHASE 2: Creation

Only begin after explicit approval. Execute posts in order.

**Determine post numbers:**
- Check existing `posts/` folders for highest NNN
- Start new posts at NNN+1

### For EVERY post — Step 1: Research first

Before writing anything, go back to the extracted idea and research it deeply:

- Use WebSearch to find real data, stats, tool documentation, studies backing the idea
- **"Comment X for guide" flag**: research the actual topic from scratch — find the real substance yourself, do not reference the original CTA
- **"Personal claims" flag**: reframe all "I did X / I experienced Y" statements as factual craft knowledge — never attribute personal experience to Ananda unless it's genuinely his

Only after research is done, write the post.

### Writing — MANDATORY: use the LinkedIn Post Writer skill

Read `.claude/skills/linkedin-post-writer/SKILL.md` before writing any post.

The post is ALWAYS written first. The graphic is designed after, to deepen and fuel the post.

**For each post, follow this order:**

#### Step A: Write the post text
1. Read the idea's full JSON schema from `outputs/YYYY-MM-DD-instagram-ideas.json`
2. Apply the LinkedIn Post Writer skill:
   - Pick the post type (Type 1 / 2 / 3) based on `category` and `process_steps`
   - Select the hook using Hook Selection Logic
   - Use `pain_point` for the emotional entry point
   - Use `stats_mentioned` as the lead number if present
   - Use `visual_elements` as context for what the graphic should show
   - Handle any `personal_claims` by reframing, never attributing
3. Save `posts/NNN-slug/post.md`

---

### REVIEW GATE — STOP AFTER ALL POST TEXTS ARE WRITTEN

Write ALL post texts first. Do NOT generate any graphics until this review is approved.

Once all posts are written, present them like this:

```
Here are all [N] posts. Review each one before I generate the graphics.

---
POST 1 — [slug] ([format])
[full post text]

---
POST 2 — [slug] ([format])
[full post text]

...

Which posts need changes? Or say "looks good" to start generating graphics for all of them.
```

**STOP HERE. Do not proceed to Step B until the user explicitly approves.**

If the user requests changes on any post: rewrite those posts, re-present the updated versions, and wait for approval again. Only move to Step B when the user says go.

---

#### Step B: Design the graphic (after post review is approved)
The graphic's job is to add depth the post text doesn't have room for, or to hook someone into reading the caption. It is NOT decoration.

**Follow `.claude/skills/post-to-visual/SKILL.md` for the full process — both formats.**

**CRITICAL: Re-decide the format now. Ignore the format field in post.md.**

The format was assigned during ideation before the post existed. Now that the post is written, apply Step 2: Format Decision from `.claude/skills/post-to-visual/SKILL.md` to the finished post text. Use the rules:

- Type 1 (Step-by-Step Tutorial) → almost always Carousel. Each step deserves its own slide.
- Type 2 (Guide/Breakdown) with 4+ distinct sections → Carousel if each section warrants a slide; Infographic if they form one cohesive reference frame.
- Type 3 (Conversational) → default Infographic unless the content is sequential and needs multiple slides to land.

If your format decision differs from what's in post.md, update the Format field in post.md before proceeding.

**For Infographic posts:**
1. Re-read the finished post text and run the 4-question analysis (anchor claim, gap, save layer, trust builder)
2. Identify the layout type (comparison / step-flow / icon grid / data chart / labeled diagram)
3. Write the Kie.ai prompt describing CONTENT not style — sections, labels, visual elements tied to specific concepts, layout
4. Save prompt to `post.md` under `## Image Notes`
5. Run: `python3 scripts/generate-infographic.py --post posts/NNN-slug/`

**For Carousel posts:**
1. Re-read the finished post text and run the 4-question analysis
2. Write slides: heading / subtitle / takeaway / visual per slide
   - The `visual` field must describe a specific scene or UI element that represents the concept — not atmosphere
   - See the good vs bad visual prompt examples in the post-to-visual skill
3. Save `posts/NNN-slug/content.json`
4. Run: `python3 scripts/generate-carousel-kieai.py --json posts/NNN-slug/content.json --output posts/NNN-slug/carousel.pdf`
5. Write 2-4 line companion text for the post (hook to make them swipe, ends with "Swipe through." or "Save this.") and add it to `post.md`

### Finalize
1. Run `python3 scripts/build-dashboard.py`
2. Verify every post has a visual
3. Report: list all posts with number, topic, format
4. Open dashboard: `open outputs/dashboard.html`

---

## Post Storage Format

```
posts/NNN-slug/
  post.md           # Metadata + copy-paste ready text
  image.png         # For infographic posts
  carousel.pdf      # For carousel posts
  carousel-slides/  # Slide PNGs (auto-generated)
  content.json      # Carousel source JSON
```

### post.md Template
```markdown
# [Post Title]

**Date created:** YYYY-MM-DD
**Source:** @instagram_handle — [reel URL]
**Format:** [AI Infographic / Carousel]
**Platform:** LinkedIn
**Status:** Ready to publish

## Post Text (copy-paste ready)

[Post text here]

## Image Notes

[Kie.ai prompt used, or carousel content.json summary]
```

---

## Quality Rules

- Follow the LinkedIn Post Writer skill — see `.claude/skills/linkedin-post-writer/SKILL.md`
- Post is written BEFORE the graphic. The graphic deepens the post, not the other way around.
- No em dashes anywhere in copy
- No personal story as the main hook
- No first-person claims that aren't Ananda's real experience
- Every post must have a specific number, tool name, or data point
- No generic hooks ("Here are 5 things...", "Most people don't know...")
- No banned phrases from the skill file
- Carousels: one idea per slide, every slide has a `visual` field describing a specific scene not generic atmosphere
- Infographics: prompt describes CONTENT (sections, labels, visual elements) not style — style comes from reference image
- Both formats follow `.claude/skills/post-to-visual/SKILL.md`
- All content in English — source videos translated if needed
