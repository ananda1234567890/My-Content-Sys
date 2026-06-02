#!/usr/bin/env python3
"""
Build an HTML dashboard showing all posts in the posts/ directory.
Run this after creating/updating posts to regenerate the dashboard.
Output: outputs/dashboard.html
"""

import os
import base64
import glob
from pathlib import Path

# Auto-detect workspace root (parent of scripts/)
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(WORKSPACE, "posts")
OUTPUT = os.path.join(WORKSPACE, "outputs", "dashboard.html")


def image_to_base64(path):
    ext = Path(path).suffix.lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext.lstrip("."), "image/png")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{data}"


def parse_post_md(path):
    with open(path) as f:
        content = f.read()
    meta = {}
    lines = content.split("\n")
    for line in lines:
        if line.startswith("**") and ":**" in line:
            key = line.split(":**")[0].replace("**", "").strip()
            val = line.split(":**")[1].strip()
            meta[key] = val
    post_text = ""
    in_text = False
    for line in lines:
        if "Post Text" in line or "copy-paste ready" in line.lower():
            in_text = True
            continue
        if in_text:
            if line.startswith("##"):
                break
            post_text += line + "\n"
    return meta, post_text.strip()


def get_carousel_slides(post_dir):
    # Check both root-level slide-*.png and carousel-slides/ subfolder
    slides = sorted(glob.glob(os.path.join(post_dir, "slide-*.png")))
    if not slides:
        slides = sorted(glob.glob(os.path.join(post_dir, "carousel-slides", "slide-*.png")))
    return slides


carousel_counter = [0]

def build_carousel_html(slides):
    carousel_counter[0] += 1
    cid = f"carousel-{carousel_counter[0]}"
    total = len(slides)
    slide_imgs = []
    for i, slide_path in enumerate(slides):
        b64 = image_to_base64(slide_path)
        hidden = ' style="display:none"' if i > 0 else ''
        slide_imgs.append(
            f'<img class="carousel-slide" data-carousel="{cid}" data-index="{i}"{hidden} src="{b64}" alt="Slide {i+1}">'
        )
    dots = []
    for i in range(total):
        active = " active" if i == 0 else ""
        dots.append(f'<button class="dot{active}" data-carousel="{cid}" data-dot="{i}" onclick="carouselGo(\'{cid}\', {i})"></button>')
    dots_html = "".join(dots)
    slides_html = "".join(slide_imgs)
    return f"""
        <div class="carousel" id="{cid}">
            <div class="carousel-stage">
                {slides_html}
                <button class="carousel-arrow arrow-left" onclick="carouselNav('{cid}', -1)">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
                </button>
                <button class="carousel-arrow arrow-right" onclick="carouselNav('{cid}', 1)">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
                </button>
                <div class="carousel-counter" id="{cid}-counter">1 / {total}</div>
            </div>
            <div class="carousel-dots">{dots_html}</div>
        </div>
    """


def build_card(post_dir, all_post_data):
    slug = os.path.basename(post_dir)
    post_md = os.path.join(post_dir, "post.md")
    image_path = os.path.join(post_dir, "image.png")
    pdf_path = os.path.join(post_dir, "carousel.pdf")

    if not os.path.exists(post_md):
        return None

    meta, post_text = parse_post_md(post_md)
    carousel_slides = get_carousel_slides(post_dir)

    is_carousel = os.path.exists(pdf_path) or len(carousel_slides) > 0
    post_num = slug.split("-")[0] if slug[0].isdigit() else slug
    type_label = "Carousel" if is_carousel else "Infographic"
    type_badge_color = "#7c3aed" if is_carousel else "#0077b5"

    visual_html = '<span class="no-visual">--</span>'
    if len(carousel_slides) > 0:
        visual_html = build_carousel_html(carousel_slides)
    elif os.path.exists(image_path):
        visual_html = f'<img src="{image_to_base64(image_path)}" alt="Post image" class="post-image">'

    post_text_html = post_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

    # Store data in the global JS object (avoids attribute escaping issues)
    all_post_data[post_num] = {
        "num": post_num,
        "slug": slug,
        "type": "carousel" if is_carousel else "infographic",
        "text": post_text
    }

    return f"""
    <div class="card" data-num="{post_num}">
        <div class="card-header">
            <span class="sel-dot" id="dot-{post_num}"></span>
            <span class="card-num">{post_num}</span>
            <span class="type-badge" style="background:{type_badge_color}">{type_label}</span>
            <button class="copy-btn no-select">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
                Copy text
            </button>
            <textarea class="hidden-text" style="display:none">{post_text}</textarea>
        </div>
        <div class="card-visual">
            {visual_html}
        </div>
        <div class="card-text">
            <div class="post-text">{post_text_html}</div>
        </div>
    </div>
    """


def build_html():
    import json
    carousel_counter[0] = 0
    post_dirs = sorted(glob.glob(os.path.join(POSTS_DIR, "*")))
    post_dirs = [d for d in post_dirs if os.path.isdir(d) and not os.path.basename(d).startswith(".")]

    all_post_data = {}
    cards = []
    for post_dir in post_dirs:
        card = build_card(post_dir, all_post_data)
        if card:
            cards.append(card)

    post_data_js = json.dumps(all_post_data)

    # Build rows of 2
    rows_html = ""
    for i in range(0, len(cards), 2):
        left = cards[i]
        right = cards[i + 1] if i + 1 < len(cards) else '<div class="card empty"></div>'
        rows_html += f'<div class="row">{left}{right}</div>\n'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
            background: #fafafa;
            color: #09090b;
            padding: 32px 32px 80px;
            -webkit-font-smoothing: antialiased;
        }}

        h1 {{
            font-size: 22px;
            font-weight: 600;
            letter-spacing: -0.025em;
            margin-bottom: 24px;
        }}

        .row {{
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
        }}

        .card {{
            flex: 1;
            background: #fff;
            border: 1px solid #e4e4e7;
            border-radius: 10px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        .card.empty {{
            border: none;
            background: transparent;
        }}

        .card-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border-bottom: 1px solid #f4f4f5;
        }}

        .card-num {{
            font-size: 13px;
            font-weight: 700;
            color: #a1a1aa;
            font-variant-numeric: tabular-nums;
        }}

        .card-visual {{
            display: flex;
            justify-content: center;
            align-items: center;
            background: #fafafa;
            min-height: 80px;
        }}

        .card-text {{
            padding: 12px 14px;
            border-top: 1px solid #f4f4f5;
            flex: 1;
        }}

        .post-text {{
            font-size: 14px;
            line-height: 1.6;
            font-weight: 450;
            color: #18181b;
            max-height: 220px;
            overflow-y: auto;
            padding-right: 6px;
        }}
        .post-text::-webkit-scrollbar {{ width: 3px; }}
        .post-text::-webkit-scrollbar-track {{ background: transparent; }}
        .post-text::-webkit-scrollbar-thumb {{ background: #e4e4e7; border-radius: 3px; }}

        .type-badge {{
            font-size: 10px;
            font-weight: 600;
            color: #fff;
            padding: 2px 7px;
            border-radius: 4px;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }}

        .copy-btn {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 500;
            font-family: inherit;
            color: #71717a;
            background: #fff;
            border: 1px solid #e4e4e7;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.15s;
            margin-left: auto;
            flex-shrink: 0;
        }}
        .copy-btn:hover {{
            background: #f4f4f5;
            color: #09090b;
            border-color: #d4d4d8;
        }}
        .copy-btn.copied {{
            background: #09090b;
            color: #fff;
            border-color: #09090b;
        }}

        /* Selection dot */
        .sel-dot {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 2px solid #d4d4d8;
            background: #fff;
            flex-shrink: 0;
            transition: all 0.15s;
        }}
        .card.selected .sel-dot {{
            background: #7c3aed;
            border-color: #7c3aed;
        }}
        .card.selected .sel-dot::after {{
            content: '';
            display: block;
            width: 4px;
            height: 8px;
            border: 2px solid #fff;
            border-top: none;
            border-left: none;
            transform: rotate(45deg);
            margin: 1px auto 0;
        }}
        .card {{ cursor: pointer; }}

        /* Card selection */
        .card.selected {{
            border-color: #7c3aed;
            background: #faf5ff;
            box-shadow: 0 0 0 2px #7c3aed22;
        }}
        .card.selected .card-num {{
            color: #7c3aed;
        }}

        /* Fixed footer bar */
        .footer {{
            position: fixed;
            bottom: 0; left: 0; right: 0;
            background: #09090b;
            border-top: 1px solid #27272a;
            padding: 12px 32px;
            display: flex;
            align-items: center;
            gap: 12px;
            z-index: 100;
        }}
        .footer-label {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: #71717a;
            white-space: nowrap;
        }}
        .footer-display {{
            flex: 1;
            background: #18181b;
            border: 1px solid #3f3f46;
            border-radius: 6px;
            padding: 7px 14px;
            font-size: 13px;
            color: #e4e4e7;
            min-height: 34px;
            font-family: inherit;
            user-select: all;
        }}
        .footer-count {{
            font-size: 12px;
            color: #71717a;
            white-space: nowrap;
        }}
        .footer-clear {{
            background: transparent;
            color: #71717a;
            border: 1px solid #3f3f46;
            border-radius: 6px;
            padding: 7px 14px;
            font-size: 12px;
            font-family: inherit;
            font-weight: 500;
            cursor: pointer;
            white-space: nowrap;
            transition: color 0.15s, border-color 0.15s;
        }}
        .footer-clear:hover {{ color: #e4e4e7; border-color: #71717a; }}
        .footer-copy {{
            background: #7c3aed;
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
        .footer-copy:hover {{ background: #6d28d9; }}
        .footer-copy.copied {{ background: #16a34a; }}

        .no-visual {{
            color: #d4d4d8;
            padding: 24px;
        }}

        .post-image {{
            max-height: 260px;
            max-width: 100%;
            width: auto;
            border-radius: 0;
            object-fit: contain;
        }}

        /* Carousel */
        .carousel {{
            width: 100%;
        }}
        .carousel-stage {{
            position: relative;
            overflow: hidden;
            background: #f4f4f5;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .carousel-slide {{
            display: block;
            max-height: 260px;
            max-width: 100%;
            width: auto;
            height: auto;
            object-fit: contain;
        }}

        .carousel-arrow {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: none;
            background: rgba(255,255,255,0.9);
            box-shadow: 0 1px 4px rgba(0,0,0,0.12);
            color: #09090b;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.15s;
            opacity: 0;
            z-index: 2;
        }}
        .carousel-stage:hover .carousel-arrow {{
            opacity: 1;
        }}
        .carousel-arrow:hover {{
            background: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.16);
        }}
        .arrow-left {{ left: 6px; }}
        .arrow-right {{ right: 6px; }}

        .carousel-counter {{
            position: absolute;
            bottom: 6px;
            right: 8px;
            background: rgba(0,0,0,0.6);
            color: #fff;
            font-size: 10px;
            font-weight: 500;
            padding: 2px 7px;
            border-radius: 10px;
            z-index: 2;
            font-variant-numeric: tabular-nums;
        }}

        .carousel-dots {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            padding: 6px 0;
        }}
        .dot {{
            width: 5px;
            height: 5px;
            border-radius: 9999px;
            border: none;
            background: #d4d4d8;
            cursor: pointer;
            padding: 0;
            transition: all 0.2s;
        }}
        .dot:hover {{ background: #a1a1aa; }}
        .dot.active {{
            background: #18181b;
            width: 16px;
        }}
    </style>
</head>
<body>
    <h1>Content Dashboard</h1>
    {rows_html}

    <div class="footer">
        <span class="footer-label">Schedule</span>
        <div class="footer-display" id="footer-display">&mdash;</div>
        <span class="footer-count" id="footer-count">0 selected</span>
        <button class="footer-clear" id="footer-clear-btn">Clear</button>
        <button class="footer-copy" id="footer-copy-btn">Copy for Claude</button>
    </div>

    <script>
        var POST_DATA = {post_data_js};
        var selected = {{}};

        // Document-level click — same pattern as ideas dashboard
        document.addEventListener('click', function(e) {{
            // Copy text button
            var copyBtn = e.target.closest('.copy-btn.no-select');
            if (copyBtn) {{
                var textarea = copyBtn.nextElementSibling;
                navigator.clipboard.writeText(textarea.value).then(function() {{
                    copyBtn.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg> Copied!';
                    copyBtn.classList.add('copied');
                    setTimeout(function() {{
                        copyBtn.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg> Copy text';
                        copyBtn.classList.remove('copied');
                    }}, 2000);
                }});
                return;
            }}

            // Card selection — ignore carousel arrows/dots
            if (e.target.closest('.carousel-arrow') || e.target.closest('.carousel-dots')) return;
            var card = e.target.closest('.card');
            if (!card) return;
            var num = card.dataset.num;
            if (selected[num]) {{
                delete selected[num];
                card.classList.remove('selected');
            }} else {{
                selected[num] = POST_DATA[num];
                card.classList.add('selected');
            }}
            updateFooter();
        }});

        document.getElementById('footer-clear-btn').addEventListener('click', function() {{
            selected = {{}};
            document.querySelectorAll('.card.selected').forEach(function(c) {{ c.classList.remove('selected'); }});
            updateFooter();
        }});

        document.getElementById('footer-copy-btn').addEventListener('click', function() {{
            var nums = Object.keys(selected).sort(function(a,b){{return Number(a)-Number(b);}});
            if (nums.length === 0) return;
            var lines = ['Schedule these posts on Buffer LinkedIn. For each post, ask me the date and time to schedule it.\\n'];
            nums.forEach(function(n, i) {{
                var d = selected[n];
                var note = d.type === 'carousel'
                    ? 'TYPE: carousel — schedule the text only. After scheduling, remind me to manually upload posts/' + d.slug + '/carousel.pdf to Buffer.'
                    : 'TYPE: infographic — upload posts/' + d.slug + '/image.png to Cloudinary, then schedule with the image.';
                lines.push('POST ' + (i+1) + ':');
                lines.push('FOLDER: ' + d.slug);
                lines.push(note);
                lines.push('---');
                lines.push(d.text);
                lines.push('---\\n');
            }});
            var btn = this;
            navigator.clipboard.writeText(lines.join('\\n')).then(function() {{
                btn.textContent = 'Copied!';
                btn.classList.add('copied');
                setTimeout(function() {{ btn.textContent = 'Copy for Claude'; btn.classList.remove('copied'); }}, 2000);
            }});
        }});

        function updateFooter() {{
            var nums = Object.keys(selected).sort(function(a,b){{return Number(a)-Number(b);}});
            document.getElementById('footer-display').textContent = nums.length === 0 ? '—' :
                nums.map(function(n) {{ return '#' + n + ' (' + selected[n].type + ')'; }}).join('  ·  ');
            document.getElementById('footer-count').textContent = nums.length === 0 ? '0 selected' : nums.length + ' selected';
        }}

        function carouselNav(carouselId, direction) {{
            const slides = document.querySelectorAll('img[data-carousel="' + carouselId + '"]');
            if (slides.length === 0) return;
            let current = 0;
            slides.forEach((s, i) => {{ if (s.style.display !== 'none') current = i; }});
            const next = Math.max(0, Math.min(slides.length - 1, current + direction));
            if (next === current) return;
            carouselGo(carouselId, next);
        }}

        function carouselGo(carouselId, index) {{
            const slides = document.querySelectorAll('img[data-carousel="' + carouselId + '"]');
            const dots = document.querySelectorAll('button[data-carousel="' + carouselId + '"]');
            const total = slides.length;
            slides.forEach((s, i) => {{ s.style.display = i === index ? 'block' : 'none'; }});
            dots.forEach((d, i) => {{ d.classList.toggle('active', i === index); }});
            document.getElementById(carouselId + '-counter').textContent = (index + 1) + ' / ' + total;
        }}
    </script>
</body>
</html>"""

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        f.write(html)
    print(f"Dashboard built: {OUTPUT}")
    print(f"Posts found: {len(cards)}")


if __name__ == "__main__":
    build_html()
