#!/usr/bin/env python3
"""
Test Gemini 3.1 Flash-Lite video analysis via OpenRouter.
Downloads a video URL, encodes to base64, sends to model.

Usage:
    python3 scripts/test-video-analysis.py --url "https://..."
    python3 scripts/test-video-analysis.py --url "https://..." --prompt "What editing techniques are used?"
"""

import os
import base64
import argparse
import requests

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_api_key():
    env_path = os.path.join(WORKSPACE_ROOT, '.env')
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('OPENROUTER_API_KEY='):
                return line.split('=', 1)[1]
    raise ValueError("OPENROUTER_API_KEY not found in .env")


def download_video_as_base64(url):
    print(f"Downloading video...")
    r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    content_type = r.headers.get("content-type", "video/mp4").split(";")[0].strip()
    b64 = base64.b64encode(r.content).decode("utf-8")
    size_mb = len(r.content) / (1024 * 1024)
    print(f"  Downloaded {size_mb:.1f}MB ({content_type})")
    return b64, content_type


def analyze_video(video_url, prompt):
    api_key = get_api_key()
    b64, content_type = download_video_as_base64(video_url)

    print(f"Sending to gemini/gemini-3.1-flash-lite via OpenRouter...")
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "google/gemini-3.1-flash-lite",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "video_url",
                            "video_url": {
                                "url": f"data:{content_type};base64,{b64}"
                            }
                        }
                    ]
                }
            ]
        },
        timeout=120
    )

    if resp.status_code != 200:
        raise ValueError(f"API error {resp.status_code}: {resp.text}")

    data = resp.json()
    return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Video URL to analyze")
    parser.add_argument("--prompt", default="Describe everything in this video in detail.", help="Analysis prompt")
    args = parser.parse_args()

    result = analyze_video(args.url, args.prompt)
    print(f"\n{'='*60}\nMODEL RESPONSE\n{'='*60}\n{result}\n")
