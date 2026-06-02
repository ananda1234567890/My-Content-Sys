#!/usr/bin/env python3
"""
Build a consolidated HTML dashboard showing ALL Instagram idea batches.
Reads every outputs/*-instagram-ideas.json file, groups by date, and
renders a tabbed interface where each tab is one scrape run.

Output: outputs/ideas-dashboard.html

Run manually:
    python3 scripts/build-ideas-dashboard.py

Also called automatically at the end of scrape-instagram-ideas.py.
"""

import os
import json
import glob
import re
from datetime import datetime

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(WORKSPACE_ROOT, "outputs")
OUTPUT_PATH = os.path.join(OUTPUTS_DIR, "ideas-dashboard.html")


def load_all_batches():
    """Return list of (date_str, ideas) tuples sorted newest-first."""
    pattern = os.path.join(OUTPUTS_DIR, "*-instagram-ideas.json")
    files = sorted(glob.glob(pattern), reverse=True)
    batches = []
    for fpath in files:
        fname = os.path.basename(fpath)
        # Extract date from filename like 2026-05-28-instagram-ideas.json
        m = re.match(r"^(\d{4}-\d{2}-\d{2})-instagram-ideas\.json$", fname)
        if not m:
            continue
        date_str = m.group(1)
        try:
            with open(fpath) as f:
                ideas = json.load(f)
            if isinstance(ideas, list):
                batches.append((date_str, ideas))
        except Exception as e:
            print(f"  Warning: could not load {fname}: {e}")
    return batches


def format_tab_label(date_str, ideas):
    """Return a human-friendly tab label like 'May 28 – 7 ideas'."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        label = dt.strftime("%b %-d")
    except Exception:
        label = date_str
    count = len(ideas)
    noun = "idea" if count == 1 else "ideas"
    return f"{label} &ndash; {count} {noun}"


def render_idea_cards(ideas, batch_index):
    """Render the idea cards for one batch."""
    if not ideas:
        return '<p class="empty-state">No ideas in this batch.</p>'

    cards_html = []
    for i, idea in enumerate(ideas):
        # Number badge (1-based within this batch)
        num = i + 1

        # Title and account
        title = idea.get("post_title") or idea.get("core_idea") or "Untitled"
        account = idea.get("account") or ""
        reel_url = idea.get("reel_url") or "#"

        # Core idea (description)
        core_idea = idea.get("core_idea") or ""

        # Category
        category = idea.get("category") or ""

        # Pain point as italic subtitle
        pain_point = idea.get("pain_point") or ""

        # Stats as small green tags (up to 4)
        stats = idea.get("stats_mentioned") or []
        stats_html = "".join(
            f'<span class="tag tag-stat">{s}</span>'
            for s in stats[:4]
        )

        # Format suggestion — derive from category / tool hints
        # Carousels suit step-by-step / workflow; infographics suit data / ai-feature / tool / algorithm
        cat = (category or "").lower()
        carousel_cats = {"workflow", "technique"}
        suggested_format = "Carousel" if cat in carousel_cats else "Infographic"
        format_class = "fmt-carousel" if suggested_format == "Carousel" else "fmt-infographic"

        # CTA / claim flags
        flags_html = ""
        if idea.get("cta_flag") == "comment_for_guide":
            flags_html += '<span class="flag flag-guide">guide CTA</span>'
        if idea.get("personal_claims"):
            flags_html += '<span class="flag flag-claims">claims</span>'

        # Tool tag
        tool = idea.get("tool_name") or ""
        tool_html = f'<span class="tag tag-tool">{tool}</span>' if tool else ""

        # Category tag
        cat_html = f'<span class="tag tag-cat">{category}</span>' if category else ""

        pain_html = f'<p class="pain-point">{pain_point}</p>' if pain_point else ""

        card = f"""
        <div class="idea-card" data-batch="{batch_index}" data-num="{num}">
          <div class="card-top">
            <span class="num-badge">{num}</span>
            <div class="card-title-block">
              <p class="card-title">{title}</p>
              {pain_html}
            </div>
            <span class="format-badge {format_class}">{suggested_format}</span>
          </div>
          <p class="card-desc">{core_idea}</p>
          <div class="card-meta">
            <a href="{reel_url}" target="_blank" class="acct-link">@{account}</a>
            {cat_html}{tool_html}{stats_html}{flags_html}
          </div>
        </div>"""
        cards_html.append(card)

    return "\n".join(cards_html)


def build_html(batches):
    """Build the full HTML string."""

    # ---- Tab buttons ----
    tab_buttons_html = ""
    for idx, (date_str, ideas) in enumerate(batches):
        active = " active" if idx == 0 else ""
        label = format_tab_label(date_str, ideas)
        tab_buttons_html += f'<button class="tab-btn{active}" data-tab="{idx}" onclick="switchTab({idx})">{label}</button>\n'

    # ---- Tab panels ----
    tab_panels_html = ""
    for idx, (date_str, ideas) in enumerate(batches):
        hidden = "" if idx == 0 else ' style="display:none"'
        cards = render_idea_cards(ideas, idx)
        tab_panels_html += f'<div class="tab-panel" id="panel-{idx}"{hidden}>\n{cards}\n</div>\n'

    total_ideas = sum(len(ideas) for _, ideas in batches)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Instagram Ideas Dashboard</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: #0D0B16;
    color: #E2E0FF;
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
    font-size: 14px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}

  /* ---- Header ---- */
  .header {{
    background: #13111F;
    border-bottom: 1px solid #2A2640;
    padding: 18px 36px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
  }}
  .header-title {{
    font-size: 15px;
    font-weight: 600;
    color: #fff;
  }}
  .header-title span {{ color: #A78BFA; }}
  .header-meta {{
    font-size: 12px;
    color: #6B6B8A;
  }}

  /* ---- Tabs ---- */
  .tabs-bar {{
    background: #11101C;
    border-bottom: 1px solid #2A2640;
    padding: 0 36px;
    display: flex;
    gap: 4px;
    overflow-x: auto;
    scrollbar-width: none;
  }}
  .tabs-bar::-webkit-scrollbar {{ display: none; }}

  .tab-btn {{
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: #6B6B8A;
    font-size: 13px;
    font-family: inherit;
    font-weight: 500;
    padding: 12px 16px;
    cursor: pointer;
    white-space: nowrap;
    transition: color 0.15s, border-color 0.15s;
    flex-shrink: 0;
  }}
  .tab-btn:hover {{
    color: #C4B5FD;
  }}
  .tab-btn.active {{
    color: #A78BFA;
    border-bottom-color: #7C3AED;
  }}

  /* ---- Content area ---- */
  .content {{
    padding: 28px 36px 100px;
    max-width: 1200px;
  }}

  /* ---- Cards grid ---- */
  .tab-panel {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 14px;
  }}

  .empty-state {{
    color: #4A4870;
    font-size: 14px;
    padding: 40px 0;
    grid-column: 1 / -1;
  }}

  /* ---- Individual idea card ---- */
  .idea-card {{
    background: #13111F;
    border: 1px solid #2A2640;
    border-radius: 10px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    transition: border-color 0.15s, background 0.15s;
  }}
  .idea-card:hover {{
    border-color: #3D3568;
    background: #15122A;
  }}

  .card-top {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
  }}

  .num-badge {{
    flex-shrink: 0;
    width: 26px;
    height: 26px;
    border-radius: 6px;
    background: #1E1A36;
    border: 1px solid #3D3568;
    color: #A78BFA;
    font-size: 12px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 1px;
  }}

  .card-title-block {{
    flex: 1;
    min-width: 0;
  }}

  .card-title {{
    font-size: 13px;
    font-weight: 600;
    color: #fff;
    line-height: 1.4;
  }}

  .pain-point {{
    margin-top: 4px;
    font-size: 11px;
    color: #7C6FAA;
    font-style: italic;
    line-height: 1.35;
  }}

  .format-badge {{
    flex-shrink: 0;
    font-size: 10px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 5px;
    letter-spacing: 0.3px;
    margin-top: 2px;
    text-transform: uppercase;
  }}
  .fmt-infographic {{
    background: #1A1030;
    color: #A78BFA;
    border: 1px solid #3D2A6A;
  }}
  .fmt-carousel {{
    background: #0F2238;
    color: #60A5FA;
    border: 1px solid #1E3A5F;
  }}

  .card-desc {{
    font-size: 12px;
    color: #9CA3C8;
    line-height: 1.5;
  }}

  .card-meta {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 5px;
  }}

  .acct-link {{
    color: #A78BFA;
    font-weight: 600;
    font-size: 12px;
    text-decoration: none;
  }}
  .acct-link:hover {{
    color: #C4B5FD;
    text-decoration: underline;
  }}

  .tag {{
    display: inline-block;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 10px;
    font-weight: 500;
  }}
  .tag-cat {{
    background: #1E1A36;
    color: #9CA3C8;
    text-transform: uppercase;
    letter-spacing: 0.4px;
  }}
  .tag-tool {{
    background: #102030;
    color: #60A5FA;
  }}
  .tag-stat {{
    background: #0A2018;
    color: #34D399;
  }}

  .flag {{
    display: inline-block;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 10px;
    font-weight: 500;
  }}
  .flag-guide {{
    background: #2D1B00;
    color: #FBBF24;
  }}
  .flag-claims {{
    background: #1A0D2E;
    color: #C084FC;
  }}

  /* ---- Footer bar (selection) ---- */
  .footer {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #13111F;
    border-top: 1px solid #2A2640;
    padding: 12px 36px;
    display: flex;
    align-items: center;
    gap: 14px;
    z-index: 100;
  }}
  .footer-label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #6B6B8A;
    white-space: nowrap;
  }}
  #selected-display {{
    flex: 1;
    background: #0D0B16;
    border: 1px solid #3D3568;
    border-radius: 6px;
    padding: 7px 14px;
    font-size: 13px;
    color: #E2E0FF;
    min-height: 34px;
    letter-spacing: 0.3px;
    user-select: all;
  }}
  .clear-btn {{
    background: transparent;
    color: #6B6B8A;
    border: 1px solid #3D3568;
    border-radius: 6px;
    padding: 7px 14px;
    font-size: 12px;
    font-family: inherit;
    font-weight: 500;
    cursor: pointer;
    white-space: nowrap;
    transition: color 0.15s, border-color 0.15s;
  }}
  .clear-btn:hover {{
    color: #E2E0FF;
    border-color: #6B6B8A;
  }}
  .copy-btn {{
    background: #7C3AED;
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 7px 18px;
    font-size: 13px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.15s;
  }}
  .copy-btn:hover {{ background: #6D28D9; }}
  .copy-btn.copied {{ background: #16A34A; }}

  .sel-count {{
    font-size: 12px;
    color: #A78BFA;
    font-weight: 500;
    white-space: nowrap;
  }}
</style>
</head>
<body>

<div class="header">
  <p class="header-title">Instagram Ideas &mdash; <span>{len(batches)} batch{"es" if len(batches) != 1 else ""}</span></p>
  <p class="header-meta">{total_ideas} total ideas across all runs</p>
</div>

<div class="tabs-bar">
{tab_buttons_html}
</div>

<div class="content">
{tab_panels_html}
</div>

<div class="footer">
  <span class="footer-label">Selected #s</span>
  <div id="selected-display">&mdash;</div>
  <span class="sel-count" id="sel-count">0 selected</span>
  <button class="clear-btn" onclick="clearSelection()">Clear</button>
  <button class="copy-btn" id="copy-btn" onclick="copySelection()">Copy</button>
</div>

<script>
  // ---- Tab switching ----
  function switchTab(idx) {{
    document.querySelectorAll('.tab-btn').forEach(function(btn) {{
      btn.classList.toggle('active', parseInt(btn.dataset.tab) === idx);
    }});
    document.querySelectorAll('.tab-panel').forEach(function(panel, i) {{
      panel.style.display = i === idx ? '' : 'none';
    }});
    // Clear selection when switching tabs
    clearSelection();
  }}

  // ---- Card selection ----
  var selected = {{}};  // num -> true, scoped to current tab

  function getActiveTab() {{
    var btn = document.querySelector('.tab-btn.active');
    return btn ? parseInt(btn.dataset.tab) : 0;
  }}

  document.addEventListener('click', function(e) {{
    var card = e.target.closest('.idea-card');
    if (!card) return;
    if (e.target.closest('a')) return;  // don't intercept reel links
    var num = parseInt(card.dataset.num);
    var tab = parseInt(card.dataset.batch);
    if (tab !== getActiveTab()) return;
    if (selected[num]) {{
      delete selected[num];
      card.classList.remove('selected-card');
    }} else {{
      selected[num] = true;
      card.classList.add('selected-card');
    }}
    updateFooter();
  }});

  function clearSelection() {{
    selected = {{}};
    document.querySelectorAll('.idea-card.selected-card').forEach(function(c) {{
      c.classList.remove('selected-card');
    }});
    updateFooter();
  }}

  function updateFooter() {{
    var nums = Object.keys(selected).map(Number).sort(function(a,b){{return a-b;}});
    var display = document.getElementById('selected-display');
    var count = document.getElementById('sel-count');
    if (nums.length === 0) {{
      display.innerHTML = '&mdash;';
      count.textContent = '0 selected';
    }} else {{
      display.textContent = nums.join(', ');
      count.textContent = nums.length + ' selected';
    }}
  }}

  function copySelection() {{
    var text = document.getElementById('selected-display').textContent;
    if (!text || text === '—') return;
    navigator.clipboard.writeText(text).then(function() {{
      var btn = document.getElementById('copy-btn');
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
      setTimeout(function() {{
        btn.textContent = 'Copy';
        btn.classList.remove('copied');
      }}, 1500);
    }});
  }}

  // ---- Selected card highlight style (injected dynamically so we don't need a separate CSS block) ----
  var style = document.createElement('style');
  style.textContent = '.idea-card.selected-card {{ border-color: #7C3AED !important; background: #160F2A !important; }} .idea-card.selected-card .num-badge {{ background: #7C3AED; border-color: #7C3AED; color: #fff; }}';
  document.head.appendChild(style);
</script>
</body>
</html>"""

    return html


def main():
    batches = load_all_batches()

    if not batches:
        print("No instagram-ideas JSON files found in outputs/. Nothing to build.")
        return

    print(f"Found {len(batches)} batch(es):")
    for date_str, ideas in batches:
        print(f"  {date_str}: {len(ideas)} ideas")

    html = build_html(batches)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(html)

    total = sum(len(ideas) for _, ideas in batches)
    print(f"\nDashboard written: {OUTPUT_PATH}")
    print(f"Batches: {len(batches)}  |  Total ideas: {total}")


if __name__ == "__main__":
    main()
