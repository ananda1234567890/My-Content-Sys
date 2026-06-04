# /setup-buffer

Sets up Buffer + Cloudinary integration so posts can be scheduled directly from Claude Code.

## What Claude Does

1. Ask for the three credentials (one at a time, clearly)
2. Write them to the root `.env` file
3. Test the Buffer connection — fetch the LinkedIn channel ID automatically
4. Confirm everything works

---

## Step 1: Ask for credentials

Say this to the user exactly:

> I need three things to set up Buffer scheduling. Paste them one at a time:
>
> **1. Buffer API token** — go to https://publish.buffer.com/settings/api and copy your token.

Wait for the token. Then ask:

> **2. Cloudinary API Key** — go to https://cloudinary.com/console → Settings → API Keys. Copy the API Key (the number).

Wait. Then ask:

> **3. Cloudinary API Secret** — same page, copy the API Secret (the long string next to your key).

---

## Step 2: Write to .env

Add these lines to the root `.env` file (create it if it doesn't exist):

```
BUFFER_TOKEN=<their token>
CLOUDINARY_CLOUD_NAME=duoq5xmdp
CLOUDINARY_API_KEY=<their key>
CLOUDINARY_API_SECRET=<their secret>
```

Do not add `BUFFER_LINKEDIN_CHANNEL_ID` yet — fetch it in the next step.

---

## Step 3: Find the LinkedIn channel ID

Run this Python snippet to get the org ID and then list channels:

```python
python3 -c "
import urllib.request, json
token = open('.env').read()
token = [l.split('=',1)[1].strip() for l in token.splitlines() if l.startswith('BUFFER_TOKEN=')][0]

def gql(q):
    req = urllib.request.Request('https://api.buffer.com', json.dumps({'query':q}).encode(), {'Content-Type':'application/json','Authorization':f'Bearer {token}'})
    return json.loads(urllib.request.urlopen(req).read())

org_id = gql('{ account { organizations { id } } }')['data']['account']['organizations'][0]['id']
channels = gql(f'{{ channels(input: {{ organizationId: \"{org_id}\" }}) {{ id name service }} }}')['data']['channels']
for c in channels:
    print(c['service'], c['id'], c['name'])
"
```

Find the line that says `linkedin`. Copy that ID and add it to `.env`:

```
BUFFER_LINKEDIN_CHANNEL_ID=<the id>
```

---

## Step 4: Test it

Run a dry-run to confirm everything is wired up:

```bash
python3 scripts/schedule-to-buffer.py posts/017-ai-transition-bridging --time "2026-06-11T09:00:00+05:30"
```

If it prints `✓ Scheduled successfully` — setup is complete. Delete the test post immediately after:

The post ID will be printed. Delete it with:

```python
python3 -c "
import urllib.request, json
token = [l.split('=',1)[1].strip() for l in open('.env').read().splitlines() if l.startswith('BUFFER_TOKEN=')][0]
post_id = input('Post ID to delete: ')
req = urllib.request.Request('https://api.buffer.com', json.dumps({'query': f'mutation {{ deletePost(input: {{ id: \"{post_id}\" }}) {{ ... on DeletePostSuccess {{ id }} }} }}'}).encode(), {'Content-Type':'application/json','Authorization':f'Bearer {token}'})
print(json.loads(urllib.request.urlopen(req).read()))
"
```

---

## Step 5: Confirm to the user

Once done, tell Ananda:

> Buffer is set up. To schedule a post, just say:
> **"Schedule post 018 for June 12th 5pm"**
>
> Claude will generate/upload any image or carousel automatically and schedule it to your LinkedIn.

---

## Troubleshooting

**"No LinkedIn channel connected"** — Buffer account doesn't have LinkedIn added. Go to https://publish.buffer.com → Channels → Add Channel → LinkedIn.

**Cloudinary upload fails** — double-check the API Key and Secret are copied exactly, no extra spaces.

**"BUFFER_TOKEN not set"** — `.env` file is missing or in the wrong folder. Must be in the root of the project (same level as CLAUDE.md).
