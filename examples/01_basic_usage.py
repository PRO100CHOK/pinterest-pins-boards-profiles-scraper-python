"""Search Pinterest pins for a keyword — no login, no API key.

Actor: https://apify.com/pro100chok/pinterest-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python
"""
import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/pinterest-scraper-all-in-one").call(run_input={
    "scrapeType": "search",
    "items": ["home office ideas"],
    "searchScope": "pins",
    "maxResults": 25,
})

for pin in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(f"{pin.get('repin_count') or 0:>7,} saves  {pin.get('media_type') or '?':<5} "
          f"{(pin.get('title') or '(untitled)')[:60]}")
    print(f"    {pin.get('url')}  ->  {pin.get('link') or 'no outbound link'}")
