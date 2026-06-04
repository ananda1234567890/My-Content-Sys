#!/usr/bin/env python3
"""
Scrape Instagram video editing accounts, analyze videos with Gemini, extract post ideas.

All Apify scrape jobs are submitted simultaneously and polled in parallel.
All Gemini video analyses are also submitted simultaneously via threads.

Phase 1 of the create-10-posts pipeline.

Usage:
    python3 scripts/scrape-instagram-ideas.py
    python3 scripts/scrape-instagram-ideas.py --accounts peter_mckinnon gradientfilms
    python3 scripts/scrape-instagram-ideas.py --per-account 20 --sample 5
"""

import os
import sys
import json
import random
import base64
import time
import argparse
import re
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APIFY_ACTOR = "xMc5Ga1oCONPmWJIa"

VIDEO_ANALYSIS_PROMPT = """You are analyzing an Instagram reel from a video editing creator.

Watch the entire video carefully. Extract the following in JSON format:

{
  "language": "English or Hindi or other",
  "core_idea": "One sentence — what is the main hack, trick, tool, or technique being shown?",
  "category": "tool | technique | workflow | algorithm | ai-feature | other",
  "tool_name": "Name of specific tool/software if mentioned, else null",
  "process_steps": ["Step 1", "Step 2", "Step 3"],
  "key_insight": "The single most valuable thing a video editor would take away from this",
  "pain_point": "What frustration or problem does this solve for an editor? Write it as the emotion an editor would feel — e.g. 'Tired of vertical exports looking zoomed in and cropped?' This is the hook entry point.",
  "visual_elements": ["What did the viewer see on screen beyond a talking head? List specific UI panels, before/after comparisons, timeline views, settings menus, color grade changes, etc. shown in the video."],
  "stats_mentioned": ["Any specific numbers, percentages, time saved, file sizes, frame rates, or quantitative claims mentioned in the video. If none, empty array."],
  "is_business_content": true or false,
  "cta_flag": "comment_for_guide | none — does the creator ask viewers to comment to get a resource?",
  "cta_detail": "What they're offering if cta_flag is comment_for_guide, else null",
  "personal_claims": ["List any 'I did X' or 'I experienced Y' first-person claims that need to be reframed as facts"],
  "post_angle": "Suggested LinkedIn post angle — how would this help a YouTuber or video editor?",
  "post_title": "Suggested LinkedIn post headline (short, punchy, specific)"
}

Important rules:
- If the video is in Hindi or any non-English language, translate everything to English in your response
- Extract the actual substance — not just surface description. What would an editor actually DO after watching this?
- If the creator says "comment X to get the guide/template/resource", flag it and describe what they're offering
- Be specific with tool names, steps, numbers
- For pain_point: write it as a frustrated editor's inner monologue, not a description
- For visual_elements: be specific about what software UI, panel, or visual comparison was shown
- For stats_mentioned: only include numbers actually said or shown in the video — don't infer
- For is_business_content: set to true ONLY if the video is primarily about getting clients, finding freelance work, pricing editing services, cold outreach, pitching to clients, or making money as a freelance editor. Set to false for everything else — editing techniques, tools, software features, workflow improvements, storytelling, YouTube growth, content strategy, AI tools, typography, career development through craft, or becoming a better editor. The test is simple: is the main value "how to get paid as an editor"? If yes, true. If the main value is anything about the craft of editing itself, false.
- Return ONLY valid JSON, no other text"""


def read_env():
    env = {}
    env_path = os.path.join(WORKSPACE_ROOT, '.env')
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def start_scrape_job(username, results_limit, apify_key):
    resp = requests.post(
        f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/runs",
        headers={"Authorization": f"Bearer {apify_key}", "Content-Type": "application/json"},
        json={"username": [username], "resultsLimit": results_limit}
    )
    if resp.status_code not in (200, 201):
        raise ValueError(f"Apify start failed for @{username}: {resp.status_code} {resp.text[:200]}")
    run_id = resp.json()["data"]["id"]
    print(f"  ✓ @{username} — job started ({run_id[:12]}...)")
    return run_id


def poll_scrape_job(username, run_id, apify_key, timeout=300):
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(8)
        r = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}",
            params={"token": apify_key}
        )
        status = r.json()["data"]["status"]
        if status == "SUCCEEDED":
            items = requests.get(
                f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items",
                params={"token": apify_key}
            ).json()
            print(f"  ✓ @{username} — {len(items)} reels scraped")
            return username, items
        elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise ValueError(f"Apify run failed for @{username}: {status}")
    raise TimeoutError(f"Apify timed out for @{username}")


def extract_video_url(item):
    for field in ["videoUrl", "video_url", "videoPlayUrl", "playUrl", "url"]:
        if item.get(field):
            return item[field]
    if item.get("childPosts"):
        for child in item["childPosts"]:
            url = extract_video_url(child)
            if url:
                return url
    return None


def download_video_base64(url):
    r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    content_type = r.headers.get("content-type", "video/mp4").split(";")[0].strip()
    b64 = base64.b64encode(r.content).decode("utf-8")
    size_mb = len(r.content) / (1024 * 1024)
    return b64, content_type, size_mb


def analyze_video(username, reel, openrouter_key):
    video_url = extract_video_url(reel)
    reel_id = reel.get("id", reel.get("shortCode", "unknown"))
    b64, content_type, size_mb = download_video_base64(video_url)
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"},
        json={
            "model": "google/gemini-3.1-flash-lite",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": VIDEO_ANALYSIS_PROMPT},
                    {"type": "video_url", "video_url": {"url": f"data:{content_type};base64,{b64}"}}
                ]
            }]
        },
        timeout=120
    )
    if resp.status_code != 200:
        raise ValueError(f"OpenRouter error {resp.status_code}: {resp.text[:200]}")
    raw = resp.json()["choices"][0]["message"]["content"]
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse JSON: {raw[:200]}")
    analysis = json.loads(match.group())
    analysis["account"] = username
    analysis["reel_id"] = reel_id
    analysis["reel_url"] = f"https://www.instagram.com/reel/{reel.get('shortCode', reel_id)}/"
    analysis["video_url"] = video_url
    analysis["size_mb"] = round(size_mb, 1)
    return analysis


def generate_html(ideas, out_path):
    rows = ""
    for i, idea in enumerate(ideas):
        flags_html = ""
        if idea.get("cta_flag") == "comment_for_guide":
            flags_html += '<span class="flag flag-guide">⚠ guide</span> '
        if idea.get("personal_claims"):
            flags_html += '<span class="flag flag-claims">⚠ claims</span>'

        tool = idea.get("tool_name") or ""
        tool_html = f'<span class="tag tag-tool">{tool}</span>' if tool else ""
        cat = idea.get("category") or ""
        cat_html = f'<span class="tag tag-cat">{cat}</span>' if cat else ""
        reel_url = idea.get("reel_url", "#")
        account = idea.get("account", "")
        title = idea.get("post_title") or idea.get("core_idea", "")
        description = idea.get("core_idea", "")
        pain_point = idea.get("pain_point") or ""
        pain_html = f'<div class="pain-point">{pain_point}</div>' if pain_point else ""
        stats = idea.get("stats_mentioned") or []
        stats_html = "".join(f'<span class="tag tag-stat">{s}</span>' for s in stats[:3])

        rows += f"""
        <tr class="row" id="row-{i}" onclick="toggle({i})">
          <td class="td-check">
            <label class="checkbox-wrap" onclick="event.stopPropagation()">
              <input type="checkbox" class="idea-check" id="cb-{i}" data-index="{i}" onchange="updateCount(); highlightRow({i})">
              <span class="checkmark"></span>
            </label>
          </td>
          <td class="td-num">{i+1}</td>
          <td class="td-account"><a href="{reel_url}" target="_blank" class="acct-link" onclick="event.stopPropagation()">@{account}</a></td>
          <td class="td-title">{title}{pain_html}</td>
          <td class="td-desc">{description}</td>
          <td class="td-meta">{cat_html}{tool_html}{stats_html}{flags_html}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Instagram Ideas — {len(ideas)} extracted</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0D0B16; color: #E2E0FF; font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif; font-size: 14px; line-height: 1.5; }}
  .header {{ background: #13111F; border-bottom: 1px solid #2A2640; padding: 18px 36px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 100; }}
  .header h1 {{ font-size: 16px; font-weight: 600; color: #fff; }}
  .header h1 span {{ color: #A78BFA; }}
  .counter {{ background: #1E1A36; border: 1px solid #3D3568; border-radius: 6px; padding: 6px 14px; font-size: 13px; color: #A78BFA; font-weight: 500; }}
  .counter strong {{ color: #fff; }}
  .wrap {{ padding: 24px 36px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{ text-align: left; padding: 10px 12px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.7px; color: #6B6B8A; font-weight: 600; border-bottom: 1px solid #2A2640; white-space: nowrap; }}
  .row {{ cursor: pointer; border-bottom: 1px solid #1A1830; transition: background 0.1s; }}
  .row:hover {{ background: #15122A; }}
  .row.selected {{ background: #160F2A; }}
  .row.selected td {{ border-bottom-color: #2A1A5A; }}
  td {{ padding: 11px 12px; vertical-align: middle; }}
  .td-check {{ width: 36px; }}
  .td-num {{ width: 32px; color: #4A4870; font-size: 12px; font-weight: 500; }}
  .td-account {{ width: 130px; white-space: nowrap; }}
  .acct-link {{ color: #A78BFA; font-weight: 600; font-size: 13px; text-decoration: none; }}
  .acct-link:hover {{ color: #C4B5FD; text-decoration: underline; }}
  .td-title {{ font-weight: 600; color: #fff; font-size: 13px; line-height: 1.4; min-width: 200px; }}
  .td-desc {{ color: #9CA3C8; font-size: 13px; line-height: 1.4; }}
  .td-meta {{ white-space: nowrap; }}
  .tag {{ display: inline-block; border-radius: 4px; padding: 2px 7px; font-size: 11px; margin-right: 4px; }}
  .tag-cat {{ background: #1E1A36; color: #9CA3C8; text-transform: uppercase; letter-spacing: 0.4px; }}
  .tag-tool {{ background: #1A1530; color: #60A5FA; }}
  .flag {{ display: inline-block; border-radius: 4px; padding: 2px 7px; font-size: 11px; margin-right: 4px; }}
  .flag-guide {{ background: #2D1B00; color: #FBBF24; }}
  .flag-claims {{ background: #1A0D2E; color: #C084FC; }}
  .tag-stat {{ background: #0F2A1A; color: #34D399; }}
  .pain-point {{ margin-top: 4px; font-size: 11px; color: #7C6FAA; font-style: italic; font-weight: 400; line-height: 1.3; }}
  .checkbox-wrap {{ position: relative; display: inline-block; width: 18px; height: 18px; }}
  .checkbox-wrap input {{ opacity: 0; width: 0; height: 0; position: absolute; }}
  .checkmark {{ position: absolute; inset: 0; background: #1E1A36; border: 2px solid #3D3568; border-radius: 4px; cursor: pointer; transition: all 0.15s; }}
  .checkbox-wrap input:checked ~ .checkmark {{ background: #7C3AED; border-color: #7C3AED; }}
  .checkbox-wrap input:checked ~ .checkmark::after {{ content: ''; position: absolute; left: 4px; top: 1px; width: 6px; height: 10px; border: 2px solid white; border-top: none; border-left: none; transform: rotate(45deg); }}
  .footer {{ position: fixed; bottom: 0; left: 0; right: 0; background: #13111F; border-top: 1px solid #2A2640; padding: 14px 36px; display: flex; align-items: center; gap: 16px; z-index: 100; }}
  .footer-label {{ font-size: 12px; color: #6B6B8A; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; white-space: nowrap; }}
  #selected-nums {{ flex: 1; background: #0D0B16; border: 1px solid #3D3568; border-radius: 6px; padding: 8px 14px; font-size: 14px; color: #E2E0FF; font-family: inherit; outline: none; cursor: text; min-height: 36px; letter-spacing: 0.3px; }}
  .copy-btn {{ background: #7C3AED; color: #fff; border: none; border-radius: 6px; padding: 8px 18px; font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap; transition: background 0.15s; }}
  .copy-btn:hover {{ background: #6D28D9; }}
  .copy-btn.copied {{ background: #16A34A; }}
  body {{ padding-bottom: 70px; }}
</style>
</head>
<body>
<div class="header">
  <h1>Instagram Ideas — <span>{len(ideas)} extracted</span></h1>
  <div class="counter">Selected: <strong id="count">0</strong> / {len(ideas)}</div>
</div>
<div class="wrap">
<table>
  <thead>
    <tr>
      <th></th>
      <th>#</th>
      <th>Account</th>
      <th>Title</th>
      <th>What it's about</th>
      <th>Category / Tool / Flags</th>
    </tr>
  </thead>
  <tbody>
{rows}
  </tbody>
</table>
</div>
<div class="footer">
  <span class="footer-label">Selected #s</span>
  <div id="selected-nums" readonly style="user-select:all;"></div>
  <button class="copy-btn" id="copy-btn" onclick="copyNums()">Copy</button>
</div>
<script>
function toggle(i) {{
  const cb = document.getElementById('cb-' + i);
  cb.checked = !cb.checked;
  updateCount();
  highlightRow(i);
}}
function highlightRow(i) {{
  const row = document.getElementById('row-' + i);
  const cb = document.getElementById('cb-' + i);
  row.classList.toggle('selected', cb.checked);
}}
function updateCount() {{
  const checked = document.querySelectorAll('.idea-check:checked').length;
  document.getElementById('count').textContent = checked;
  const nums = Array.from(document.querySelectorAll('.idea-check:checked'))
    .map(cb => cb.dataset.index)
    .map(i => parseInt(i) + 1)
    .sort((a, b) => a - b)
    .join(', ');
  document.getElementById('selected-nums').textContent = nums || '—';
}}
function copyNums() {{
  const text = document.getElementById('selected-nums').textContent;
  if (!text || text === '—') return;
  navigator.clipboard.writeText(text).then(() => {{
    const btn = document.getElementById('copy-btn');
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = 'Copy'; btn.classList.remove('copied'); }}, 1500);
  }});
}}
</script>
</body>
</html>"""

    with open(out_path, "w") as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--accounts", nargs="+", help="Instagram handles (without @)")
    parser.add_argument("--per-account", type=int, default=20, help="Reels to scrape per account")
    parser.add_argument("--sample", type=int, default=5, help="Reels to randomly sample per account")
    args = parser.parse_args()

    env = read_env()
    apify_key = env.get("APIFY_API_KEY")
    openrouter_key = env.get("OPENROUTER_API_KEY")
    if not apify_key or apify_key == "YOUR_KEY":
        raise ValueError("APIFY_API_KEY not set in .env")
    if not openrouter_key:
        raise ValueError("OPENROUTER_API_KEY not set in .env")

    if args.accounts:
        accounts = args.accounts
    else:
        accounts_file = os.path.join(WORKSPACE_ROOT, "context", "instagram-accounts.json")
        with open(accounts_file) as f:
            data = json.load(f)
        accounts = data.get("accounts", [])
        if not accounts:
            raise ValueError("No accounts found. Add handles to context/instagram-accounts.json or use --accounts")

    print(f"\nScraping {len(accounts)} accounts in parallel ({args.per_account} reels each, sampling {args.sample})...\n")

    # Step 1 — Submit all Apify jobs simultaneously
    print("Submitting all scrape jobs...")
    run_ids = {}
    for username in accounts:
        try:
            run_id = start_scrape_job(username, args.per_account, apify_key)
            run_ids[username] = run_id
        except Exception as e:
            print(f"  ERROR starting @{username}: {e}")

    if not run_ids:
        print("No scrape jobs started.")
        return

    # Step 2 — Poll all jobs in parallel
    print(f"\nPolling {len(run_ids)} jobs in parallel...")
    account_reels = {}
    with ThreadPoolExecutor(max_workers=len(run_ids)) as executor:
        futures = {
            executor.submit(poll_scrape_job, username, run_id, apify_key): username
            for username, run_id in run_ids.items()
        }
        for future in as_completed(futures):
            username = futures[future]
            try:
                username, reels = future.result()
                account_reels[username] = reels
            except Exception as e:
                print(f"  ERROR polling @{username}: {e}")

    # Step 3 — Sample videos from each account
    videos_to_analyze = []
    for username, reels in account_reels.items():
        reels_with_video = [r for r in reels if extract_video_url(r)]
        if not reels_with_video:
            print(f"  No downloadable video URLs for @{username}")
            continue
        sample_size = min(args.sample, len(reels_with_video))
        sampled = random.sample(reels_with_video, sample_size)
        print(f"  @{username} — sampled {sample_size} of {len(reels_with_video)} reels")
        for reel in sampled:
            videos_to_analyze.append((username, reel))

    if not videos_to_analyze:
        print("\nNo videos to analyze.")
        return

    # Step 4 — Analyze all videos in parallel with Gemini
    print(f"\nAnalyzing {len(videos_to_analyze)} videos with Gemini in parallel...\n")
    all_ideas = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(analyze_video, username, reel, openrouter_key): (username, reel)
            for username, reel in videos_to_analyze
        }
        for future in as_completed(futures):
            username, reel = futures[future]
            reel_id = reel.get("id", reel.get("shortCode", "?"))
            try:
                analysis = future.result()
                all_ideas.append(analysis)
                print(f"  ✓ @{username} [{reel_id[:12]}] — {analysis.get('core_idea', '')[:70]}")
            except Exception as e:
                print(f"  ERROR @{username} [{reel_id[:12]}]: {e}")

    if not all_ideas:
        print("\nNo ideas extracted.")
        return

    # Step 4.5 — Filter out business/client-acquisition content
    before_filter = len(all_ideas)
    filtered_out = [i for i in all_ideas if i.get("is_business_content") is True]
    all_ideas = [i for i in all_ideas if i.get("is_business_content") is not True]
    if filtered_out:
        print(f"\n  Filtered out {len(filtered_out)} business/client-acquisition reel(s):")
        for f in filtered_out:
            print(f"    — [@{f.get('account')}] {f.get('post_title', f.get('core_idea', '?'))}")
    print(f"  {len(all_ideas)} craft ideas remaining.\n")

    if not all_ideas:
        print("All ideas were filtered out (business content). Try different accounts or reels.")
        return

    # Step 5 — Save and display
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join(WORKSPACE_ROOT, "outputs", f"{date_str}-instagram-ideas.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(all_ideas, f, indent=2)

    print(f"\n{'='*60}")
    print(f"EXTRACTED {len(all_ideas)} IDEAS")
    print(f"{'='*60}\n")

    for i, idea in enumerate(all_ideas, 1):
        flags = []
        if idea.get("cta_flag") == "comment_for_guide":
            flags.append("⚠️ comment-for-guide")
        if idea.get("personal_claims"):
            flags.append("⚠️ personal claims")
        flag_str = "  " + " | ".join(flags) if flags else ""

        steps = idea.get("process_steps") or []
        steps_str = ""
        if steps:
            steps_str = "\n    Steps: " + " → ".join(steps[:4])
            if len(steps) > 4:
                steps_str += f" (+{len(steps)-4} more)"

        print(f"{'─'*60}")
        print(f"{i:2}. [@{idea.get('account')}] {idea.get('post_title', '?')}{flag_str}")
        print(f"    Category: {idea.get('category')} | Tool: {idea.get('tool_name') or 'none'}")
        print(f"    What it's about: {idea.get('core_idea', '')}")
        print(f"    Key insight: {idea.get('key_insight', '')}")
        if steps_str:
            print(steps_str)
        print(f"    LinkedIn angle: {idea.get('post_angle', '')}")
        print()

    print(f"{'─'*60}")
    print(f"\nSaved to: outputs/{date_str}-instagram-ideas.json")

    # Rebuild consolidated ideas dashboard (all batches in one page)
    build_dashboard_script = os.path.join(WORKSPACE_ROOT, "scripts", "build-ideas-dashboard.py")
    dashboard_path = os.path.join(WORKSPACE_ROOT, "outputs", "ideas-dashboard.html")
    import subprocess
    result = subprocess.run(["python3", build_dashboard_script], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"\nIdeas dashboard updated: {dashboard_path}")
        if result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                print(f"  {line}")
    else:
        print(f"\nWarning: dashboard rebuild failed: {result.stderr[:200]}")

    os.system(f"open '{dashboard_path}'")


if __name__ == "__main__":
    main()
