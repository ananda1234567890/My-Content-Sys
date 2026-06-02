#!/usr/bin/env python3
"""
Generate LinkedIn carousel slides via Kie.ai (gpt-image-2-image-to-image)
and stitch them into a PDF.

Each slide is a 1:1 cinematic AI-generated image matching the carousel brand guide.

Usage:
    python3 scripts/generate-carousel-kieai.py --json posts/002-slug/content.json --output posts/002-slug/carousel.pdf
"""

import json
import os
import time
import argparse
import requests
from io import BytesIO
from PIL import Image

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Brand guide hosted on Cloudinary — passed as input_urls so Kie.ai can actually see the style
CAROUSEL_REF_URL = "https://res.cloudinary.com/duoq5xmdp/image/upload/v1779533851/Brand_Carousel_Guide_dz6mz3.png"
INFOGRAPHIC_REF_URL = "https://res.cloudinary.com/duoq5xmdp/image/upload/v1779533849/Infographic_Guide_g2ins5.png"


def get_api_key():
    env_path = os.path.join(WORKSPACE_ROOT, '.env')
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('KIE_AI_API_KEY='):
                return line.split('=', 1)[1]
    raise ValueError("KIE_AI_API_KEY not found in .env")


def submit_task(prompt, ref_url, api_key):
    """Submit a 1:1 generation task to Kie.ai and return task ID."""
    resp = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "gpt-image-2-image-to-image",
            "input": {
                "prompt": prompt,
                "width": 1080,
                "height": 1080,
                "image_num": 1,
                "resolution": "1K",
                "input_urls": [ref_url]
            }
        }
    )
    if resp.status_code != 200:
        raise ValueError(f"API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if "data" not in data or "taskId" not in data["data"]:
        raise ValueError(f"Unexpected response: {data}")
    return data["data"]["taskId"]


def poll_task(task_id, api_key, timeout=360):
    """Poll until task completes. Returns image URL."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(6)
        r = requests.get(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        payload = r.json()
        state = payload["data"]["state"]
        if state == "success":
            result = json.loads(payload["data"]["resultJson"])
            return result["resultUrls"][0]
        elif state in ("failed", "error", "FAILED"):
            raise ValueError(f"Task {task_id} failed: {payload}")
        print(f"    [{task_id[:8]}...] state={state}, waiting...")
    raise TimeoutError(f"Task {task_id} timed out after {timeout}s")


def download_image(url):
    r = requests.get(url, timeout=30)
    img = Image.open(BytesIO(r.content))
    w, h = img.size
    if w != h:
        # Crop to square — don't resize, just cut to the smaller dimension
        size = min(w, h)
        left = (w - size) // 2
        top = (h - size) // 2
        img = img.crop((left, top, left + size, top + size))
    return img


# ── PROMPT TEMPLATES ──────────────────────────────────────────────────────────

SQUARE_RULE = (
    "CRITICAL FORMAT RULE: Output must be exactly 1:1 square ratio, 1080x1080 pixels. "
    "Fill the entire square canvas edge to edge. "
    "No black bars, no letterboxing, no pillarboxing, no empty margins, no portrait or landscape cropping. "
    "Every element — background, imagery, text — must be designed natively for a square frame. "
)

STYLE = (
    "LinkedIn carousel slide. "
    "Exactly match the visual style, color palette, typography, and mood of the reference image. "
    "Deep dark purple/black background. Bold white sans-serif typography. "
    "Purple accent color (#7C3AED, #A78BFA). Cinematic atmospheric imagery. "
    "High contrast. Minimal text. One idea per slide. No borders."
)


def prompt_cover(title):
    return (
        f"{SQUARE_RULE}"
        f"{STYLE} "
        f"COVER SLIDE. "
        f"Very large bold white headline: '{title}'. "
        f"'swipe →' in small gray text near bottom. "
        f"'ANANDA PARAMANICK' in small white caps at very bottom. "
        f"Atmospheric dark background with subtle purple light bleed or bokeh."
    )


def prompt_content(number, heading, subtitle, takeaway, visual):
    return (
        f"{SQUARE_RULE}"
        f"{STYLE} "
        f"CONTENT SLIDE. "
        f"Dark purple circle badge top-left with bold white number '{number}' inside. "
        f"Large bold white headline: '{heading}'. "
        f"Smaller purple or gray subtitle: '{subtitle}'. "
        f"Italic white takeaway text at bottom: '{takeaway}'. "
        f"Background visual concept — make this specific and relevant to the point: {visual}"
    )


def prompt_cta(cta_text, cta_subtitle):
    return (
        f"{SQUARE_RULE}"
        f"{STYLE} "
        f"FINAL CTA SLIDE. "
        f"Large bold white centered text: '{cta_text}'. "
        f"Italic purple subtitle: '{cta_subtitle}'. "
        f"'Ananda Paramanick' in white, 'YouTube Video Editor' in gray below. "
        f"Deep atmospheric background with centered purple radial glow."
    )


# ── MAIN ──────────────────────────────────────────────────────────────────────

def generate_carousel(content, output_path):
    api_key = get_api_key()

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    png_dir = os.path.splitext(output_path)[0] + "-slides"
    os.makedirs(png_dir, exist_ok=True)

    # Build slide specs
    specs = [("slide-00-cover", prompt_cover(content["title"]))]
    for slide in content["slides"]:
        name = f"slide-{slide['number']:02d}-{slide['heading'].lower().replace(' ', '-')[:20]}"
        specs.append((name, prompt_content(
            slide["number"], slide["heading"], slide["subtitle"], slide["takeaway"],
            slide.get("visual", "Atmospheric dark background with subtle purple glow.")
        )))
    specs.append(("slide-99-cta", prompt_cta(
        content.get("cta_text", "Follow for more."),
        content.get("cta_subtitle", "")
    )))

    # Submit all tasks at once
    print(f"\nSubmitting {len(specs)} slides to Kie.ai (1:1, 1K resolution)...")
    tasks = []
    for name, prompt in specs:
        task_id = submit_task(prompt, CAROUSEL_REF_URL, api_key)
        tasks.append((name, task_id))
        print(f"  ✓ {name} → task {task_id[:12]}...")

    # Poll all tasks
    print(f"\nPolling for results...")
    slides_in_order = []
    for name, task_id in tasks:
        print(f"  Waiting for {name}...")
        url = poll_task(task_id, api_key)
        img = download_image(url).convert("RGB")
        png_path = os.path.join(png_dir, f"{name}.png")
        img.save(png_path)
        slides_in_order.append(img)
        print(f"  ✓ Saved: {png_path}")

    # Stitch into PDF
    print(f"\nStitching {len(slides_in_order)} slides into PDF...")
    slides_in_order[0].save(
        output_path, "PDF", resolution=100.0,
        save_all=True, append_images=slides_in_order[1:]
    )
    print(f"\n✓ Carousel saved: {output_path} ({len(slides_in_order)} slides)")
    print(f"✓ Slide PNGs: {png_dir}/")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate LinkedIn carousel via Kie.ai")
    parser.add_argument("--json", required=True, help="Path to content JSON file")
    parser.add_argument("--output", required=True, help="Output PDF path")
    args = parser.parse_args()

    with open(args.json) as f:
        content = json.load(f)

    generate_carousel(content, args.output)
