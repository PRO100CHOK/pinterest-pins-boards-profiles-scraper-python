"""Export a Pinterest board: its metadata, its sections and every pin on it.

`board` mode returns one board record followed by its pins (set
`includeBoardPins` to False for metadata only). `boardSections` lists the
board's sections with their pin counts.

Actor: https://apify.com/pro100chok/pinterest-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python
"""
import os

from apify_client import ApifyClient
from dotenv import load_dotenv

BOARD = "https://www.pinterest.com/ikeausa/kitchen-inspiration/"

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])
actor = client.actor("pro100chok/pinterest-scraper-all-in-one")

run = actor.call(run_input={"scrapeType": "boardSections", "items": [BOARD], "maxResults": 50})
sections = list(client.dataset(run["defaultDatasetId"]).iterate_items())
print(f"{len(sections)} sections")
for s in sections:
    print(f"  {s.get('pin_count') or 0:>5} pins  {s.get('title')}")

run = actor.call(run_input={
    "scrapeType": "board",
    "items": [BOARD],
    "includeBoardPins": True,
    "maxResults": 100,
})
records = list(client.dataset(run["defaultDatasetId"]).iterate_items())
board = next((r for r in records if r.get("dataType") == "board"), {})
pins = [r for r in records if r.get("dataType") == "pin"]

print(f"\nBoard: {board.get('name')} by @{board.get('owner_username')}")
print(f"  {board.get('pin_count')} pins, {board.get('follower_count')} followers, "
      f"{board.get('section_count')} sections")
print(f"  cover: {board.get('image_cover')}")
print(f"\nFetched {len(pins)} pins; top 5 by saves:")
for p in sorted(pins, key=lambda p: -(p.get("repin_count") or 0))[:5]:
    print(f"  {p.get('repin_count') or 0:>6,}  {(p.get('title') or '')[:60]}  {p.get('image')}")
