#!/usr/bin/env python3
"""
Schedule a post to Buffer (LinkedIn).

Usage:
  python3 scripts/schedule-to-buffer.py posts/017-ai-transition-bridging
  python3 scripts/schedule-to-buffer.py posts/017-ai-transition-bridging --time "2026-06-09T09:00:00+05:30"
  python3 scripts/schedule-to-buffer.py posts/017-ai-transition-bridging --queue

- If a carousel.pdf exists in the post folder, it is uploaded to Cloudinary and attached.
- If an image.png exists, it is uploaded to Cloudinary and attached.
- Defaults to 9am IST tomorrow if no --time given and --queue not passed.
"""

import sys
import os
import re
import json
import hashlib
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path


def load_env(path=".env"):
    env = {}
    try:
        for line in Path(path).read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env

_env = load_env()
def _get(key): return os.environ.get(key) or _env.get(key)

BUFFER_TOKEN               = _get("BUFFER_TOKEN")
BUFFER_LINKEDIN_CHANNEL_ID = _get("BUFFER_LINKEDIN_CHANNEL_ID")
CLOUDINARY_CLOUD_NAME      = _get("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY         = _get("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET      = _get("CLOUDINARY_API_SECRET")
BUFFER_API_URL             = "https://api.buffer.com"


# ── Cloudinary ──────────────────────────────────────────────────────────────

def cloudinary_upload(file_path: Path, public_id: str, resource_type: str = "image") -> str:
    """Upload a file to Cloudinary and return its secure URL."""
    timestamp = str(int(time.time()))
    params_to_sign = f"public_id={public_id}&timestamp={timestamp}"
    sig = hashlib.sha1(f"{params_to_sign}{CLOUDINARY_API_SECRET}".encode()).hexdigest()

    boundary = "----FormBoundaryBuffer"
    content_type = "application/pdf" if file_path.suffix == ".pdf" else "image/png"

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + file_data + (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="api_key"\r\n\r\n{CLOUDINARY_API_KEY}'
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="timestamp"\r\n\r\n{timestamp}'
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="public_id"\r\n\r\n{public_id}'
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="signature"\r\n\r\n{sig}'
        f"\r\n--{boundary}--\r\n"
    ).encode()

    url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/{resource_type}/upload"
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["secure_url"]


# ── Buffer GraphQL ───────────────────────────────────────────────────────────

def graphql(query: str) -> dict:
    payload = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        BUFFER_API_URL, data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {BUFFER_TOKEN}",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}")
        sys.exit(1)


def get_channel_id() -> str:
    if BUFFER_LINKEDIN_CHANNEL_ID:
        return BUFFER_LINKEDIN_CHANNEL_ID

    print("BUFFER_LINKEDIN_CHANNEL_ID not in .env — fetching from API...")
    org_id = graphql("{ account { organizations { id } } }")["data"]["account"]["organizations"][0]["id"]
    channels = graphql(f'{{ channels(input: {{ organizationId: "{org_id}" }}) {{ id name service }} }}')["data"]["channels"]
    linkedin = [c for c in channels if c["service"] == "linkedin"]

    if not linkedin:
        print("Error: No LinkedIn channel connected in Buffer.")
        sys.exit(1)
    if len(linkedin) > 1:
        print("Multiple LinkedIn channels — set BUFFER_LINKEDIN_CHANNEL_ID in .env:")
        for c in linkedin: print(f"  {c['id']}  {c['name']}")
        sys.exit(1)

    return linkedin[0]["id"]


def extract_post_text(post_folder: Path) -> str:
    post_md = post_folder / "post.md"
    if not post_md.exists():
        print(f"Error: {post_md} not found.")
        sys.exit(1)

    content = post_md.read_text(encoding="utf-8")
    match = re.search(r"## Post Text \(copy-paste ready\)\n\n(.*?)(?:\n\n## |\Z)", content, re.DOTALL)
    if not match:
        print("Error: Could not find '## Post Text (copy-paste ready)' section in post.md")
        sys.exit(1)

    return match.group(1).strip()


def extract_title(post_folder: Path) -> str:
    post_md = post_folder / "post.md"
    content = post_md.read_text(encoding="utf-8")
    match = re.match(r"^# (.+)", content)
    return match.group(1).strip() if match else post_folder.name


def default_due_at() -> str:
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    scheduled = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if scheduled <= now:
        scheduled = scheduled.replace(day=scheduled.day + 1)
    return scheduled.isoformat()


def build_assets_field(post_folder: Path) -> str:
    """Upload media if present and return the GraphQL assets field string."""
    slug = post_folder.name
    carousel_pdf = post_folder / "carousel.pdf"
    image_png = post_folder / "image.png"

    if carousel_pdf.exists():
        if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
            print("Warning: carousel.pdf found but Cloudinary credentials missing — scheduling text-only.")
            return ""

        print("Uploading carousel PDF to Cloudinary...")
        pdf_url = cloudinary_upload(carousel_pdf, f"posts/{slug}-carousel", resource_type="raw")
        print(f"  PDF URL: {pdf_url}")

        # Use cover slide as thumbnail if available, else first slide
        cover = post_folder / "carousel-slides" / "slide-00-cover.png"
        slides = sorted((post_folder / "carousel-slides").glob("*.png")) if (post_folder / "carousel-slides").exists() else []
        thumb_path = cover if cover.exists() else (slides[0] if slides else None)

        if thumb_path:
            print("Uploading cover thumbnail...")
            thumb_url = cloudinary_upload(thumb_path, f"posts/{slug}-cover", resource_type="image")
            print(f"  Thumbnail URL: {thumb_url}")
        else:
            print("Warning: no thumbnail found, Buffer may reject the document asset.")
            thumb_url = pdf_url

        title = extract_title(post_folder)
        return f'assets: [{{ document: {{ url: {json.dumps(pdf_url)}, title: {json.dumps(title)}, thumbnailUrl: {json.dumps(thumb_url)} }} }}]'

    elif image_png.exists():
        if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
            print("Warning: image.png found but Cloudinary credentials missing — scheduling text-only.")
            return ""

        print("Uploading image to Cloudinary...")
        img_url = cloudinary_upload(image_png, f"posts/{slug}-image", resource_type="image")
        print(f"  Image URL: {img_url}")
        return f'assets: [{{ image: {{ url: {json.dumps(img_url)} }} }}]'

    return ""


def schedule_post(channel_id: str, text: str, assets_field: str, due_at: str | None, add_to_queue: bool) -> dict:
    mode = "addToQueue" if add_to_queue else "customScheduled"
    due_at_field = "" if add_to_queue else f'dueAt: "{due_at}"'

    mutation = f"""
    mutation {{
      createPost(input: {{
        channelId: "{channel_id}"
        schedulingType: automatic
        mode: {mode}
        {due_at_field}
        text: {json.dumps(text)}
        {assets_field}
        aiAssisted: true
      }}) {{
        ... on PostActionSuccess {{
          post {{ id dueAt status }}
        }}
        ... on MutationError {{ message }}
      }}
    }}
    """
    return graphql(mutation)


STATUS_FILE = Path(__file__).parent.parent / "outputs" / "post-status.json"


def read_status() -> dict:
    try:
        return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_status(data: dict):
    STATUS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def mark_linkedin_posted(post_num: str):
    data = read_status()
    if post_num not in data:
        data[post_num] = {}
    data[post_num]["linkedin"] = True
    write_status(data)
    print(f"  Dashboard: marked post {post_num} as LinkedIn posted ✓")


def main():
    if not BUFFER_TOKEN:
        print("Error: BUFFER_TOKEN not set in .env")
        print("Get your token at: https://publish.buffer.com/settings/api")
        sys.exit(1)

    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    post_folder = Path(args[0])
    if not post_folder.exists():
        print(f"Error: {post_folder} does not exist.")
        sys.exit(1)

    # Extract post number from folder name (e.g. "023" from "023-three-hook-types")
    slug = post_folder.name
    post_num = slug.split("-")[0] if slug[0].isdigit() else slug

    # ── Check if already scheduled/posted ───────────────────────
    status = read_status()
    if status.get(post_num, {}).get("linkedin"):
        print(f"\n⚠️  ALREADY SCHEDULED/POSTED")
        print(f"   Post {post_num} is already marked as LinkedIn posted in the dashboard.")
        print(f"   Stopping. If you want to schedule again anyway, remove the LinkedIn mark from the dashboard first.")
        sys.exit(1)
    # ────────────────────────────────────────────────────────────

    add_to_queue = "--queue" in args
    text_only = "--text-only" in args
    due_at = None
    if not add_to_queue:
        if "--time" in args:
            due_at = args[args.index("--time") + 1]
        else:
            due_at = default_due_at()

    print(f"Reading post from: {post_folder}")
    text = extract_post_text(post_folder)
    print(f"Post text: {len(text)} characters")

    assets_field = "" if text_only else build_assets_field(post_folder)

    channel_id = get_channel_id()
    print(f"LinkedIn channel: {channel_id}")
    print(f"Mode: {'queue' if add_to_queue else due_at}")

    result = schedule_post(channel_id, text, assets_field, due_at, add_to_queue)
    post_data = result.get("data", {}).get("createPost", {})

    if "post" in post_data:
        post = post_data["post"]
        print(f"\nScheduled successfully")
        print(f"  Post ID : {post['id']}")
        print(f"  Status  : {post['status']}")
        if post.get("dueAt"):
            print(f"  Due at  : {post['dueAt']}")
        # ── Auto-mark as LinkedIn posted in dashboard ────────────
        mark_linkedin_posted(post_num)
        # ────────────────────────────────────────────────────────
    elif "message" in post_data:
        print(f"\nError from Buffer: {post_data['message']}")
        sys.exit(1)
    else:
        print(f"\nUnexpected response: {result}")
        sys.exit(1)


if __name__ == "__main__":
    main()
