# Post to Visual Skill

**Purpose:** Take a finished LinkedIn post and produce either an infographic or carousel that deepens it. The graphic is not a restatement of the post. It adds the layer the post didn't have room for.

**Input:** A finished post text.
**Output:** Either a generated `image.png` (infographic) or a generated `carousel.pdf` + companion post text update.

---

## HARD RULES

- **No em dashes anywhere.** Not in prompts, not in slide text, not in labels. Use a comma, a period, or a line break.
- **Never describe style in the prompt.** Colors, fonts, mood, and brand style are handled by the reference image passed to Kie.ai. Your prompt describes CONTENT, not aesthetics.
- **Every visual element must connect to the specific concept.** No "atmospheric dark background" without something concrete attached to it. If you can't describe what the visual represents, it's filler.

---

## Step 1: Post Analysis

Read the finished post. Answer these four questions before touching any design work.

**1. What is the anchor claim?**
The single argument the post makes. One sentence.

**2. What is the gap?**
What does the post mention but not unpack? Named techniques without showing steps. Stats without context. Frameworks referenced but not diagrammed. Examples named but not compared. The gap is what the graphic fills.

**3. What would someone save?**
Is it a reference card? A comparison table? A labeled diagram? A checklist? The format of the save determines the format of the graphic.

**4. What would make the claim more credible?**
Visual evidence. A before/after. A diagram that shows the mechanism. Data that backs the argument. Side-by-side comparison. Something that makes the reader think "oh I can actually see that."

Write these four answers down before moving to Step 2.

---

## Step 2: Format Decision

**Choose infographic when:**
- The gap is a single cohesive visual frame (one diagram, one comparison, one labeled breakdown)
- The save layer is a reference card the reader can come back to
- The post is Type 2 (Guide/Breakdown) with clear sections that map to a visual structure
- The whole argument can be summarized in one image without losing meaning

**Choose carousel when:**
- The post introduces 4+ distinct points each worth going one level deeper on
- The post is Type 1 (Step-by-Step) and each step deserves its own slide treatment
- The content needs to be read sequentially to land (each slide builds on the last)
- The gap requires more space than one image allows

**When it's genuinely ambiguous:** default to infographic. One strong image is harder to get wrong than 6 weak slides.

---

## Step 3: Content Extraction

### For Infographic

**Identify the layout type first.** One of:

- **Comparison** — two approaches, tools, or methods side by side. Use when the post argues one thing beats another.
- **Step-flow** — a numbered sequence of steps as a visual process. Use when the post is tutorial-based with clear sequential steps.
- **Icon grid / Tip cards** — 3-6 distinct techniques or concepts, each with a short label. Use when the post covers multiple independent tips.
- **Data chart** — stat callouts, bar charts, number comparisons. Use when the post is anchored in data and the numbers are the point.
- **Labeled diagram** — a concept shown as a diagram with labels (a model, a framework, a process). Use when the post describes how something works mechanically.

**Extract these for the prompt:**
- Headline (5-7 words max, punchy, no em dash)
- Each section/column/row: label + one key data point or concept (3-5 words each)
- One specific visual metaphor per section that represents its concept
- Bottom callout: the single most important stat or takeaway

### For Carousel

**Decide slide count first.** 6-8 slides is the sweet spot (cover + 5-6 content slides + CTA).

**Per content slide, extract:**
- `heading` — 3-6 words. The point.
- `subtitle` — one sentence. Expands the heading with a specific detail.
- `takeaway` — the thing they should actually do or remember. The most important line.
- `visual` — see Step 4 prompt writing below.

**CTA slide:**
- One of: "Save this.", "Follow Ananda Paramanick for more editing insights.", "Repost to help a creator you know."

---

## Step 4: Write the Kie.ai Prompt

### The core principle

The reference image (passed as `input_urls`) handles ALL style decisions: background color, font family, spacing, overall mood. Your prompt handles ALL content decisions: what sections exist, what text labels appear, what visual elements are present, what the layout looks like.

If your prompt is mostly describing style, you've written the wrong thing.

### Infographic prompt format

```
Create a [LAYOUT TYPE: comparison / step-flow / icon grid / data chart / labeled diagram] infographic for video editors. Use the uploaded brand style guide for all design decisions.

Headline: [PUNCHY HEADLINE — 5-7 words, no em dash]

[SECTION BREAKDOWN — list each section/column/row with its exact label and content]

[DATA POINTS — if data chart, specify exact numbers and what they represent]

[VISUAL ELEMENTS — for each concept, name the specific thing to show: a timeline strip, a waveform, a camera, an editing interface, a retention graph. NOT "dark atmosphere" or "moody lighting"]

Layout: [describe the flow — left to right, top to bottom, numbered flow, two columns, etc.]
```

**Infographic prompt example (camera angles post):**

```
Create a labeled diagram infographic for video editors showing how camera angles control emotional perception. Use the uploaded brand style guide for all design decisions.

Headline: Camera Angle Is an Emotion Instruction

Section 1 — Eye-Level
Label: Neutral. Equal. Relatable.
Visual: A camera at face height facing a subject directly, horizontal sight line

Section 2 — Low-Angle
Label: Power. Dominance. Threat.
Visual: A camera pointing upward at a subject, making them appear larger, tilted perspective

Section 3 — High-Angle
Label: Vulnerable. Small. Defeated.
Visual: A camera pointing downward at a subject, making them appear smaller

Bottom callout: Choose the angle that matches the emotion of the moment, not the one in focus.

Layout: Three vertical panels side by side, each showing the angle diagram with label above and emotional effect below.
```

### Carousel visual prompt format (per slide)

The `visual` field in `content.json` drives the image for that slide. Write it as:

```
[What specific thing is shown] + [what detail makes it concrete] + [one brand anchor]
```

The brand anchor is always: `Deep dark purple background, cinematic mood, purple accent light, high contrast, match the brand guide style.`

**Examples:**

| Slide concept | Bad visual prompt | Good visual prompt |
|---|---|---|
| Eye-level camera angle | Atmospheric silhouette in purple fog | A film camera at eye level facing a subject directly, horizontal sight line visible, studio lighting. Deep dark purple background, cinematic mood, purple accent light, high contrast, match the brand guide style. |
| Retention drop at 40% | Dark moody background | A YouTube analytics screen showing a retention graph sharply declining at the 40% mark, purple glow around the drop. Deep dark purple background, cinematic mood, purple accent light, high contrast, match the brand guide style. |
| B-roll cutting technique | Person in dark atmosphere | A cinema camera on a tripod in a dark studio, raw footage waiting to be cut, purple backlight from behind. Deep dark purple background, cinematic mood, purple accent light, high contrast, match the brand guide style. |
| Audio sync | Abstract purple shapes | Close-up of an audio waveform on an editing timeline, peaks and valleys visible, cursor hovering over a sync point. Deep dark purple background, cinematic mood, purple accent light, high contrast, match the brand guide style. |

**Rule:** If you can't describe what is literally shown in the frame, the visual is not specific enough. A good visual prompt reads like a photography brief, not a mood description.

---

## Step 5: Text Rules for Graphic Content

All text that appears inside the graphic (headings, labels, subtitles, callouts, takeaways) must follow these rules:

- No em dashes
- No filler words (basically, essentially, in order to)
- Labels: 3-5 words max
- Takeaways: one sentence, active voice, starts with a verb
- No banned words from the LinkedIn Post Writer skill
- No stacked 2-3 word fragments. If a callout or takeaway has multiple related ideas, connect them into one flowing sentence with commas or natural connectors. "I had like 0 connections and no mentors, did I mention? no roadmap as well." not "No connections. No mentors. No roadmap."

---

## Step 6: Generate

### Infographic

Save the final prompt to `post.md` under `## Image Notes` then run:

```bash
python3 scripts/generate-infographic.py --post posts/NNN-slug/
```

### Carousel

Save `content.json` with the full slides array then run:

```bash
python3 scripts/generate-carousel-kieai.py --json posts/NNN-slug/content.json --output posts/NNN-slug/carousel.pdf
```

For carousel posts: write a 2-4 line companion caption in `post.md`. Hook that makes them swipe. Ends with "Swipe through." or "Save this." Keep it clean and direct. No em dashes.

---

## Quick Self-Check Before Generating

- Did I read the post before designing anything?
- Does the graphic add a layer the post didn't have room for, or does it just restate the post?
- Is every visual element in the prompt connected to a specific concept?
- Are there any em dashes in the prompt or slide text?
- Does the prompt describe content, not style?
- Is the format decision (carousel vs infographic) based on the rules, not gut feel?
- Would someone save this graphic even if they hadn't read the post?

If any fail, rewrite before generating.
