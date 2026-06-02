# Infographic Prompt Generator — Process Guide

Before generating any infographic image, Claude must follow this process to write the image prompt. Do NOT skip to generation. The prompt quality determines the image quality.

---

## Step 1: Identify the Content Type

Read the post and classify it as ONE of:

- **Tutorial/Steps** — clear sequence (Step 1, 2, 3...) → vertical or horizontal step-flow layout
- **Data/Stats** — numbers, percentages, comparisons, benchmarks → charts, stat callouts, comparison tables
- **Tips/Concepts** — tools or techniques without strict sequence → icon grids or tip cards
- **Comparison** — two workflows, tools, or approaches → side-by-side or pros/cons layout

## Step 2: Research Supporting Data

Use WebSearch to find real data around the post's core topic:

- Real industry statistics — export benchmarks, adoption rates, survey results
- Tool-specific facts — version numbers, feature names, known performance data (Premiere Pro, DaVinci Resolve, After Effects, CapCut, Final Cut Pro, etc.)
- Real-world context — how professionals actually use the workflow being described
- Credible comparisons — published benchmarks or user data

Prioritize: Puget Systems benchmarks, Adobe blogs, DaVinci Resolve release notes, Statista, YouTube Creator reports, Motion Array industry surveys, reputable tech publications.

Use research to find the strongest 3-5 data points worth visualizing. If the post already has solid data, verify and supplement it.

## Step 3: Extract the Visual Core

Combine post content + research findings. Identify:

- Exact steps with labels (if tutorial)
- The strongest 3-5 data points to visualize (if data-driven)
- Key tool names, outcomes, or terms that should appear as text
- The ONE main takeaway the infographic should land on — the headline

## Step 4: Write the Image Prompt

Use this exact format:

```
Create a [TYPE: step-by-step / data / comparison / tips] infographic about [TOPIC] for video editors. Use the uploaded brand style guide for all design decisions including colors, fonts, layout style, and visual tone.

Headline: [PUNCHY HEADLINE — short, specific, impactful]

[If tutorial: List each step with a one-line description. Include relevant icons or visual metaphors per step.]

[If data: Specify each stat, what it represents, and how to visualize it — bar chart, number callout, pie chart, etc. Include source label in small text beneath each stat.]

[If comparison: Define Column A and Column B with their labels and comparison points.]

[If tips: List each tip with a short label and a suggested icon or visual.]

Design notes: Clean, modern layout. Video editing context — use visual metaphors like timelines, play buttons, film strips, cursor icons, or editing UI elements where relevant. All text must be legible at social media dimensions. Single infographic, not a carousel. Portrait (4:5) format.
```

## Rules — NON-NEGOTIABLE

- **ONE prompt per post.** If multiple angles exist, pick the one with the strongest visual potential.
- **Never describe colors or fonts.** The brand guide (passed as input_urls) handles all of that.
- **Keep all extracted text short.** Labels and numbers, not sentences.
- **Do not fabricate statistics.** If research turns up nothing concrete, use tutorial or tips format instead.
- **Always reference the brand guide** in the prompt so Kie.ai applies it.
- **Prioritize real researched data** over vague claims.
- **The image must assist the post** — it reinforces the main argument, not decorates it.

## Step 5: Save and Generate

Save the final prompt to `post.md` under `## Image Notes` → `**Prompt:**`

Then run:
```bash
python3 scripts/generate-infographic.py --post posts/NNN-slug/
```
