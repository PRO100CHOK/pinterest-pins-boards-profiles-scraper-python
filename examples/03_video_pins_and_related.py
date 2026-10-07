"""Find Pinterest video pins for a keyword, then expand the best one with related pins.

Video pins come back with a direct MP4 URL (`video_url`), an HLS stream
(`video_hls_url`), duration and thumbnail. `relatedPins` returns the "more like
this" feed for a pin — a cheap way to widen a content-idea list.

Actor: https://apify.com/pro100chok/pinterest-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python
"""
import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])
actor = client.actor("pro100chok/pinterest-scraper-all-in-one")

run = actor.call(run_input={
    "scrapeType": "search",
    "items": ["easy dinner recipes"],
    "searchScope": "videos",
    "maxResults": 40,
})
videos = [p for p in client.dataset(run["defaultDatasetId"]).iterate_items() if p.get("is_video")]
print(f"{len(videos)} video pins")
for v in videos[:10]:
    secs = (v.get("video_duration_ms") or 0) / 1000
    print(f"  {v.get('repin_count') or 0:>6,} saves  {secs:>5.0f}s  {(v.get('title') or '')[:50]}")
    print(f"      mp4: {v.get('video_url') or '-'}")

if videos:
    best = max(videos, key=lambda v: v.get("repin_count") or 0)
    run = actor.call(run_input={"scrapeType": "relatedPins", "items": [best["url"]], "maxResults": 30})
    print(f"\nRelated to {best['url']}:")
    for p in client.dataset(run["defaultDatasetId"]).iterate_items():
        print(f"  {p.get('media_type') or '?':<5} {(p.get('title') or '')[:60]}  {p.get('domain') or ''}")
