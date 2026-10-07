"""Weekly Pinterest keyword tracker in a Google Sheet.

Setup:
  1. Google Cloud console -> create a service account -> download its JSON key.
  2. Save it as service_account.json next to this file (it is gitignored).
  3. Share the target spreadsheet with the service account's email address.
  4. Put the keywords you track in KEYWORDS.

Each run appends the top pins for every keyword with a date stamp, so you can
watch which pins, creators and sites hold the top of Pinterest search over time.

Actor: https://apify.com/pro100chok/pinterest-scraper-all-in-one?utm_source=github_pro100&utm_medium=readme&utm_campaign=pinterest-pins-boards-profiles-scraper-python
"""
import os
from datetime import datetime, timezone

import gspread
from apify_client import ApifyClient
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

SPREADSHEET = "Pinterest keyword tracker"
WORKSHEET = "top_pins"
KEYWORDS = ["capsule wardrobe", "meal prep ideas", "garden path ideas"]
PINS_PER_KEYWORD = 25
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/pinterest-scraper-all-in-one").call(run_input={
    "scrapeType": "search",
    "items": KEYWORDS,
    "searchScope": "pins",
    "maxResults": PINS_PER_KEYWORD,
})

header = ["date", "keyword", "position", "pin_id", "title", "media_type", "saves",
          "comments", "pinner", "pinner_followers", "domain", "link", "pin_url"]
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
positions: dict[str, int] = {}
rows = []
for p in client.dataset(run["defaultDatasetId"]).iterate_items():
    kw = p.get("input")  # the keyword this record came from
    positions[kw] = positions.get(kw, 0) + 1
    rows.append([
        today, kw, positions[kw], p.get("id"), (p.get("title") or "")[:150],
        p.get("media_type"), p.get("repin_count"), p.get("comment_count"),
        p.get("pinner_username"), p.get("pinner_followers"), p.get("domain"),
        p.get("link"), p.get("url"),
    ])

creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
sheet = gspread.authorize(creds).open(SPREADSHEET)
try:
    ws = sheet.worksheet(WORKSHEET)
except gspread.WorksheetNotFound:
    ws = sheet.add_worksheet(WORKSHEET, rows=20000, cols=len(header))
    ws.append_row(header)

ws.append_rows(rows, value_input_option="USER_ENTERED")
print(f"Appended {len(rows)} pins for {len(KEYWORDS)} keywords to {SPREADSHEET}/{WORKSHEET}")
