#!/usr/bin/env python3
"""
Regenerate only the cover slide for a carousel and restitch the PDF.
Usage:
    python3 scripts/regen-cover-slide.py --post posts/020-planar-tracking-after-effects
"""

import json
import os
import sys
import time
import argparse
import requests
from io import BytesIO
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAROUSEL_REF_URL = "https://res.cloudinary.com/duoq5xmdp/image/upload/v1780567511/Brand_Carousel_Guide_btgnqz.png"


def get_api_key():
    env_path = os.path.join(WORKSPACE_ROOT, '.env')
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('KIE_AI_API_KEY='):
                return line.split('=', 1)[1]
    raise ValueError("KIE_AI_API_KEY not found in .env")


def submit_task(prompt, api_key):
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
                "input_urls": [CAROUSEL_REF_URL]
            }
        }
    )
    if resp.status_code != 200:
        raise ValueError(f"API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if "data" not in data or not data["data"] or "taskId" not in data["data"]:
        raise ValueError(f"Unexpected response: {data}")
    return data["data"]["taskId"]


def poll_task(task_id, api_key, timeout=360):
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
        size = min(w, h)
        left = (w - size) // 2
        top = (h - size) // 2
        img = img.crop((left, top, left + size, top + size))
    return img


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--post", required=True, help="Post folder, e.g. posts/020-planar-tracking-after-effects")
    args = parser.parse_args()

    post_dir = os.path.join(WORKSPACE_ROOT, args.post)
    content_path = os.path.join(post_dir, "content.json")
    slides_dir = os.path.join(post_dir, "carousel-slides")
    pdf_path = os.path.join(post_dir, "carousel.pdf")

    with open(content_path) as f:
        content = json.load(f)

    title = content["title"]
    api_key = get_api_key()

    # Prompt — reduced font size, strict centering, no edge clipping, no white border
    prompt = (
        "1:1 square 1080x1080px LinkedIn carousel COVER SLIDE. "
        "Deep dark purple/black background (#0D0B16), no white borders, no white lines on any edge, background fills 100% of canvas. "
        "Match the reference image style: bold white sans-serif, purple accents #7C3AED, cinematic dark mood. "
        f"Headline text: '{title}'. "
        "Text must be: perfectly centered horizontally AND vertically, font size medium-large (NOT oversized), "
        "broken into 4-5 short lines so every word fits comfortably with at least 150px margin on left AND right. "
        "Every single letter fully inside the canvas — nothing touches or crosses any edge. "
        "Small purple 'swipe →' text near bottom center. "
        "Small white caps 'ANANDA PARAMANICK' at very bottom center. "
        "Subtle purple bokeh or light bleed in background only — no other elements."
    )

    print(f"\nRegenerating cover slide for: {title}")
    print("Submitting to Kie.ai...")
    task_id = submit_task(prompt, api_key)
    print(f"  Task ID: {task_id}")

    print("Polling for result...")
    url = poll_task(task_id, api_key)
    img = download_image(url).convert("RGB")

    cover_path = os.path.join(slides_dir, "slide-00-cover.png")
    img.save(cover_path)
    print(f"  ✓ Saved: {cover_path}")

    # Restitch PDF from all slides in order
    print("\nRestitching PDF...")
    slide_files = sorted([
        f for f in os.listdir(slides_dir) if f.endswith(".png")
    ])
    print(f"  Slides found: {slide_files}")

    images = []
    for fname in slide_files:
        slide_img = Image.open(os.path.join(slides_dir, fname)).convert("RGB")
        images.append(slide_img)

    images[0].save(
        pdf_path, "PDF", resolution=100.0,
        save_all=True, append_images=images[1:]
    )
    print(f"  ✓ PDF restitched: {pdf_path} ({len(images)} slides)")


if __name__ == "__main__":
    main()
