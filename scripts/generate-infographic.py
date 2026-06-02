#!/usr/bin/env python3
"""
Generate a single LinkedIn infographic image via Kie.ai (gpt-image-2-image-to-image).

Dimensions: 1080x1350 (4:5) — standard LinkedIn portrait image
Reference: Infographic brand guide on Cloudinary (dark purple, data-viz style)

Usage:
    python3 scripts/generate-infographic.py --prompt "your prompt here" --output posts/NNN-slug/image.png
    python3 scripts/generate-infographic.py --post posts/001-slug/  # reads prompt from post.md
"""

import json
import os
import time
import argparse
import re
import requests
from io import BytesIO
from PIL import Image

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INFOGRAPHIC_REF_URL = "https://res.cloudinary.com/duoq5xmdp/image/upload/v1779533849/Infographic_Guide_g2ins5.png"

STYLE_PREFIX = (
    "STRICT 4:5 PORTRAIT FORMAT — 1080x1350 pixels. "
    "The entire composition must fill the full portrait canvas with no letterboxing, no black bars, no blank margins, and no square or landscape cropping. "
    "Design the layout natively for portrait — all text, imagery, and visual elements positioned within a tall portrait frame. "
    "Exactly match the visual style, color palette, typography, and layout of the reference image. "
)


def get_api_key():
    env_path = os.path.join(WORKSPACE_ROOT, '.env')
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('KIE_AI_API_KEY='):
                return line.split('=', 1)[1]
    raise ValueError("KIE_AI_API_KEY not found in .env")


def extract_prompt_from_post(post_dir):
    """Read the image prompt from a post.md file."""
    post_md = os.path.join(post_dir, 'post.md')
    with open(post_md) as f:
        content = f.read()
    # Extract everything after "**Prompt:**" or "Prompt:" in Image Notes section
    match = re.search(r'\*?\*?Prompt:\*?\*?\s*\n(.*?)(?:\n##|\Z)', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    raise ValueError(f"No prompt found in {post_md} — add a '**Prompt:**' line under '## Image Notes'")


def submit_task(prompt, api_key):
    full_prompt = STYLE_PREFIX + prompt
    resp = requests.post(
        "https://api.kie.ai/api/v1/jobs/createTask",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "gpt-image-2-image-to-image",
            "input": {
                "prompt": full_prompt,
                "width": 1080,
                "height": 1350,
                "image_num": 1,
                "resolution": "1K",
                "input_urls": [INFOGRAPHIC_REF_URL]
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
            raise ValueError(f"Task failed: {payload}")
        print(f"  [{task_id[:8]}...] state={state}, waiting...")
    raise TimeoutError(f"Task timed out after {timeout}s")


def generate_infographic(prompt, output_path):
    api_key = get_api_key()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    print(f"Submitting infographic to Kie.ai (1080x1350, 1K)...")
    task_id = submit_task(prompt, api_key)
    print(f"  Task: {task_id[:12]}...")

    print(f"Polling for result...")
    url = poll_task(task_id, api_key)

    print(f"Downloading image...")
    r = requests.get(url, timeout=30)
    img = Image.open(BytesIO(r.content)).convert("RGB")
    img.save(output_path)
    print(f"\n✓ Infographic saved: {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate LinkedIn infographic via Kie.ai")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt", help="Image prompt (content description)")
    group.add_argument("--post", help="Path to post folder — reads prompt from post.md")
    parser.add_argument("--output", help="Output image path (default: <post>/image.png)")
    args = parser.parse_args()

    if args.post:
        prompt = extract_prompt_from_post(args.post)
        output = args.output or os.path.join(args.post, "image.png")
        print(f"Prompt extracted from post.md:\n{prompt}\n")
    else:
        prompt = args.prompt
        if not args.output:
            raise ValueError("--output required when using --prompt")
        output = args.output

    generate_infographic(prompt, output)
