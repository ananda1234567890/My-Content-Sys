# HEVC Export Settings for Crisp Instagram Reels

**Date created:** 2026-06-04
**Source:** @artzenmedia — https://www.instagram.com/reel/DYMpZZtvHEJ/
**Format:** AI Infographic
**Platform:** LinkedIn
**Status:** Draft

## Post Text (copy-paste ready)

Your Instagram exports are getting compressed worse than they need to be.

The fix is not chasing the perfect bitrate number. It's choosing the codec Instagram actually processes better.
Here's the exact setup.

𝗦𝘁𝗲𝗽 𝟭: Set your format to HEVC (H.265)
In Premiere's export settings, open the Format dropdown and select H.265. Not H.264. HEVC compresses more efficiently at the same visual quality, which means Instagram's re-compression has significantly less to destroy.

𝗦𝘁𝗲𝗽 𝟮: Resolution and frame rate
Set resolution to 1080x1920 minimum for vertical. If your sequence allows it, export at 2K.
→ Frame rate: 24fps for cinematic, 30fps for standard
→ Do not export at 60fps unless the footage was shot at 60

𝗦𝘁𝗲𝗽 𝟯: Bitrate settings
Encoding: VBR, 1 Pass.
→ Target Bitrate: 17 to 30 Mbps for 24/30fps
→ Maximum Bitrate: 35 Mbps
Check Maximum Depth and Maximum Render Quality in the export panel.

𝗦𝘁𝗲𝗽 𝟰: Audio codec
Set to AAC. Do not use Linear PCM. There are documented upload issues with PCM audio on Instagram and AAC is what the platform expects.

𝗦𝘁𝗲𝗽 𝟱: File size before uploading
Keep the final file between 15 MB and 60 MB. Files larger than 60 MB can trigger more aggressive compression from Instagram's pipeline, which defeats the whole point.

HEVC gives Instagram's compression algorithm less to destroy.
You've been handing it H.264 and wondering why it comes out blurry.

Worth it.

## Image Notes

TBD — to be filled after post review approval.
