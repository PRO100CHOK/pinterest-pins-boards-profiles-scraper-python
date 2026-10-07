"""Pinterest niche audit — which sites, creators and formats win a keyword set.

Use case: a home-decor brand wants to know what actually gets saved on Pinterest
for its keywords before planning content. This script:

  1. searches Pinterest pins for several keywords,
  2. ranks the outbound domains that collect the most saves (repins) — i.e. which
     blogs and shops Pinterest traffic really flows to,
  3. measures how saves split between images, GIFs and videos,
  4. pulls full profiles for the most-saved creators (followers, pin and board
     counts, website) so you get an outreach / partnership list,
  5. writes everything to output.json and the creator list to output.csv.

No Pinterest login or API key is needed.

Run:
    pip install -r requirements.txt
    cp .env.example .env
    python main.py

Actor: https://apify.com/pro100chok/pinterest-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python
"""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

from apify_client import ApifyClient
from apify_client.errors import ApifyApiError
from dotenv import load_dotenv

ACTOR_ID = "pro100chok/pinterest-scraper-all-in-one"
KEYWORDS = ["japandi living room", "boho bedroom decor", "small balcony ideas"]
PINS_PER_KEYWORD = 150
TOP_CREATORS = 15
OUT_DIR = Path(__file__).parent


def run_actor(client: ApifyClient, run_input: dict, label: str) -> list[dict]:
    print(f"  -> {label}")
    try:
        run = client.actor(ACTOR_ID).call(run_input=run_input, timeout_secs=1800)
    except ApifyApiError as exc:
        sys.exit(f"{label} failed: {exc}")
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"     {len(items)} records")
    return items


def main() -> int:
    load_dotenv()
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        sys.exit("APIFY_API_TOKEN missing — copy .env.example to .env first.")
    client = ApifyClient(token)

    print("Step 1/2 — keyword search")
    pins = run_actor(client, {
        "scrapeType": "search",
        "items": KEYWORDS,
        "searchScope": "pins",
        "maxResults": PINS_PER_KEYWORD,
    }, f"{len(KEYWORDS)} keywords x {PINS_PER_KEYWORD} pins")
    pins = [p for p in pins if p.get("dataType") == "pin"]
    if not pins:
        sys.exit("No pins returned.")

    saves_by_domain: Counter = Counter()
    pins_by_domain: Counter = Counter()
    saves_by_media: Counter = Counter()
    count_by_media: Counter = Counter()
    creator_saves: dict[str, int] = defaultdict(int)
    creator_pins: Counter = Counter()

    for p in pins:
        saves = p.get("repin_count") or 0
        media = p.get("media_type") or "image"
        saves_by_media[media] += saves
        count_by_media[media] += 1
        if p.get("domain"):
            saves_by_domain[p["domain"]] += saves
            pins_by_domain[p["domain"]] += 1
        if p.get("pinner_username"):
            creator_saves[p["pinner_username"]] += saves
            creator_pins[p["pinner_username"]] += 1

    print("\nTop outbound domains by saves:")
    for domain, saves in saves_by_domain.most_common(10):
        print(f"  {saves:>9,} saves  {pins_by_domain[domain]:>4} pins  {domain}")

    print("\nFormat mix:")
    for media, n in count_by_media.most_common():
        print(f"  {media:<6} {n:>5} pins, avg {saves_by_media[media] / n:,.0f} saves per pin")

    top = sorted(creator_saves, key=creator_saves.get, reverse=True)[:TOP_CREATORS]
    print(f"\nStep 2/2 — profiles of the {len(top)} most-saved creators")
    profiles = run_actor(client, {
        "scrapeType": "profile",
        "items": [f"@{u}" for u in top],
    }, "profile mode") if top else []

    creators = []
    for prof in profiles:
        user = prof.get("username")
        creators.append({
            "username": user,
            "full_name": prof.get("full_name"),
            "follower_count": prof.get("follower_count"),
            "pin_count": prof.get("pin_count"),
            "board_count": prof.get("board_count"),
            "video_pin_count": prof.get("video_pin_count"),
            "is_verified_merchant": prof.get("is_verified_merchant"),
            "website": prof.get("website"),
            "pins_in_sample": creator_pins.get(user, 0),
            "saves_in_sample": creator_saves.get(user, 0),
            "url": prof.get("url"),
        })
    creators.sort(key=lambda c: -c["saves_in_sample"])

    (OUT_DIR / "output.json").write_text(json.dumps({
        "keywords": KEYWORDS,
        "domains": [{"domain": d, "saves": s, "pins": pins_by_domain[d]}
                    for d, s in saves_by_domain.most_common()],
        "formats": {m: {"pins": n, "saves": saves_by_media[m]} for m, n in count_by_media.items()},
        "creators": creators,
        "pins": pins,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    if creators:
        with (OUT_DIR / "output.csv").open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(creators[0].keys()))
            writer.writeheader()
            writer.writerows(creators)

    print(f"\n{'creator':<26}{'followers':>11}{'saves':>10}  website")
    for c in creators:
        print(f"{(c['username'] or '-'):<26}{c['follower_count'] or 0:>11,}"
              f"{c['saves_in_sample']:>10,}  {c['website'] or '-'}")
    print(f"\nSaved {len(pins)} pins and {len(creators)} creators to output.json / output.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
