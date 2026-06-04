# Buffer Setup Guide

How to connect Buffer to this content system so posts can be scheduled directly from Claude Code.

---

## What This Does

Instead of manually copying post text and uploading to LinkedIn, this integration lets Claude schedule posts directly to Buffer, which then publishes them at the right time.

**Supported:** LinkedIn text posts (with the post text from `post.md`)
**Not yet supported:** Carousel PDFs and images (Buffer API requires a public URL — see section below)

---

## Step 1: Create a Buffer Account

Go to [buffer.com](https://buffer.com) and sign up (free tier works for getting started).

---

## Step 2: Connect Your LinkedIn Channel

Inside Buffer → Channels → Add Channel → LinkedIn.

Authorize Buffer to post on your behalf. You'll see your LinkedIn profile appear in the channel list.

---

## Step 3: Get Your API Token

Go to: [publish.buffer.com/settings/api](https://publish.buffer.com/settings/api)

Copy the token. It looks like: `u1sWdvygehW2XK5cZHU8REKr-yJ-0XS_PcYYgMmtjni`

---

## Step 4: Add to .env

In the root `.env` file, add:

```
BUFFER_TOKEN=your_token_here
BUFFER_LINKEDIN_CHANNEL_ID=your_channel_id_here
```

To find your LinkedIn channel ID, run this once:

```bash
python3 -c "
import urllib.request, json
token = 'your_token_here'
res = urllib.request.urlopen(urllib.request.Request(
    'https://api.buffer.com',
    data=json.dumps({'query': '{ account { organizations { id } } }'}).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
))
data = json.loads(res.read())
org_id = data['data']['account']['organizations'][0]['id']
res2 = urllib.request.urlopen(urllib.request.Request(
    'https://api.buffer.com',
    data=json.dumps({'query': f'{{ channels(input: {{ organizationId: \"{org_id}\" }}) {{ id name service }} }}'}).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
))
channels = json.loads(res2.read())['data']['channels']
for c in channels:
    print(c['service'], c['id'], c['name'])
"
```

Look for the line that says `linkedin` — copy that ID.

---

## Step 5: Schedule a Post

Tell Claude: **"schedule post 017 for June 9th 9am"**

Or run directly:

```bash
# Schedule at a specific time (IST)
python3 scripts/schedule-to-buffer.py posts/017-ai-transition-bridging --time "2026-06-09T09:00:00+05:30"

# Add to Buffer queue (next available slot)
python3 scripts/schedule-to-buffer.py posts/017-ai-transition-bridging --queue

# Default: 9am IST tomorrow
python3 scripts/schedule-to-buffer.py posts/017-ai-transition-bridging
```

---

## Mistakes We Hit (and what the fix was)

### Mistake 1: Wrong delete mutation fields

First attempt to delete a test post used `postId` and `deletedPostId` — both wrong.

```
"Field 'DeletePostInput.id' of required type 'PostId!' was not provided"
"Field 'postId' is not defined by type 'DeletePostInput'"
```

**Fix:** The field is `id`, not `postId`. The response is a union type, needs `... on DeletePostSuccess { id }`.

```graphql
mutation {
  deletePost(input: { id: "your_post_id" }) {
    ... on DeletePostSuccess { id }
    ... on MutationError { message }
  }
}
```

### Mistake 2: Garbled Unicode bold characters

The post text uses Unicode mathematical bold characters for step headers (𝗦𝘁𝗲𝗽 𝟭). When manually typing Unicode escape sequences in Python, they came out wrong — "Step" became "𝗦𝗹𝗲𝗽" and step numbers shifted by 2.

**Fix:** Always read post text directly from the `post.md` file using Python's file IO. Never manually type Unicode escape sequences for user content.

```python
# Wrong: hardcoding with escape sequences
text = "\U0001d5e6\U0001d5f9..."

# Right: read from file
text = Path("posts/017-ai-transition-bridging/post.md").read_text(encoding="utf-8")
```

### Mistake 3: `dueAt` must include timezone offset

Passing a bare UTC time like `2026-06-09T09:00:00Z` gives 9am UTC, not 9am IST. For Kolkata (IST = UTC+5:30), use `+05:30`.

**Fix:** Always build `dueAt` with the timezone offset:
```
2026-06-09T09:00:00+05:30  ← correct for 9am IST
2026-06-09T09:00:00Z       ← this is 2:30pm IST — wrong
```

---

## Limitations: Images and Carousels

Buffer's API requires a **publicly accessible URL** for images — it can't accept file uploads directly.

For carousels (PDF format), Buffer does not support PDF scheduling via API.

**Options:**
1. **Text-only scheduling** — schedule the post text now, manually add the image/carousel when it goes live in Buffer's web dashboard
2. **Cloudinary upload** — upload the image to Cloudinary first, then pass the Cloudinary URL to Buffer. Ananda already has a Cloudinary account (`duoq5xmdp`). This requires adding `CLOUDINARY_API_KEY` and `CLOUDINARY_API_SECRET` to `.env`.

This is the next thing to build.

---

## Rate Limits (Buffer free tier)

| Window | Limit |
|--------|-------|
| 15 minutes | 100 requests |
| 24 hours | 100 requests |
| 30 days | 3,000 requests |

For daily scheduling of a few posts, the free tier is more than enough.

---

## API Quick Reference

**Endpoint:** `https://api.buffer.com` (GraphQL, POST)
**Auth:** `Authorization: Bearer YOUR_TOKEN`

**Get channels:**
```graphql
{ channels(input: { organizationId: "ORG_ID" }) { id name service } }
```

**Schedule a post:**
```graphql
mutation {
  createPost(input: {
    channelId: "CHANNEL_ID"
    schedulingType: automatic
    mode: customScheduled
    dueAt: "2026-06-09T09:00:00+05:30"
    text: "your post text"
  }) {
    ... on PostActionSuccess { post { id dueAt status } }
    ... on MutationError { message }
  }
}
```

**Delete a post:**
```graphql
mutation {
  deletePost(input: { id: "POST_ID" }) {
    ... on DeletePostSuccess { id }
    ... on MutationError { message }
  }
}
```
